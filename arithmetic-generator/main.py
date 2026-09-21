import argparse   # 命令行参数
import random     # 随机生成题目
import sys        # 程序退出码
from fractions import Fraction   # 精确分数运算

# 四则运算符与优先级表
OPS = ['+', '−', '×', '÷']
PREC = {'+': 1, '−': 1, '×': 2, '÷': 2}

def format_number(x: Fraction) -> str:
    """把分数转成展示格式：自然数 5，真分数 3/5，带分数 2'3/8。"""
    if x.denominator == 1:
        return str(x.numerator)
    sign = '-' if x < 0 else ''
    a, b = abs(x.numerator), x.denominator
    whole, rem = divmod(a, b)
    if whole == 0:
        return f"{sign}{a}/{b}"
    return f"{sign}{whole}'{rem}/{b}"

def parse_number(s: str) -> Fraction:
    """解析自然数 / 真分数 / 带分数，如 5、3/5、2'3/8。"""
    s = s.strip()
    if "'" in s:
        whole, frac = s.split("'", 1)
        num, den = frac.split('/', 1)
        return Fraction(int(whole)) + Fraction(int(num), int(den))
    if '/' in s:
        num, den = s.split('/', 1)
        return Fraction(int(num), int(den))
    return Fraction(int(s))


def tokenize(text: str):
    """把表达式字符串切成记号流：数字记号为 ('num', Fraction)，其余为运算符/括号字符。"""
    tokens = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
        elif c in '+-−×÷()=':
            tokens.append('−' if c == '-' else c)   # 统一减号字符为 −
            i += 1
        elif c.isdigit():
            j = i
            while j < n and text[j].isdigit():
                j += 1
            if j < n and text[j] == "'":                # 带分数 2'3/8
                j2 = j + 1
                while j2 < n and text[j2].isdigit():
                    j2 += 1
                if j2 >= n or text[j2] != '/':
                    raise ValueError(f"无法解析带分数: {text[i:]}")
                j3 = j2 + 1
                while j3 < n and text[j3].isdigit():
                    j3 += 1
                v = Fraction(int(text[i:j])) + Fraction(
                    int(text[j + 1:j2]), int(text[j2 + 1:j3]))
                tokens.append(('num', v))
                i = j3
            elif j < n and text[j] == '/':              # 分数 3/8
                j2 = j + 1
                while j2 < n and text[j2].isdigit():
                    j2 += 1
                tokens.append(('num', Fraction(int(text[i:j]), int(text[j + 1:j2]))))
                i = j2
            else:                                       # 自然数 5
                tokens.append(('num', Fraction(int(text[i:j]))))
                i = j
        else:
            raise ValueError(f"无法识别的字符: {c!r}")
    return tokens


class Parser:
    """递归下降解析器。语法：
       expr   := term (('+'|'−') term)*
       term   := factor (('×'|'÷') factor)*
       factor := number | '(' expr ')'
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def next(self):
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def parse(self):
        node = self.parse_expr()
        if self.pos != len(self.tokens):
            raise ValueError(f"表达式末尾有多余内容: {self.tokens[self.pos:]}")
        return node

    def parse_expr(self):
        node = self.parse_term()
        while self.peek() in ('+', '−'):
            op = self.next()
            node = ('bin', op, node, self.parse_term())
        return node

    def parse_term(self):
        node = self.parse_factor()
        while self.peek() in ('×', '÷'):
            op = self.next()
            node = ('bin', op, node, self.parse_factor())
        return node

    def parse_factor(self):
        t = self.peek()
        if isinstance(t, tuple) and t[0] == 'num':
            self.next()
            return ('num', t[1])
        if t == '(':
            self.next()
            node = self.parse_expr()
            if self.peek() != ')':
                raise ValueError("缺少右括号")
            self.next()
            return node
        raise ValueError(f"非法的表达式记号: {t!r}")


def eval_node(node) -> Fraction:
    """对表达式树求值，返回精确的 Fraction。"""
    if node[0] == 'num':
        return node[1]
    _, op, l, r = node
    a, b = eval_node(l), eval_node(r)
    if op == '+':
        return a + b
    if op == '−':
        return a - b
    if op == '×':
        return a * b
    if op == '÷':
        if b == 0:
            raise ValueError("除数为 0")
        return a / b
    raise ValueError(f"未知运算符: {op!r}")


def parse_expr(text: str):
    """解析一行题目文本（可带结尾的 = 号）→ AST。"""
    text = text.replace('=', '').strip()
    return Parser(tokenize(text)).parse()

def canonical(node) -> str:
    """返回表达式的规范串，用于 O(1) 判重。"""
    if node[0] == 'num':
        v = node[1]
        return f"n{v.numerator}/{v.denominator}" if v.denominator != 1 else f"n{v.numerator}"
    _, op, l, r = node
    cl, cr = canonical(l), canonical(r)
    if op in ('+', '×'):
        return f"{op}({min(cl, cr)},{max(cl, cr)})"   # 交换律：子节点排序
    return f"{op}({cl},{cr})"                          # 减法/除法保持顺序

def render(node) -> str:
    """按运算符优先级与结合性输出题目文本，必要时加括号。"""
    if node[0] == 'num':
        return format_number(node[1])
    _, op, l, r = node
    return f"{render_child(l, op, 'left')} {op} {render_child(r, op, 'right')}"


def render_child(node, parent_op, side) -> str:
    """决定子表达式是否需要括号。"""
    s = render(node)
    if node[0] == 'num':
        return s
    child_op = node[1]
    if PREC[child_op] > PREC[parent_op]:
        return s            # 保持不变
    if PREC[child_op] < PREC[parent_op]:
        return f"({s})"     # 加括号
    if side == 'left':
        return s            # 左结合
    return f"({s})"         # 右侧同级加括号保留结构

def random_leaf(rng: random.Random, r: int) -> Fraction:
    """生成一个 [0, r) 内的自然数或真分数（真分数分母 < r）。"""
    if r >= 3 and rng.random() < 0.35:
        den = rng.randint(2, r - 1)
        num = rng.randint(1, den - 1)
        return Fraction(num, den)
    return Fraction(rng.randint(0, r - 1))


def gen_expression(rng, r, op_count):
    """递归生成一棵含 op_count 个运算符的表达式树。

    返回 (node, value)；约束不满足时返回 None（由上层重试）。
    """
    if op_count == 0:
        v = random_leaf(rng, r)
        return ('num', v), v
    op = rng.choice(OPS)
    lo = rng.randint(0, op_count - 1)          # 左右子树分配运算符个数
    ro = op_count - 1 - lo
    got = gen_expression(rng, r, lo)
    if got is None:
        return None
    lnode, lv = got
    got = gen_expression(rng, r, ro)
    if got is None:
        return None
    rnode, rv = got
    if op == '−' and lv < rv:                  # 约束1：减法不产生负数
        return None
    if op == '÷':                              # 约束2：除法结果必须是真分数
        if lv <= 0 or lv >= rv:
            return None
        v = lv / rv
    elif op == '+':
        v = lv + rv
    elif op == '−':
        v = lv - rv
    else:
        v = lv * rv
    return ('bin', op, lnode, rnode), v


def generate_problem(rng, r, max_ops=3):
    """生成一道运算符个数为 1~max_ops 的题目，返回表达式树。"""
    op_count = rng.randint(1, max_ops)
    for _ in range(200):
        got = gen_expression(rng, r, op_count)
        if got is not None:
            return got[0]
    return None


def generate_all(n, r, max_ops=3):
    """生成 n 道互不重复（一次运行内）的题目，返回表达式树列表。"""
    if r < 1:
        raise ValueError("-r 必须是大于等于 1 的自然数")
    if n < 1:
        raise ValueError("-n 必须是大于等于 1 的自然数")
    rng = random.Random()
    seen, problems = set(), []
    attempts, max_attempts = 0, max(50000, n * 200)
    while len(problems) < n and attempts < max_attempts:
        attempts += 1
        node = generate_problem(rng, r, max_ops)
        if node is None:
            continue
        key = canonical(node)                  # 规范串判重，O(1)
        if key in seen:
            continue
        seen.add(key)
        problems.append(node)
    if len(problems) < n:
        raise RuntimeError(
            f"无法在 -r {r} 范围内生成 {n} 道互不重复的题目"
            f"（仅生成 {len(problems)} 道）。请增大 -r 或减小 -n。")
    return problems

def grade(ex_file: str, ans_file: str):
    """读取题目文件与答案文件，判定对错并写入Grade.txt。"""
    with open(ex_file, encoding='utf-8') as f:
        exercises = [ln.strip() for ln in f if ln.strip()]
    with open(ans_file, encoding='utf-8') as f:
        answers = [ln.strip() for ln in f if ln.strip()]
    if len(exercises) != len(answers):
        raise ValueError(
            f"题目数量 {len(exercises)} 与答案数量 {len(answers)} 不一致")
    correct, wrong = [], []
    for i, (e, a) in enumerate(zip(exercises, answers), 1):
        try:
            actual = eval_node(parse_expr(e))      # 重算标准答案
            expected = parse_number(a)             # 解析学生答案
            (correct if actual == expected else wrong).append(i)
        except Exception:
            wrong.append(i)                        # 解析/求值失败按错误计
    with open('Grade.txt', 'w', encoding='utf-8') as f:
        f.write(f"Correct: {len(correct)} ({', '.join(map(str, correct))})\n")
        f.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")
    print(f"Correct: {len(correct)} ({', '.join(map(str, correct))})")
    print(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})")

def main(argv=None):
    ap = argparse.ArgumentParser(
        prog='Myapp',
        description='小学四则运算题目生成与批改程序',
        epilog='示例：\n'
               '  Myapp -n 10 -r 10        生成10道10以内题目\n'
               '  Myapp -e Ex.txt -a An.txt  批改并输出 Grade.txt')
    ap.add_argument('-n', type=int, metavar='N', help='生成题目的个数（默认 10）')
    ap.add_argument('-r', type=int, metavar='R',
                    help='题目中数值的范围：0 到 R-1（不含 R），生成模式必填')
    ap.add_argument('-e', metavar='exercisefile.txt', help='批改模式：题目文件')
    ap.add_argument('-a', metavar='answerfile.txt', help='批改模式：答案文件')
    args = ap.parse_args(argv)

    # ---- 批改模式 ----
    if args.e is not None or args.a is not None:
        if args.e is None or args.a is None:
            print('错误：批改模式必须同时使用 -e 与 -a。', file=sys.stderr)
            ap.print_help(file=sys.stderr)
            return 2
        try:
            grade(args.e, args.a)
        except (OSError, ValueError) as exc:
            print(f'错误：{exc}', file=sys.stderr)
            return 1
        return 0

    # ---- 生成模式：-r 必须给定，否则报错并给出帮助信息 ----
    if args.r is None:
        print('错误：生成模式必须指定 -r 参数（数值范围）。', file=sys.stderr)
        ap.print_help(file=sys.stderr)
        return 2

    n = args.n if args.n is not None else 10
    try:
        problems = generate_all(n, args.r)
    except (ValueError, RuntimeError) as exc:
        print(f'错误：{exc}', file=sys.stderr)
        return 1

    # 题目与答案写入当前目录
    with open('Exercises.txt', 'w', encoding='utf-8') as f:
        for node in problems:
            f.write(f"{render(node)} = \n")
    with open('Answers.txt', 'w', encoding='utf-8') as f:
        for node in problems:
            f.write(f"{format_number(eval_node(node))}\n")
    print(f'已生成 {len(problems)} 道题目：Exercises.txt / Answers.txt')
    return 0


if __name__ == '__main__':
    sys.exit(main())