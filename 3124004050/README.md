# 论文查重

一个基于Python的论文查重工具，使用 jieba 分词+余弦相似度计算两篇论文的重复率。

## 功能

- 命令行三参数文件输入输出
- 自动识别常见中文编码（UTF-8-sig/UTF-8/GBK）
- jieba分词+余弦相似度
- 答案保留两位小数输出

## 使用方法
```
python main.py <论文原文路径> <抄袭版论文路径> <答案文件路径>
```
```
示例：python main.py samples/orig.txt samples/orig_add.txt samples/ans.txt
```

## 项目结构
```
paper_checker/
├── main.py              # 入口：参数解析、文件读写、主流程
├── checker/
│   ├── exceptions.py    # 自定义异常体系
│   ├── preprocess.py    # 文本清洗与分词
│   └── similarity.py    # 余弦相似度计算
├── tests/               # 单元测试（31 个）
├── samples/             # 样例与测试文本
├── requirements.txt     # 依赖：jieba
└── pytest.ini           # pytest 配置
```

## 测试
```
pytest
```
31个测试全部通过，覆盖率99%，pylint评分10.00/10。

## 依赖
jieba>=0.42.1


