# -*- coding: utf-8 -*-
# @place: Pudong, Shanghai
# @file: preprocess.py
# @time: 2024/8/15 22:03
import os
import json
import time

import fitz
from PIL import Image

from src.config.config import PROJECT_DIR


# 使用fitz模块提取文本， 未使用OCR
def get_pdf_file_text(
        pdf_file_path: str
) -> dict[int, str]:
    doc = fitz.open(pdf_file_path)
    page_result = {}
    for i in range(doc.page_count):
        page = doc[i]
        text = ""
        page_content = page.get_text("blocks")
        for record in page_content:
            if not record[-1]:
                text += record[4]
        page_result[i] = text
    doc.close()
    # 将识别结果保存到json文件中
    pdf_file_name = pdf_file_path.split('/')[-1].split(".")[0]
    json_output_path = os.path.join(PROJECT_DIR, f"output/{pdf_file_name}/original_text.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(page_result, ensure_ascii=False, indent=4))
    return page_result


# 将PDF文件转换为图片
def convert_pdf_2_img(
        pdf_file: str
) -> list[str]:
    """
    convert pdf to image
    :param pdf_file: pdf file path
    :param pages: convert pages number(at most)
    :return: output of image file path list
    """
    pdf_document = fitz.open(pdf_file)
    output_image_file_path_list = []
    # Iterate through each page and convert to an image
    for page_number in range(pdf_document.page_count):
        # Get the page
        page = pdf_document[page_number]
        # Convert the page to an image
        pix = page.get_pixmap()
        # Create a Pillow Image object from the pixmap
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        # Save the image
        pdf_file_name = pdf_file.split('/')[-1].split(".")[0]
        output_dir = os.path.join(PROJECT_DIR, f"output/{pdf_file_name}")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        save_image_path = os.path.join(output_dir, f"{page_number}.png")
        image.save(save_image_path)
        output_image_file_path_list.append(save_image_path)
    # Close the PDF file
    pdf_document.close()
    return output_image_file_path_list


if __name__ == '__main__':
    s_time = time.time()
    file_name = "weite.pdf"
    file_path = os.path.join(PROJECT_DIR, f"docs/{file_name}")
    output_image_path_list = convert_pdf_2_img(file_path)
    original_text = get_pdf_file_text(file_path)


