"""论文查重程序入口。
用法: python main.py <论文原文路径> <抄袭版论文路径> <答案文件路径>
"""

import sys

from checker.exceptions import PaperCheckerError, FileReadError, FileWriteError, UsageError
from checker.preprocess import tokenize
from checker.similarity import cosine_similarity
# 常见中文文本编码，按优先级依次尝试解码
_ENCODINGS = ("utf-8-sig", "utf-8", "gbk")

def parse_args(argv):
    """校验命令行参数，返回原文路径, 抄袭版路径, 答案路径。"""
    if len(argv) != 3:
        raise UsageError(
            f"需要 3 个参数(原文 抄袭版 答案文件)，实际收到 {len(argv)} 个"
        )
    return argv[0], argv[1], argv[2]

def read_text(path):
    """读取文本文件，自动识别常见中文编码，失败时抛出FileReadError。"""
    try:
        with open(path, "rb") as file:
            raw = file.read()
    except OSError as exc:
        raise FileReadError(f"无法读取文件: {path}") from exc
    for encoding in _ENCODINGS:
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise FileReadError(f"无法识别的文件编码: {path}")

def write_result(path, rate):
    """把重复率写入答案文件（保留两位小数），失败时抛出FileWriteError。"""
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.write(f"{rate:.2f}")
    except OSError as exc:
        raise FileWriteError(f"无法写入答案文件: {path}") from exc

def main(argv=None):
    """程序主流程，返回进程退出码（0为成功，1为失败）。"""
    args = list(sys.argv[1:]) if argv is None else list(argv)
    try:
        orig_path, plag_path, ans_path = parse_args(args)
        orig_words = tokenize(read_text(orig_path))
        plag_words = tokenize(read_text(plag_path))
        rate = cosine_similarity(orig_words, plag_words)
        write_result(ans_path, rate)
        print(f"重复率: {rate:.2f}")
        return 0
    except PaperCheckerError as exc:
        print(f"错误: {exc}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
