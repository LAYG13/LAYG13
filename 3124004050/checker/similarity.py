"""相似度计算模块：基于词频向量的余弦相似度。"""

import math
from collections import Counter

def cosine_similarity(words_a, words_b):
    """计算两个词序列的余弦相似度，返回[0,1]之间的浮点数。
    任一序列为空时返回0.0（没有内容可比对，避免除零）。
    """
    if not words_a or not words_b:
        return 0.0
    counter_a = Counter(words_a)
    counter_b = Counter(words_b)
    dot = sum(count * counter_b[word] for word, count in counter_a.items())
    norm_a = math.sqrt(sum(count * count for count in counter_a.values()))
    norm_b = math.sqrt(sum(count * count for count in counter_b.values()))
    return dot / (norm_a * norm_b)
