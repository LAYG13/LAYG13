import time
import random
import main

def naive_generate(n, r):
    """初版：生成树后，用渲染文本在列表里逐个比对去重（O(n²)）。"""
    rendered = []
    rng = random.Random()
    while len(rendered) < n:
        node = main.generate_problem(rng, r)
        if node is None:
            continue
        text = main.render(node)
        if text in rendered:      # 判重：每次 O(n)，总共 O(n²)
            continue
        rendered.append(text)
    return rendered


def optimized_generate(n, r):
    """优化版：main.generate_all 内部用 canonical 集合 O(1) 判重。"""
    return main.generate_all(n, r)


if __name__ == '__main__':
    print(f"{'n':>6}  {'初版':>8}  {'优化版':>8}  {'提速':>8}")
    for n in (200, 500, 1000, 2000, 5000, 10000, 20000):
        t0 = time.perf_counter()
        naive_generate(n, 100)
        t_naive = time.perf_counter() - t0

        t0 = time.perf_counter()
        optimized_generate(n, 100)
        t_opt = time.perf_counter() - t0

        print(f"{n:>6}  {t_naive:>9.3f}s  {t_opt:>9.3f}s  {t_naive/t_opt:>7.1f}x")
