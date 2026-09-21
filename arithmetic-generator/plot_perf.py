import time
import matplotlib.pyplot as plt
import main

def time_generate(n, r, repeat=3):
    """生成 n 道题，跑 repeat 次取最快，返回耗时（秒）。"""
    best = float('inf')
    for _ in range(repeat):
        t0 = time.perf_counter()
        main.generate_all(n, r)
        best = min(best, time.perf_counter() - t0)
    return best


if __name__ == '__main__':
    plt.rcParams['font.sans-serif'] = ['SimHei']   # Windows 自带黑体，解决中文乱码
    plt.rcParams['axes.unicode_minus'] = False

    #A组：固定 r=1000，看耗时随题目数量 n 怎么变
    ns = [100, 500, 1000, 2000, 5000, 10000, 20000]
    times_n = [time_generate(n, 1000) for n in ns]

    #B组：固定 n=10000，看耗时随数值范围 r 怎么变
    rs = [10, 20, 50, 100, 500, 1000]
    times_r = [time_generate(10000, r) for r in rs]

    # 打印数据表
    print('A. 固定 r=1000：')
    for n, t in zip(ns, times_n):
        print(f'  n={n:>6}  耗时 {t:.4f} s')
    print('B. 固定 n=10000：')
    for r, t in zip(rs, times_r):
        print(f'  r={r:>5}  耗时 {t:.4f} s')

    # 画两张子图并排
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    ax1.plot(ns, times_n, 'o-', color='#1f77b4')
    ax1.set_xlabel('题目数量 n')
    ax1.set_ylabel('耗时（秒）')
    ax1.set_title('固定 r=1000：耗时随 n 变化')
    ax1.grid(True, alpha=0.3)

    ax2.plot(rs, times_r, 's-', color='#d62728')
    ax2.set_xlabel('数值范围 r')
    ax2.set_ylabel('耗时（秒）')
    ax2.set_title('固定 n=10000：耗时随 r 变化')
    ax2.grid(True, alpha=0.3)

    fig.suptitle('四则运算题目生成器性能分析')
    fig.tight_layout()
    fig.savefig('perf_chart.png', dpi=150)
    print('已保存 perf_chart.png')
