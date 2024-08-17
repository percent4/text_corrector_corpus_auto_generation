# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: corpus_generator.py
# @time: 2024/8/15 22:41
import os
import json

import difflib
from sentencex import segment

from src.config.config import PROJECT_DIR


def text_preprocess(text: str) -> str:
    """
    text preprocess
    :param text: original text
    :return: preprocessed text
    """
    text = text.replace("\n", "")
    return text


def get_sentences(text: str) -> list[str]:
    """
    get sentences from text
    :param text: original text
    :return: sentences list
    """
    sentences = segment("zh", text)
    return sentences


def find_similar_sentence(sent: str, candidate_sentences: list[str]) -> str:
    """
    find similar sentence
    :param sent: sentence
    :param candidate_sentences: candidate sentences
    :return: similar sentence
    """
    for candidate_sent in candidate_sentences:
        if sent == candidate_sent:
            return candidate_sent
        elif len(sent) == len(candidate_sent):
            # 计算两个句子的jaccard相似度
            set_sent = set(sent)
            set_candidate_sent = set(candidate_sent)
            jaccard_sim = len(set_sent & set_candidate_sent) / len(set_sent | set_candidate_sent)
            if jaccard_sim > 0.8:
                return candidate_sent
        return ""


# 使用difflib, 查找s1 与 s2 不同的文字
def find_differences(s1: str, s2: str):
    # 使用 difflib.SequenceMatcher 来比较两个字符串
    matcher = difflib.SequenceMatcher(None, s1, s2)

    # 存储不同的字符及其在 s1 中的下标
    differences = []

    # 遍历匹配块，获取不匹配的部分
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag != 'equal':
            # 不匹配的部分
            for i in range(i1, i2):
                differences.append((i, s1[i]))

    return differences


def get_corpus(original_text: str, ocr_text: str) -> list[dict]:
    corpus_list = []
    original_sents = get_sentences(text_preprocess(original_text))
    ocr_sents = get_sentences(text_preprocess(ocr_text))
    for ocr_sent in ocr_sents:
        if len(ocr_sent) > 4:   # 过滤掉长度小于4的ocr句子
            similar_sent = find_similar_sentence(ocr_sent, original_sents)
            if similar_sent:
                # 如果两个句子中的不同文字数量大于0且小于6, 则添加至corpus_list，认为是文本纠错语料
                diffs = find_differences(similar_sent, ocr_sent)
                if 0 < len(diffs) < 6:
                    corpus_list.append({
                        "ori_sent": similar_sent,
                        "ocr_sent": ocr_sent,
                        "diffs": diffs
                    })

    return corpus_list


if __name__ == '__main__':
    pdf_file_name = "wushihui"
    pdf_dir_path = os.path.join(PROJECT_DIR, f"output/{pdf_file_name}")
    ocr_result_file_path = os.path.join(pdf_dir_path, "ocr_result.json")
    original_text_file_path = os.path.join(pdf_dir_path, "original_text.json")
    with open(ocr_result_file_path, "r", encoding="utf-8") as f:
        ocr_result_dict = json.load(f)
    with open(original_text_file_path, "r", encoding="utf-8") as f:
        original_text_dict = json.load(f)

    # 生成文本纠错语料
    final_corpus_list = []
    for key, value in ocr_result_dict.items():
        my_ocr_text = value
        if key in original_text_dict:
            my_original_text = original_text_dict[key]
            my_corpus_list = get_corpus(my_original_text, my_ocr_text)
            final_corpus_list.extend(my_corpus_list)

    # 将文本纠错语料保存到json文件中
    json_output_path = os.path.join(PROJECT_DIR, f"data/{pdf_dir_path.split('/')[-1]}_corpus.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(final_corpus_list, ensure_ascii=False, indent=4))
    print(f"已找到{len(final_corpus_list)}条文本纠错语料，保存至{json_output_path}")
