#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试套件：覆盖需求 1~8（生成、约束、判重、格式、一万道、批改）。
运行方式：python test_main.py -v
"""

import os
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import main

PROJ = os.path.dirname(os.path.abspath(__file__))
MAIN = os.path.join(PROJ, 'main.py')


def iter_nodes(node):
    """yield 所有子树节点。"""
    yield node
    if node[0] == 'bin':
        yield from iter_nodes(node[2])
        yield from iter_nodes(node[3])


def subtree_values(node):
    return [main.eval_node(n) for n in iter_nodes(node)]


def check_generated(problems, r):
    """全面校验一批生成结果：范围、约束、运算符个数。"""
    for node in problems:
        ops = sum(1 for n in iter_nodes(node) if n[0] == 'bin')
        assert 1 <= ops <= 3, f"运算符个数越界: {ops}"
        for leaf in (n for n in iter_nodes(node) if n[0] == 'num'):
            v = leaf[1]
            if v.denominator == 1:
                assert 0 <= v.numerator < r, f"自然数越界: {v}"
            else:
                assert 0 < v < 1 and v.denominator < r, f"真分数越界: {v}"
        assert all(v >= 0 for v in subtree_values(node)), "存在负的中间结果"
        for n in iter_nodes(node):
            if n[0] == 'bin' and n[1] == '÷':
                lv, rv = main.eval_node(n[2]), main.eval_node(n[3])
                assert 0 < lv < rv, f"除法结果不是真分数: {lv}/{rv}"


class TestNumberFormat(unittest.TestCase):
    def test_format(self):     #分数格式化测试
        self.assertEqual(main.format_number(Fraction(5)), '5')
        self.assertEqual(main.format_number(Fraction(3, 5)), '3/5')
        self.assertEqual(main.format_number(Fraction(11, 8)), "1'3/8")
        self.assertEqual(main.format_number(Fraction(7, 24)), '7/24')

    def test_parse(self):     #字符串解析测试
        self.assertEqual(main.parse_number('5'), Fraction(5))
        self.assertEqual(main.parse_number('3/5'), Fraction(3, 5))
        self.assertEqual(main.parse_number("2'3/8"), Fraction(19, 8))


class TestFractionArithmetic(unittest.TestCase):
    def test_example(self):     #基础算术功能测试
        node = main.parse_expr('1/6 + 1/8')
        self.assertEqual(main.eval_node(node), Fraction(7, 24))
        self.assertEqual(main.format_number(main.eval_node(node)), '7/24')


class TestCanonical(unittest.TestCase):     #判重测试
    def _canon(self, text):     #返回规范串
        return main.canonical(main.parse_expr(text))

    def test_commutative_duplicate(self):     #测试简单交换律
        self.assertEqual(self._canon('23 + 45'), self._canon('45 + 23'))
        self.assertEqual(self._canon('6 × 8'), self._canon('8 × 6'))

    def test_nested_duplicate(self):     #测试嵌套交换律
        self.assertEqual(self._canon('3 + (2 + 1)'), self._canon('1 + 2 + 3'))

    def test_not_duplicate(self):     #测试非等价表达式
        self.assertNotEqual(self._canon('1 + 2 + 3'), self._canon('3 + 2 + 1'))


class TestRendering(unittest.TestCase):    #括号生成与往返测试
    def test_parens(self):     #测试括号必要性
        self.assertEqual(main.render(main.parse_expr('3 + (2 + 1)')), '3 + (2 + 1)')
        self.assertEqual(main.render(main.parse_expr('1 + 2 + 3')), '1 + 2 + 3')
        self.assertEqual(main.render(main.parse_expr('(1 + 2) × 3')), '(1 + 2) × 3')

    def test_roundtrip(self):     #往返测试
        samples = ['3 + (2 + 1)', '1 − 2 − 3', '1 − (2 − 3)',
                   '(1 + 2) × 3', '1 ÷ (2 × 3)', '2/3 × (1 + 1/2)']
        for s in samples:
            v1 = main.eval_node(main.parse_expr(s))
            rendered = main.render(main.parse_expr(s))
            v2 = main.eval_node(main.parse_expr(rendered))
            self.assertEqual(v1, v2, f"roundtrip 失败: {s} -> {rendered}")


class TestGeneration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):     #初始化
        cls.rng = __import__('random').Random(2024)
        cls.problems = main.generate_all(200, 10, max_ops=3)

    def test_count(self):     #测试题目数量
        self.assertEqual(len(self.problems), 200)

    def test_constraints(self):     #测试约束条件
        check_generated(self.problems, 10)

    def test_no_duplicate(self):     #测试判重
        keys = [main.canonical(p) for p in self.problems]
        self.assertEqual(len(keys), len(set(keys)), "存在重复题目")

    def test_answer_consistency(self):     #测试渲染与求值的一致性
        for node in self.problems:
            rendered = main.render(node)
            self.assertEqual(main.eval_node(main.parse_expr(rendered)),
                             main.eval_node(node))


class TestCLIGenerate(unittest.TestCase):
    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, MAIN, *args],
                              capture_output=True, text=True, encoding='utf-8', cwd=cwd)

    def test_r_required(self):     #测试-r参数
        r = self.run_cli('-n', '10')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('错误', r.stderr)
        self.assertIn('-r', r.stderr)

    def test_generate_10(self):     #测试生成少量题目的基本功能是否正常
        with tempfile.TemporaryDirectory() as td:
            r = self.run_cli('-n', '10', '-r', '10', cwd=td)
            self.assertEqual(r.returncode, 0)
            ex = open(os.path.join(td, 'Exercises.txt'), encoding='utf-8').read().splitlines()
            an = open(os.path.join(td, 'Answers.txt'), encoding='utf-8').read().splitlines()
            self.assertEqual(len(ex), 10)
            self.assertEqual(len(an), 10)

    def test_10000(self):     #测试生成大量题目的基本功能是否正常
        with tempfile.TemporaryDirectory() as td:
            r = self.run_cli('-n', '10000', '-r', '100', cwd=td)
            self.assertEqual(r.returncode, 0)
            ex = open(os.path.join(td, 'Exercises.txt'), encoding='utf-8').read().splitlines()
            an = open(os.path.join(td, 'Answers.txt'), encoding='utf-8').read().splitlines()
            self.assertEqual(len(ex), 10000)
            self.assertEqual(len(an), 10000)
            nodes = [main.parse_expr(line) for line in ex]
            check_generated(nodes, 100)
            keys = [main.canonical(n) for n in nodes]
            self.assertEqual(len(set(keys)), 10000)

    def test_r1_small(self):     #测试边界情况
        with tempfile.TemporaryDirectory() as td:
            r = self.run_cli('-n', '1', '-r', '1', cwd=td)
            self.assertEqual(r.returncode, 0)

    def test_r1_overflow_graceful(self):     #测试当请求的题目数量远超可能组合数时的错误处理机制
        with tempfile.TemporaryDirectory() as td:
            r = self.run_cli('-n', '10000', '-r', '1', cwd=td)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('无法', r.stderr)


class TestCLIGrade(unittest.TestCase):     #测试批改功能
    def run_cli(self, *args, cwd=None):
        return subprocess.run([sys.executable, MAIN, *args],
                              capture_output=True, text=True, encoding='utf-8', cwd=cwd)

    def _write(self, td, name, lines):
        p = os.path.join(td, name)
        with open(p, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines) + '\n')
        return p

    def test_grade_mixed(self):     #混合对错场景测试
        with tempfile.TemporaryDirectory() as td:
            ex = self._write(td, 'Ex.txt', [
                '1 + 2 = ', '3/5 + 1/5 = ', '2 × 3 = ',
                '1 − 1/2 = ', '5 + 3 = ', '1/6 + 1/8 = '])
            ans = self._write(td, 'An.txt', [
                '3', '4/5', '6', '1/3', '8', '7/24'])
            r = self.run_cli('-e', ex, '-a', ans, cwd=td)
            self.assertEqual(r.returncode, 0)
            grade = open(os.path.join(td, 'Grade.txt'), encoding='utf-8').read()
            self.assertIn('Correct: 5 (1, 2, 3, 5, 6)', grade)
            self.assertIn('Wrong: 1 (4)', grade)

    def test_grade_all_correct(self):     #全对场景测试
        with tempfile.TemporaryDirectory() as td:
            ex = self._write(td, 'Ex.txt', ['1 + 2 = ', '3/5 + 1/5 = '])
            ans = self._write(td, 'An.txt', ['3', '4/5'])
            r = self.run_cli('-e', ex, '-a', ans, cwd=td)
            self.assertEqual(r.returncode, 0)
            grade = open(os.path.join(td, 'Grade.txt'), encoding='utf-8').read()
            self.assertIn('Correct: 2 (1, 2)', grade)
            self.assertIn('Wrong: 0 ()', grade)

    def test_grade_mixed_number_answer(self):     #带分数答案识别测试
        with tempfile.TemporaryDirectory() as td:
            ex = self._write(td, 'Ex.txt', ['3/4 + 5/8 = '])
            ans = self._write(td, 'An.txt', ["1'3/8"])
            r = self.run_cli('-e', ex, '-a', ans, cwd=td)
            self.assertEqual(r.returncode, 0)
            grade = open(os.path.join(td, 'Grade.txt'), encoding='utf-8').read()
            self.assertIn('Correct: 1 (1)', grade)

    def test_e_without_a(self):     #测试不提供-a的情况
        r = self.run_cli('-e', 'Ex.txt')
        self.assertNotEqual(r.returncode, 0)
        self.assertIn('错误', r.stderr)

    def test_line_count_mismatch(self):     #测试练习题文件和答案文件的行数不匹配时程序是否能正确报错
        with tempfile.TemporaryDirectory() as td:
            ex = self._write(td, 'Ex.txt', ['1 + 2 = ', '3 + 4 = '])
            ans = self._write(td, 'An.txt', ['3'])
            r = self.run_cli('-e', ex, '-a', ans, cwd=td)
            self.assertNotEqual(r.returncode, 0)
            self.assertIn('不一致', r.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=2)