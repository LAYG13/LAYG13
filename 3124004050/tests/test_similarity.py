"""相似度计算模块的单元测试（白盒：覆盖各分支与边界）。"""
import math

import pytest

from checker.similarity import cosine_similarity

def test_identical_lists_returns_one():
    """完全相同词序列：余弦值应为 1。"""
    words = ["今天", "天气", "电影"]
    assert cosine_similarity(words, words) == pytest.approx(1.0)

def test_disjoint_lists_returns_zero():
    """毫无共同词的序列：余弦值应为 0。"""
    assert cosine_similarity(["苹果", "香蕉"], ["跑步", "游泳"]) == pytest.approx(0.0)

def test_partial_overlap_known_value():
    """部分重合：共同词占 2/3，验证数值精确性。"""
    assert cosine_similarity(["我", "爱", "编程"], ["我", "爱", "学习"]) == pytest.approx(
        2.0 / 3.0, abs=1e-6
    )

def test_empty_first_list():
    """边界：第一序列为空，返回0。"""
    assert cosine_similarity([], ["a"]) == 0.0

def test_empty_second_list():
    """边界：第二序列为空，返回0。"""
    assert cosine_similarity(["a"], []) == 0.0

def test_empty_both_lists():
    """边界：两序列均为空，返回0（避免除零）。"""
    assert cosine_similarity([], []) == 0.0

def test_repeated_words_are_similar():
    """词频加权：两序列都只有同一个词，重复次数不同仍应判为1。"""
    assert cosine_similarity(["电影"] * 5, ["电影"] * 3) == pytest.approx(1.0)

def test_frequency_weight_affects_result():
    """词频权重：a中出现两次的词应提高相似度，验证手工计算值2/sqrt(10)。"""
    value = cosine_similarity(["a", "a", "b"], ["a", "c"])
    expected = 2.0 / math.sqrt(10.0)
    assert value == pytest.approx(expected, abs=1e-6)
