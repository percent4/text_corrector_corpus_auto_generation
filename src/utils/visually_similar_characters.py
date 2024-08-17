# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: visually_similar_characters.py
# @time: 2024/8/17 17:33
import os
import json
from pprint import pprint
from collections import defaultdict


from src.config.config import PROJECT_DIR

visually_similar_characters = defaultdict(set)

for file in os.listdir(os.path.join(PROJECT_DIR, 'data')):
    file_path = os.path.join(PROJECT_DIR, 'data', file)
    # read json file
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.loads(f.read())
    for sample in data:
        for record_item in sample["diffs"]:
            char = record_item[1]
            # 判断是否为中文字符
            if '\u4e00' <= char <= '\u9fff':
                visually_similar_characters[char].add(sample['ocr_sent'][record_item[0]])

pprint(visually_similar_characters)
