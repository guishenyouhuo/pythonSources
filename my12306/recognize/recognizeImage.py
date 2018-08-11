#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-6 10:47
# @Author  : wangfei
# @File    : recognizeImage.py


import requests
import urllib3
from PIL import Image
from recognize_title import BaiDu
from recognize_container import RecognizeContainer


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__auther__ = "wangfei"


headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
}


def get_title_pic(image_code, image_title, index):
    """
    通过图片截取获得标题文字部分
    :param image_code:
    :param image_title:
    :param index:
    :return:
    """
    box = (120, 0, 178, 30) if index == 1 else (178, 0, 238, 30)
    image = Image.open(image_code)
    image.convert("L")
    t = image.crop(box)
    t.save(image_title + str(index) + ".png")


def get_title_context(image_code, image_title):
    """
    识别标题
    :param image_code:
    :param image_title:
    :return:
    """
    # 标题内容
    result = list()
    print("调用百度API进行标题识别：")
    for index in range(1, 3):
        get_title_pic(image_code, image_title, index)
        try:
            bd = BaiDu()
            res = bd.get_result(image_title + str(index) + ".png")
            print(res)
            if len(res['words_result']) != 0:
                result.append(res['words_result'][0]['words'])
        except Exception:
            print("识别出现异常！")
    return result


if __name__ == "__main__":
    image_code = "../images/code.png"
    image_title = "../images/temp_title"
    title_list = list()
    res = get_title_context(image_code, image_title)
    print(res)
    print("开始对图片内容进行识别....")
    c = RecognizeContainer("../images")
    lists = c.get_text("../images/code.png")
    print(lists)
    point = list()
    for li in lists:
        # 得到每一个坐标点和内容
        # 循环标题，进行比对
        for title_text in res:
            for po, value in li.items():
                if title_text in value:
                    # 判断当前坐标点是否存在
                    if po not in point:
                        print("识别出一个坐标点")
                        point.append(po)
            # 再次对标题进行分割
            for tx in title_text:
                for po, value in li.items():
                    if tx in value:
                        # 判断当前坐标点是否存在
                        if po not in point:
                            print("识别出一个坐标点")
                            point.append(po)
    print(point)

