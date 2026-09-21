import time
import main

def time_generate(n, r, repeat=3):
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        main.generate_all(n, r)
        dt = time.perf_counter() - t0
        best = min(best, dt)
    return best


if __name__ == '__main__':
    print('A. 固定 r=1000，随题目数量 n 变化')
    for n in (100, 500, 1000, 2000, 5000, 10000, 20000):
        dt = time_generate(n, 1000)
        print(f"n={n:>6}  耗时 {dt:.4f} s  每题 {dt / n * 1000:.4f} ms")
    print('B. 固定 n=10000，随数值范围 r 变化')
    for r in (10, 20, 50, 100, 500, 1000):
        dt = time_generate(10000, r)
        print(f"r={r:>5}  耗时 {dt:.4f} s")