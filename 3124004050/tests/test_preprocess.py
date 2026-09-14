"""文本预处理模块的单元测试（白盒：清洗与过滤分支）。"""
from checker.preprocess import clean_text, tokenize

def test_clean_text_strips_whitespace():
    """首尾普通空白应被去除。"""
    assert clean_text("  你好  ") == "你好"

def test_clean_text_full_width_space():
    """全角空格应转为普通空格再去除。"""
    assert clean_text("\u3000你好\u3000") == "你好"

def test_tokenize_filters_punctuation():
    """中文标点不应出现在分词结果中。"""
    words = tokenize("今天，天气很好！")
    assert "，" not in words
    assert "！" not in words
    assert "今天" in words

def test_tokenize_lowercases_english():
    """英文 token 应统一转为小写。"""
    words = tokenize("Hello World")
    assert "hello" in words
    assert "world" in words

def test_tokenize_empty_text():
    """空文本分词结果应为空列表。"""
    assert not tokenize("")

def test_tokenize_punctuation_only():
    """纯标点文本分词结果应为空列表。"""
    assert not tokenize("，。！？；：")
