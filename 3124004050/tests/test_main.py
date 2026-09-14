"""入口模块的集成测试（白盒：覆盖正常流程与全部异常分支）。"""
import pytest

import main as main_module
from checker.exceptions import FileReadError, UsageError

def _write(path, content, encoding="utf-8"):
    """测试辅助：向文件写入内容。"""
    with open(path, "w", encoding=encoding) as file:
        file.write(content)

def test_parse_args_valid():
    """参数个数正确时应返回三元组。"""
    assert main_module.parse_args(["a", "b", "c"]) == ("a", "b", "c")

def test_parse_args_too_few_raises():
    """参数不足时应抛出 UsageError。"""
    with pytest.raises(UsageError):
        main_module.parse_args(["only_one"])

def test_main_usage_error_exit_code(capsys):
    """入口对参数错误应返回退出码1且不崩溃。"""
    code = main_module.main(["a", "b"])
    assert code == 1
    assert "参数" in capsys.readouterr().err

def test_main_missing_input_file(tmp_path, capsys):
    """输入文件不存在时应返回退出码1。"""
    missing = str(tmp_path / "not_exist.txt")
    ans = str(tmp_path / "ans.txt")
    code = main_module.main([missing, missing, ans])
    assert code == 1
    assert "无法读取文件" in capsys.readouterr().err

def test_sample_modified_paper_rate_range(tmp_path):
    """样例场景（增删改）：重复率应落在(0.5,1.0)区间。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    _write(orig, "今天是星期天，天气晴，今天晚上我要去看电影。")
    _write(plag, "今天是周天，天气晴朗，我晚上要去看电影。")
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    rate = float(ans.read_text(encoding="utf-8"))
    assert 0.5 <= rate < 1.0

def test_identical_files_output_100(tmp_path):
    """完全相同文件：答案应为1.00。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    text = "今天天气很好，我们一起去公园散步。"
    _write(orig, text)
    _write(plag, text)
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    assert ans.read_text(encoding="utf-8") == "1.00"

def test_completely_different_files_output_000(tmp_path):
    """完全不同文件：答案应为0.00。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    _write(orig, "苹果香蕉橘子")
    _write(plag, "跑步游泳打球")
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    assert ans.read_text(encoding="utf-8") == "0.00"

def test_gbk_encoded_input_readable(tmp_path):
    """GBK 编码的输入文件应能被正常读取。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    _write(orig, "天气很好，适合出游。", encoding="gbk")
    _write(plag, "天气很好，适合出游。", encoding="gbk")
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    assert ans.read_text(encoding="utf-8") == "1.00"

def test_multiline_text_handled(tmp_path):
    """多段落文本应能正常计算。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    _write(orig, "第一段内容。\n第二段内容。\n第三段内容。")
    _write(plag, "第一段内容。\n第二段内容。")
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    rate = float(ans.read_text(encoding="utf-8"))
    assert 0.5 <= rate <= 1.0

def test_read_text_invalid_encoding_raises(tmp_path):
    """无法识别的编码应抛出 FileReadError。"""
    bad = tmp_path / "bad.txt"
    bad.write_bytes(b"\xff\xfe\x00\x81\x82\x83")
    with pytest.raises(FileReadError):
        main_module.read_text(str(bad))

def test_main_write_error_exit_code(tmp_path, capsys):
    """输出目录不存在时返回退出码 1 且不崩溃。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    _write(orig, "今天天气很好")
    _write(plag, "今天天气很好")
    ans = str(tmp_path / "no_such_dir" / "ans.txt")
    code = main_module.main([str(orig), str(plag), ans])
    assert code == 1
    assert "无法写入" in capsys.readouterr().err

def test_empty_files_output_000(tmp_path):
    """两个空文件：答案应为 0.00（空文本无可比内容）。"""
    orig = tmp_path / "orig.txt"
    plag = tmp_path / "plag.txt"
    ans = tmp_path / "ans.txt"
    _write(orig, "")
    _write(plag, "")
    assert main_module.main([str(orig), str(plag), str(ans)]) == 0
    assert ans.read_text(encoding="utf-8") == "0.00"
