#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/8/11 0011 下午 11:44
# @Author  : Administrator
# @File    : buy_ticket.py

from login import login
import requests
import urllib3
from common_constants import IS_AUTO_BUY
from query_train import QueryTrain
from urllib import parse
import datetime
import time
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__author__ = "wangfei"

headers = {
    "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
}

# cookies信息(取登录的cookie)
cookies = ""

# 车票信息
ticket_info = "北京 武汉 2018-08-26"
ticInfo = ticket_info.split(" ")
from_station = ticInfo[0]
to_station = ticInfo[1]
date = ticInfo[2]

req = requests.session()


def check_uamauthclient():
    """
    检查客户端是否登录
    :return:
    """

    # 先获取newapptk
    print("验证是否登录，得到newapptk")
    data = {
        "appid": "otn"
    }
    tk_url = "https://kyfw.12306.cn/passport/web/auth/uamtk"
    response = req.post(tk_url, data=data, headers=headers, cookies=cookies)
    print(response.text)
    newapptk_id = response.json()['newapptk']
    data = {
        "tk": newapptk_id,
        "_json_att": ""
    }

    print("检查unamuth客户端")
    url = "https://kyfw.12306.cn/otn/uamauthclient"
    resp = req.post(url, data=data, headers=headers)
    # 反回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        print(resp.text)
        """
            会存在失败的情况，网络原因，转json将会失败
        """
        te = resp.json()
        if te["result_code"] == "0":
            print("用户名：", te['username'], "apptk_id: ", te['apptk'])


def init_buy_page():
    print("初始化购票页面...")
    url = "https://kyfw.12306.cn/otn/leftTicket/init"
    resp = req.get(url, headers=headers, cookies=cookies)
    if resp.status_code == requests.codes.ok:
        print("购票页面初始化成功!")


def check_user():
    """
    检查用户是否登陆
    :return:
    """
    print("检查用户是否登录")
    url = "https://kyfw.12306.cn/otn/login/checkUser"
    data = {
        "_json_att": ""
    }
    resp = req.post(url, data=data, headers=headers, cookies=cookies)
    # 反回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        print(resp.text)


def submit_order_request(trick_data):
    """
    进行订单检查
    :return:
    """
    print("开始进行订单检查...")
    url = "https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest"

    """
        分析代码的js为：
        https://kyfw.12306.cn/otn/resources/merged/queryLeftTicket_end_js.js?scriptVersion=1.9058 
        在该js中，checkG1234方法就有详细的说明
        格式化之后在7606行

        点击预订参数说明：
            p1:车次组第一个元素
            p2:出发时间
            p3:车次数组第三个元素
            p4: 出发地代码
            p5: 结束地代码
            是用来拼接成以下数据的
    """

    """

     "secretStr" 车次,需要进行解码
     "train_date": 出发日期
     "back_train_date"  返回日期
     "tour_flag": "dc"  单程/ 往返(wc)
     "purpose_codes":  "ADULT"  普通/学生(0X00)
     "query_from_stati":  出发车站 ，可以在查询车次接口中得到
     "query_to_station":  返回车站，  可以在查询车次接口中得到
     "undefined": ""  应该是跟返回数据相关
    """

    data = {
        "secretStr": parse.unquote(trick_data[len(trick_data) - 1][0]),
        "train_date": date,
        "back_train_date": datetime.datetime.now().strftime('%Y-%m-%d'),
        "tour_flag": "dc",
        "purpose_codes": "ADULT",
        "query_from_station_name": from_station,
        "query_to_station_name": to_station,
        "undefined": ""
    }
    resp = req.post(url, data=data, headers=headers, cookies=cookies)
    # 反回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        # {"validateMessagesShowId":"_validatorMessage","status":true,"httpstatus":200,"分析js文件":"N","messages":[],"validateMessages":{}}
        print(resp.text)
        if resp.json()['status']:
            return True
        else:
            print("异常结果：", resp.json()['messages'][0])
            # 强制退出程序，去处理未完成的订单
            exit(0)
            return False


def initDc():
    """
    在进行点击了预定，初始化订票页面
    :return:
    """
    print("初始化订单数据")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
    data = {
        "_json_att": ""
    }
    resp = req.post(url, data=data, headers=headers)
    # print(resp.text)
    # 反回一个验证通过信息
    if resp.status_code == requests.codes.ok:
        a1 = re.search(r'globalRepeatSubmitToken.+', resp.text).group()
        globalRepeatSubmitToken = re.sub(r'(globalRepeatSubmitToken)|(=)|(\s)|(;)|(\')', '', a1)

        b1 = re.search(r'key_check_isChange.+', resp.text).group().split(',')[0]
        key_check_isChange = re.sub(r'(key_check_isChange)|(\')|(:)', '', b1)

        return globalRepeatSubmitToken, key_check_isChange


def get_passenger(repeat_submit_token):
    """
     获取到用户的乘车人信息
    :param repeat_submit_token:
    :return:
    """
    print("获取乘车人信息.......")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs"
    data = {
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": repeat_submit_token
    }
    resp = req.post(url, data=data, cookies=cookies, headers=headers)
    if resp.status_code == requests.codes.ok:
        print(resp.text)


def check_order_info(repeat_submit_token):
    """
    再次检查订单
    :param repeat_submit_token:
    :return:
    """
    """
    js信息：https://kyfw.12306.cn/otn/resources/merged/passengerInfo_js.js?scriptVersion=1.9058
    参数信息
    cancel_flag:2  默认
    bed_level_order_num:000000000000000000000000000000  默认
    passengerTicketStr:3,0,1,黎安永,1,522121197001016817,,N  用户信息
    oldPassengerStr:黎安永,1,522121197001016817,1_
    tour_flag:dc 
    randCode: 需要重新获取验证码，为空
    whatsSelect:1  是否是常用联系人中选择的需要购买车票的人
    _json_att:
    REPEAT_SUBMIT_TOKEN:89089246526d93566b2266de1791af87
    """
    passengerTicketStr = "3, 0, 1, 黎安永, 1, 522121197001016817,, N"
    oldPassengerStr = "黎安永, 1, 522121197001016817, 1"
    print("检查订单信息")
    data = {
        "cancel_flag": "2",
        "bed_level_order_num": "000000000000000000000000000000",
        "passengerTicketStr": passengerTicketStr,
        "oldPassengerStr": oldPassengerStr,
        "tour_flag": "dc",
        "randCode": "",
        "whatsSelect": "1",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": repeat_submit_token
    }
    url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
    resp = req.post(url, data=data, cookies=cookies, headers=headers)
    if resp.status_code == requests.codes.ok:
        print(resp.text)
        if '"submitStatus":true' in resp.text:
            return True
    return False


def tranceDate(param):
    """
    将传递的字符串转化为时间
    :param param: 时间： 2017-12-29
    :return: Fri Dec 29 2017 00:00:00 GMT+0800 (中国标准时间)
    """
    ts = time.mktime(time.strptime(param, "%Y-%m-%d"))
    s = time.ctime(ts)
    t1 = s[0:11] + s[20:] + " 00:00:00 GMT+0800 (中国标准时间)"
    return t1


def getQueueCount(trick_data, REPEAT_SUBMIT_TOKEN, query_date):
    """
        判断是都有余票
    :param REPEAT_SUBMIT_TOKEN:
    :return:
    """
    print("检查余票...")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
    # 将字符串转化为需要的时间
    train_data = tranceDate(query_date)
    data = {
        # 时间
        "train_date": train_data,
        # 车次编号
        "train_no": trick_data[len(trick_data) - 1][2],
        # 火车代码
        "stationTrainCode": trick_data[len(trick_data) - 1][3],
        # 座位类型 1：硬卧 3：硬座
        "seatType": "3",
        # 出发点，终止地址
        "fromStationTelecode": trick_data[len(trick_data) - 1][6],
        "toStationTelecode": trick_data[len(trick_data) - 1][7],
        "leftTicket": trick_data[len(trick_data) - 1][12],
        "purpose_codes": "00",
        "train_location": trick_data[len(trick_data) - 1][15],
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
    print(data)
    resp = req.post(url, data=data, headers=headers, cookies=cookies)
    if resp.status_code == requests.codes.ok:
        # 有余票，返回值将会是True
        print(resp.text)


def confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, trick_data):
    """
    真正的提交订单
    最后一次确认订单
    :return: 返回购票结果
    """
    """
    passengerTicketStr:3,0,1,黎安永,1,522121197001016817,,N
    oldPassengerStr:黎安永,1,522121197001016817,1_
    tour_flag:dc
    randCode:
    purpose_codes:00
    key_check_isChange:1C84C0EA5533D3D73F88A0C7A6BE1E73D65BF9C00C38B3ABF8D09A12
    train_location:QZ
    choose_seats:
    seatDetailType:000
    whatsSelect:1
    roomType:00
    dwAll:N
    _json_att:
    REPEAT_SUBMIT_TOKEN:89089246526d93566b2266de1791af87
    """
    print("最后一次确认订单")
    url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"

    passengerTicketStr = "3, 0, 1, 黎安永, 1, 522121197001016817,, N"
    oldPassengerStr = "黎安永, 1, 522121197001016817, 1"
    data = {
        "passengerTicketStr": passengerTicketStr,
        "oldPassengerStr": oldPassengerStr,
        "randCode": "",
        "purpose_codes": "00",
        "key_check_isChange": key_check_isChange,
        "leftTicketStr": trick_data[len(trick_data) - 1][12],
        "train_location": trick_data[len(trick_data) - 1][15],
        "choose_seats": "",
        "seatDetailType": "000",
        "whatsSelect": "1",
        "roomType": "00",
        "dwAll": "N",
        "_json_att": "",
        "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
    }
    print(data)
    resp = req.post(url, data=data, cookies=cookies, headers=headers)
    if resp.status_code == requests.codes.ok:
        print(resp.text)
        # 返回购票结果
        return resp.json()['data']['submitStatus']


if __name__ == "__main__":
    # 首先登录（包括验证码识别）
    login_result = login()
    cookies = login_result.headers['set-cookie']
    if login_result["result_code"] == "0":
        # 阶段一：验证是否登录状态
        check_uamauthclient()
        # 阶段二：进行车票确认
        # 初始化购票页面
        init_buy_page()
        print("查询车票数据: 出发地:{},目的地:{},出发日期:{}".format(from_station, to_station, date))
        while IS_AUTO_BUY:
            # 查询票
            qt = QueryTrain(requests.session(), headers)
            query_ticket_data = qt.query_train(from_station, to_station, date)
            print("打印车次信息：")
            qt.trans_print_data(query_ticket_data)
            # 检查用户是否登录
            check_user()
            # 初始化订单
            order_check_result = submit_order_request(query_ticket_data)
            # 说明订单成功，需要确认订单即可
            if order_check_result:
                # 初始化订单数据,获取到REPEAT_SUBMIT_TOKEN,key_check_isChange,leftTicketStr
                REPEAT_SUBMIT_TOKEN, key_check_isChange = initDc()
                # 检查订单信息
                print("得到校验uuid:", REPEAT_SUBMIT_TOKEN)
                # 获取该用户下的乘车人信息
                get_passenger(REPEAT_SUBMIT_TOKEN)
                # 进行订单确认
                check_order_result = check_order_info(REPEAT_SUBMIT_TOKEN)
                if check_order_result:
                    # 订单检查成功，尽心确认订单
                    # 查询订单队列余票
                    getQueueCount(query_ticket_data, REPEAT_SUBMIT_TOKEN, date)
                    # 最后一次确认订单
                    ok = confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, query_ticket_data)
                    if ok:
                        print("购票成功,退出程序!")
                        exit(0)
                    else:
                        # 休眠5秒钟，防止被防刷票封ip
                        time.sleep(5)
    else:
        print("登录失败！")
