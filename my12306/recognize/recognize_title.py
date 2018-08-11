#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-6 12:07
# @Author  : wangfei
# @File    : recognize_title.py


from aip import AipOcr

__author__ = "wangfei"

"""
    使用百度API进行文字识别
"""

# 定义常量
APP_ID = "11635823"
API_KEY = "qLfwDPDWyBtPz4ob2RxS568O"
SECRET_KEY = "BNj7PXnZdf35ZQKslaasfYkF8xtvE65F"

# 初始化Aip接口对象
client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

# 定义参数变量
options = {
    'detect_direction': 'true',
    'language_type': 'CHN_ENG',
}


class BaiDu(object):
    def get_file_content(self, file_path):
        """
        获取图片文件
        :param file_path:
        :return:
        """
        with open(file_path, 'rb') as fp:
            return fp.read()

    def get_result(self, image_url):
        """
        识别结果
        :param image_url:
        :return:
        """
        image = self.get_file_content(image_url)
        return client.basicGeneral(image, options)


if __name__ == "__main__":
    baidu = BaiDu()
    result = baidu.get_result("../images/temp_title1.png")
    print(result)
    print(result['words_result'][0]['words'])
