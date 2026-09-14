"""异常层次的单元测试（白盒：类型体系与捕获顺序）。"""
import pytest

from checker.exceptions import (
    FileReadError,
    FileWriteError,
    PaperCheckerError,
    UsageError,
)

def test_usage_error_is_paper_checker_error():
    """UsageError应属于PaperCheckerError体系。"""
    assert issubclass(UsageError, PaperCheckerError)

def test_file_read_error_is_paper_checker_error():
    """FileReadError应属于PaperCheckerError体系。"""
    assert issubclass(FileReadError, PaperCheckerError)

def test_file_write_error_is_paper_checker_error():
    """FileWriteError应属于PaperCheckerError体系。"""
    assert issubclass(FileWriteError, PaperCheckerError)

def test_paper_checker_error_is_exception():
    """PaperCheckerError应继承自Exception，保证可被捕获。"""
    assert issubclass(PaperCheckerError, Exception)

def test_usage_error_has_message():
    """异常应携带可读的错误信息。"""
    with pytest.raises(UsageError) as exc_info:
        raise UsageError("参数个数不正确")
    assert "参数" in str(exc_info.value)
