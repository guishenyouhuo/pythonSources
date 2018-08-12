#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Time    : 2018/8/11 0011 下午 11:44
# @Author  : Administrator
# @File    : buy_ticket.py

from login import LoginProcess
import requests
import urllib3
from common_constants import IS_AUTO_BUY
from query_train import QueryTrain
from urllib import parse
import datetime
import time
import re
from private_constants import PASSENGER_TICKET_STR, OLD_PASSENGER_STR

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__author__ = "wangfei"


# 车票信息
ticket_info = "武汉 孝感 2018-08-28 K1366"
ticInfo = ticket_info.split(" ")
from_station = ticInfo[0]
to_station = ticInfo[1]
date = ticInfo[2]
train_no = ticInfo[3]


class BuyTicket:

    def __init__(self, request, header):
        self.req = request
        self.header = header

    def check_uamauthclient(self):
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
        response = self.req.post(tk_url, data=data, headers=self.header)
        print(response.text)
        newapptk_id = response.json()['newapptk']
        data = {
            "tk": newapptk_id,
            "_json_att": ""
        }
        print("检查unamuth客户端")
        url = "https://kyfw.12306.cn/otn/uamauthclient"
        resp = self.req.post(url, data=data, headers=self.header)
        # 反回一个验证通过信息
        if resp.status_code == requests.codes.ok:
            print(resp.text)
            """
                会存在失败的情况，网络原因，转json将会失败
            """
            te = resp.json()
            if te["result_code"] == "0":
                print("用户名：", te['username'], "apptk_id: ", te['apptk'])

    def init_buy_page(self):
        print("初始化购票页面...")
        url = "https://kyfw.12306.cn/otn/leftTicket/init"
        resp = self.req.get(url, headers=self.header)
        if resp.status_code == requests.codes.ok:
            print("购票页面初始化成功!")

    def check_user(self):
        """
        检查用户是否登陆
        :return:
        """
        print("检查用户是否登录")
        url = "https://kyfw.12306.cn/otn/login/checkUser"
        data = {
            "_json_att": ""
        }
        resp = self.req.post(url, data=data, headers=self.header)
        # 反回一个验证通过信息
        if resp.status_code == requests.codes.ok:
            print(resp.text)

    def submit_order_request(self, trick_data):
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
            "secretStr": parse.unquote(trick_data[train_no][0]),
            "train_date": date,
            "back_train_date": datetime.datetime.now().strftime('%Y-%m-%d'),
            "tour_flag": "dc",
            "purpose_codes": "ADULT",
            "query_from_station_name": from_station,
            "query_to_station_name": to_station,
            "undefined": ""
        }
        resp = self.req.post(url, data=data, headers=self.header)
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

    def initDc(self):
        """
        在进行点击了预定，初始化订票页面
        :return:
        """
        print("初始化订单数据")
        url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        data = {
            "_json_att": ""
        }
        resp = self.req.post(url, data=data, headers=self.header)
        # print(resp.text)
        # 反回一个验证通过信息
        if resp.status_code == requests.codes.ok:
            a1 = re.search(r'globalRepeatSubmitToken.+', resp.text).group()
            globalRepeatSubmitToken = re.sub(r'(globalRepeatSubmitToken)|(=)|(\s)|(;)|(\')', '', a1)

            b1 = re.search(r'key_check_isChange.+', resp.text).group().split(',')[0]
            key_check_isChange = re.sub(r'(key_check_isChange)|(\')|(:)', '', b1)

            return globalRepeatSubmitToken, key_check_isChange

    def get_passenger(self, repeat_submit_token):
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
        resp = self.req.post(url, data=data, headers=self.header)
        if resp.status_code == requests.codes.ok:
            print(resp.text)

    def check_order_info(self, repeat_submit_token):
        """
        再次检查订单
        :param repeat_submit_token:
        :return:
        """

        print("检查订单信息")
        data = {
            "cancel_flag": "2",
            "bed_level_order_num": "000000000000000000000000000000",
            "passengerTicketStr": PASSENGER_TICKET_STR,
            "oldPassengerStr": OLD_PASSENGER_STR,
            "tour_flag": "dc",
            "randCode": "",
            "whatsSelect": "1",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": repeat_submit_token
        }
        url = "https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo"
        resp = self.req.post(url, data=data, headers=self.header)
        if resp.status_code == requests.codes.ok:
            print(resp.text)
            if '"submitStatus":true' in resp.text:
                return True
        return False

    def tranceDate(self, param):
        """
        将传递的字符串转化为时间
        :param param: 时间： 2018-08-28
        :return: Fri Dec 29 2017 00:00:00 GMT+0800 (中国标准时间)
        """
        tmp = time.strftime('%a %b %d %Y 00:00:00 %z', time.strptime(param, '%Y-%m-%d')).split('+')
        # ts = time.mktime(time.strptime(param, "%Y-%m-%d"))
        # s = time.ctime(ts)
        # t1 = s[0:11] + s[20:] + " 00:00:00 GMT+0800 (中国标准时间)"
        return tmp[0] + 'GMT+' + tmp[1] + ' (中国标准时间)'

    def getQueueCount(self, trick_data, REPEAT_SUBMIT_TOKEN, query_date):
        """
            判断是都有余票
        :param REPEAT_SUBMIT_TOKEN:
        :return:
        """
        print("检查余票...")
        url = "https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount"
        # 将字符串转化为需要的时间
        train_date = self.tranceDate(query_date)
        print("leftTicket: ", end=" ")
        print(trick_data[train_no][12])
        data = {
            # 时间
            "train_date": train_date,
            # 车次编号
            "train_no": trick_data[train_no][2],
            # 火车代码
            "stationTrainCode": trick_data[train_no][3],
            # 座位类型 1：硬座 3：硬卧
            "seatType": 1,
            # 出发点，终止地址
            "fromStationTelecode": trick_data[train_no][6],
            "toStationTelecode": trick_data[train_no][7],
            "leftTicket": trick_data[train_no][12],
            "purpose_codes": "00",
            "train_location": trick_data[train_no][15],
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
        }
        print(data)
        resp = self.req.post(url, data=data, headers=self.header)
        if resp.status_code == requests.codes.ok:
            # 有余票，返回值将会是True
            print(resp.text)

    def confirm_single(self, REPEAT_SUBMIT_TOKEN, key_check_isChange, trick_data):
        """
        真正的提交订单
        最后一次确认订单
        :return: 返回购票结果
        """
        print("最后一次确认订单")
        url = "https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue"

        print("leftTicket: ", end=" ")
        print(trick_data[train_no][12])
        data = {
            "passengerTicketStr": PASSENGER_TICKET_STR,
            "oldPassengerStr": OLD_PASSENGER_STR,
            "randCode": "",
            "purpose_codes": "00",
            "key_check_isChange": key_check_isChange,
            "leftTicketStr": trick_data[train_no][12],
            "train_location": trick_data[train_no][15],
            "choose_seats": "",
            "seatDetailType": "000",
            "whatsSelect": "1",
            "roomType": "00",
            "dwAll": "N",
            "_json_att": "",
            "REPEAT_SUBMIT_TOKEN": REPEAT_SUBMIT_TOKEN
        }
        print(data)
        resp = self.req.post(url, data=data, headers=self.header)
        if resp.status_code == requests.codes.ok:
            print(resp.text)
            # 返回购票结果
            return resp.json()['data']['submitStatus']

    def query_order_wait_time(self, submit_token):
        query_url = "https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime"

        order_id = None
        while order_id is None:
            t = datetime.datetime.now()
            d = t - t.utcfromtimestamp(0)
            now_time = d.days * 24 * 60 * 60 * 1000 + d.seconds * 1000 + d.microseconds
            data = {
                "random": now_time,
                "tourFlag": "dc",
                "_json_att": "",
                "REPEAT_SUBMIT_TOKEN": submit_token
            }
            resp = self.req.post(query_url, data=data, headers=self.header)
            print(resp.text)
            resp_data = resp.json()['data']
            order_id = resp_data['orderId']
            time.sleep(4)
        return True

    def buy_ticket(self, is_auto_buy):
        # 首先登录（包括验证码识别）
        lp = LoginProcess(self.req, self.header)
        login_result = lp.login()
        res = login_result.json()
        if res["result_code"] == 0:
            # 阶段一：验证是否登录状态
            self.check_uamauthclient()
            # 阶段二：进行车票确认
            # 初始化购票页面
            self.init_buy_page()
            print("查询车票数据: 出发地:{},目的地:{},出发日期:{}".format(from_station, to_station, date))
            while is_auto_buy:
                # 查询票
                qt = QueryTrain(requests.session(), headers)
                query_ticket_data = qt.query_train(from_station, to_station, date)
                print("打印车次信息：")
                qt.trans_print_data(query_ticket_data)
                ticket_dict_data = qt.get_train_dict(query_ticket_data)
                # 检查用户是否登录
                self.check_user()
                # 初始化订单
                order_check_result = self.submit_order_request(ticket_dict_data)
                # 说明订单成功，需要确认订单即可
                if order_check_result:
                    # 初始化订单数据,获取到REPEAT_SUBMIT_TOKEN,key_check_isChange,leftTicketStr
                    REPEAT_SUBMIT_TOKEN, key_check_isChange = self.initDc()
                    # 检查订单信息
                    print("得到校验uuid:", REPEAT_SUBMIT_TOKEN)
                    # 获取该用户下的乘车人信息
                    self.get_passenger(REPEAT_SUBMIT_TOKEN)
                    # 进行订单确认
                    check_order_result = self.check_order_info(REPEAT_SUBMIT_TOKEN)
                    if check_order_result:
                        # 订单检查成功，尽心确认订单
                        # 查询订单队列余票
                        self.getQueueCount(ticket_dict_data, REPEAT_SUBMIT_TOKEN, date)
                        # 休眠5秒，防止太快导致一直排队
                        time.sleep(5)
                        # 最后一次确认订单
                        ok = self.confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, ticket_dict_data)
                        if ok:
                            if self.query_order_wait_time(REPEAT_SUBMIT_TOKEN):
                                print("购票成功,退出程序!")
                                exit(0)
                        else:
                            # 休眠5秒钟，防止被防刷票封ip
                            time.sleep(5)
        else:
            print("登录失败！")


if __name__ == "__main__":

    req = requests.session()
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }

    bt = BuyTicket(req, headers)
    bt.buy_ticket(IS_AUTO_BUY)
    # st = "I7Av2ueNwCq5Oa0qYaI2dmr6xUjBZW1F6q5qIFe7ejYbu7oou%2FGwVX72khI%3D"
    # print(parse.quote(parse.unquote(st)))
    # 首先登录（包括验证码识别）
    # lp = LoginProcess(req, headers)
    # login_result = lp.login()
    # res = login_result.json()
    # bt.cookies = login_result.headers['set-cookie']
    # if res["result_code"] == 0:
    #     # 阶段一：验证是否登录状态
    #     bt.check_uamauthclient()
    #     # 阶段二：进行车票确认
    #     # 初始化购票页面
    #     bt.init_buy_page()
    #     print("查询车票数据: 出发地:{},目的地:{},出发日期:{}".format(from_station, to_station, date))
    #     while IS_AUTO_BUY:
    #         # 查询票
    #         qt = QueryTrain(requests.session(), headers)
    #         query_ticket_data = qt.query_train(from_station, to_station, date)
    #         print("打印车次信息：")
    #         qt.trans_print_data(query_ticket_data)
    #         ticket_dict_data = qt.get_train_dict(query_ticket_data)
    #         # 检查用户是否登录
    #         bt.check_user()
    #         # 初始化订单
    #         order_check_result = bt.submit_order_request(ticket_dict_data)
    #         # 说明订单成功，需要确认订单即可
    #         if order_check_result:
    #             # 初始化订单数据,获取到REPEAT_SUBMIT_TOKEN,key_check_isChange,leftTicketStr
    #             REPEAT_SUBMIT_TOKEN, key_check_isChange = bt.initDc()
    #             # 检查订单信息
    #             print("得到校验uuid:", REPEAT_SUBMIT_TOKEN)
    #             # 获取该用户下的乘车人信息
    #             bt.get_passenger(REPEAT_SUBMIT_TOKEN)
    #             # 进行订单确认
    #             check_order_result = bt.check_order_info(REPEAT_SUBMIT_TOKEN)
    #             if check_order_result:
    #                 # 订单检查成功，尽心确认订单
    #                 # 查询订单队列余票
    #                 bt.getQueueCount(ticket_dict_data, REPEAT_SUBMIT_TOKEN, date)
    #                 # 最后一次确认订单
    #                 ok = bt.confirm_single(REPEAT_SUBMIT_TOKEN, key_check_isChange, ticket_dict_data)
    #                 if ok:
    #                     print("购票成功,退出程序!")
    #                     exit(0)
    #                 else:
    #                     # 休眠5秒钟，防止被防刷票封ip
    #                     time.sleep(5)
    # else:
    #     print("登录失败！")
