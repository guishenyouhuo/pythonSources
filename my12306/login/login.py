#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-7 9:49
# @Author  : wangfei
# @File    : login.py

from recognizeImage import get_title_context
import requests
import urllib3
from recognize_container import RecognizeContainer
import os
from private_constants import USER_NAME, PASSWORD
from common_constants import AUTO_IDENTIFY_CODE, CODE_POSITION

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__author__ = "wangfei"

headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
}

req = requests.session()


def del_file(path):
    for i in os.listdir(path):
        # 取文件绝对路径
        path_file = os.path.join(path, i)
        if os.path.isfile(path_file):
            os.remove(path_file)
        else:
            del_file(path_file)


def get_ident_code(code_url, img_code):
    """
    获取验证码
    :param code_url:
    :param img_code:
    :return:
    """
    del_file("../images")
    response = req.get(code_url, headers=headers, verify=False)
    response.encoding = 'utf-8'
    if response.status_code == 200:
        with open(img_code, 'wb') as fn:
            fn.write(response.content)
            print("验证码图片下载成功！")
            return True
    else:
        print("验证码下载失败！正在重试...")
        get_ident_code(code_url, img_code)


def check_iden_code(check_url, image_code, image_title):
    """
    分析并校验验证码
    :param check_url:
    :param image_code:
    :param image_title:
    :return:
    """
    if AUTO_IDENTIFY_CODE:
        print("自动识别...")
        title_list = get_title_context(image_code, image_title)
        rc = RecognizeContainer("../images")
        content_list = rc.get_text(image_code)
        if len(content_list) == 0:
            print("识别验证码内容失败，正在重试...")
            check_iden_code(check_url, image_code, image_title)
        point = list()
        for li in content_list:
            # 得到每一个坐标点和内容
            # 循环标题，进行比对
            for title_text in title_list:
                for po, value in li.items():
                    if title_text in value:
                        # 判断当前坐标点是否存在
                        if po not in point:
                            print("识别出一个坐标点")
                            point.append(po)
                # 再次对标题进行分割
                # for tx in title_text:
                #     for po, value in li.items():
                #         if tx in value:
                #             # 判断当前坐标点是否存在
                #             if po not in point:
                #                 print("识别出一个坐标点", end=":")
                #                 print(po)
                #                 point.append(po)
        answer = ",".join(point)
    else:
        index = input("人工识别，请输入验证码位置索引【0~7】，以逗号分隔：\n")
        index_list = index.split(",")
        pos_list = list()
        for pos in index_list:
            pos_list.append(CODE_POSITION[int(pos)])
        answer = ",".join(pos_list)

    print("开始进行验证码校验...answer: ", end="")
    print(answer)
    data = {
        "answer": answer,
        "login_site": "E",
        "rand": "sjrand"
    }
    response = req.post(check_url, data=data, headers=headers, verify=False)
    print(response.text)
    if response.status_code != 200:
        return False
    code = response.json()['result_code']
    # 取出验证结果，4：成功  5：验证失败  7：过期
    if str(code) == '4':
        return True
    else:
        return False


def login():
    code_url = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.5063958861628526"
    code_check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
    login_url = "https://kyfw.12306.cn/passport/web/login"
    code_image_path = "../images/code.png"
    title_image_path = "../images/temp_title"
    print("获取验证码...")
    get_ident_code(code_url, code_image_path)
    print("识别并验证验证码...")
    if check_iden_code(code_check_url, code_image_path, title_image_path):
        print("验证码验证成功，开始登录...")
        data = {
            'username': USER_NAME,
            'password': PASSWORD,
            'appid': 'otn'
        }
        result = req.post(url=login_url, data=data, headers=headers, verify=False)
        print("登录返回结果:", end=result.text)
        return result
    else:
        print("验证码验证失败，正在重新尝试....")
        return login()


if __name__ == "__main__":
    try:
        login()
    except Exception:
        print("抛出异常，正在重试....")
        login()
