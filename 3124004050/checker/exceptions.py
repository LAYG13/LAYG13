#自定义异常模块：统一异常层次，方便入口统一捕获。

class PaperCheckerError(Exception):
    """论文查重程序的基础异常，所有自定义异常的父类。"""

class UsageError(PaperCheckerError):
    """命令行参数错误：参数个数不等于3时抛出。"""

class FileReadError(PaperCheckerError):
    """输入文件读取失败：文件不存在、无权限或编码无法识别。"""

class FileWriteError(PaperCheckerError):
    """答案文件写入失败：输出目录不存在或没有写入权限。"""
