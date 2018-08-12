#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-6 14:19
# @Author  : wangfei
# @File    : recognize_identify_code.py
import requests
import urllib3
from PIL import Image, ImageFilter, ImageEnhance
from bs4 import BeautifulSoup
from recognize_title import BaiDu
from common_constants import CODE_POSITION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

__author__ = "wangfei"


class RecognizeIdentCode:
    def __init__(self, base_img_url, header):
        self.base_img_url = base_img_url
        self.header = header

    upload_url = "http://image.baidu.com/pictureup/uploadshitu?fr=flash&fm=index&pos=upload"

    pic_base = "query_temp_img"
    pic_ext = ".png"

    def __upload_pic__(self, file_num):
        """
        上传图片到百度
        :param file_num:
        :return:
        """
        img = open(self.base_img_url + "/" + self.pic_base + file_num + self.pic_ext, 'rb').read()
        files = {
            'fileheight': "0",
            'newfilesize': str(len(img)),
            'compresstime': "0",
            'Filename': "image.png",
            'filewidth': "0",
            'filesize': str(len(img)),
            'filetype': 'image/png',
            'Upload': "Submit Query",
            'filedata': ("image.png", img)
        }
        resp = requests.post(self.upload_url, files=files, headers=self.header, verify=False)
        return "http://image.baidu.com" + resp.text

    def __get_query_content__(self, query_url):
        """
        获取百度图片搜索结果
        :param query_url:
        :return:
        """
        response = requests.get(query_url, headers=self.header, verify=False)
        li = list()
        if response.status_code == requests.codes.ok:
            bs = BeautifulSoup(response.text, "html.parser")
            re = bs.find_all("a", class_="guess-info-word-link guess-info-word-highlight")
            for link in re:
                li.append(link.get_text())
            # 识别动物
            te = bs.find_all("ul", class_="shituplant-tag")
            for l in te:
                for child in l.children:
                    try:
                        li.append(child.get_text())
                    except:
                        pass
            # 如果没有识别到，则开始识别相似图片
            if len(li) == 0:
                simular_url = query_url.replace("pc_search", "similar")
                resp = requests.get(simular_url, headers=self.header, verify=False)
                json_info = resp.json()
                for fromTitle in json_info['data']:
                    li.append(fromTitle['fromPageTitle'])
            return "|".join(x for x in li)

    def get_title_pic(self, image_code, image_title, index):
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

    def get_title_context(self, image_code, image_title):
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
            self.get_title_pic(image_code, image_title, index)
            try:
                bd = BaiDu()
                res = bd.get_result(image_title + str(index) + ".png")
                print(res)
                if len(res['words_result']) != 0:
                    result.append(res['words_result'][0]['words'])
            except Exception:
                print("识别出现异常！")
        return result

    def get_text(self, img_url):
        """
        识别内容
        :param img_url:
        :return:
        """
        li = list()
        ImageEnhance.Contrast(Image.open(img_url)).enhance(1.3).save(img_url)
        imgs = Image.open(img_url)
        imgs.filter(ImageFilter.BLUR).filter(ImageFilter.MaxFilter(23))
        imgs.convert('L')
        x_width, y_height = imgs.size
        width = x_width / 4
        height = (y_height - 30) / 2
        for x_ in range(0, 2):
            for y_ in range(0, 4):
                left = y_ * width
                right = (y_ + 1) * width
                index = x_ * 4 + y_
                box = (left, x_ * height + 30, right, (x_ + 1) * height + 30)
                file_num = str(x_) + str(y_)
                imgs.crop(box).save(self.base_img_url + "/" + self.pic_base + file_num + self.pic_ext)
                # 上传图片并获取查询地址
                query_url = self.__upload_pic__(file_num)
                context = self.__get_query_content__(query_url)
                # 由于12306官方验证码是验证正确验证码的坐标范围,我们取每个验证码中点的坐标(大约值)
                # 将坐标保存
                li.append({CODE_POSITION[index]: context})
        return li


if __name__ == "__main__":
    # rc = RecognizeContainer("../images")
    # print(rc.get_text("../images/code.png"))
    img = open("../images/query_temp_img11.png", 'rb').read()
    files = {
        'fileheight': "0",
        'newfilesize': str(len(img)),
        'compresstime': "0",
        'Filename': "image.png",
        'filewidth': "0",
        'filesize': str(len(img)),
        'filetype': 'image/png',
        'Upload': "Submit Query",
        'filedata': ("image.png", img)
    }
    upload_url = "http://image.baidu.com/pictureup/uploadshitu?fr=flash&fm=index&pos=upload"
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    resp = requests.post(upload_url, files=files, headers=headers, verify=False)
    query_url = "http://image.baidu.com" + resp.text
    response = requests.get(query_url, headers=headers, verify=False)
    bs = BeautifulSoup(response.text, "html.parser")
    re = bs.find_all("a", class_="guess-info-word-link guess-info-word-highlight")
    print(re)
    simular_url = query_url.replace("pc_search", "similar")
    resp = requests.get(simular_url, headers=headers, verify=False)
    json_info = resp.json()
    li = list()
    for fromTitle in json_info['data']:
        li.append(fromTitle['fromPageTitle'])
    print(li)
