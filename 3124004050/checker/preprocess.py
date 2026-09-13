"""文本预处理模块：文本清洗与中文分词。
性能改进：
    1.关闭jieba词典加载时的日志输出（减少 I/O）；
    2.tokenize使用LRU缓存，同一文本重复分词时直接命中缓存。
"""

import logging
import re
from functools import lru_cache

import jieba

jieba.setLogLevel(logging.WARNING)

#匹配"仅由标点/符号组成"的token（Unicode模式下\w包含中文，不会误删中文词）
_PUNCT_ONLY = re.compile(r"^[\W_]+$", re.UNICODE)

def clean_text(text):
    """清洗文本：将全角空格转为普通空格，并去除首尾空白。"""
    return text.replace("\u3000", " ").strip()

@lru_cache(maxsize=128)
def tokenize(text):
    """对文本分词，过滤纯标点与空白token，英文统一转为小写。"""
    words = []
    for word in jieba.cut(clean_text(text)):
        word = word.strip().lower()
        if not word or _PUNCT_ONLY.match(word):
            continue
        words.append(word)
    return words
