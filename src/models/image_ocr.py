# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: image_ocr.py
# @time: 2024/8/15 22:17
import json
import os
from paddleocr import PaddleOCR

from src.config.config import PROJECT_DIR


def get_pdf_file_ocr_result(pdf_file_dir_path: str) -> dict[int, str]:
    # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
    # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
    ocr = PaddleOCR(use_angle_cls=False, lang="ch")
    page_ocr_result = {}
    files = [file for file in os.listdir(pdf_file_dir_path) if file.endswith(".png")]
    # 按数字大小排序
    files.sort(key=lambda x: int(x.split(".")[0]))
    for file in files:
        text = ""
        page_no = int(file.split(".")[0])
        img_path = os.path.join(pdf_file_dir_path, file)
        result = ocr.ocr(img_path, cls=False)
        for idx in range(len(result)):
            res = result[idx]
            if res:
                for line in res:
                    text += line[1][0]
                    print(f"page: {page_no}, text: {line[1][0]}")
        page_ocr_result[page_no] = text

    # 将识别结果保存到json文件中
    json_output_path = os.path.join(pdf_file_dir_path, "ocr_result.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(page_ocr_result, ensure_ascii=False, indent=4))
    return page_ocr_result


if __name__ == '__main__':
    pdf_file_name = "wushihui"
    test_dir_path = os.path.join(PROJECT_DIR, f"output/{pdf_file_name}")
    get_pdf_file_ocr_result(test_dir_path)
