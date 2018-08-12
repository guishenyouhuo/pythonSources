#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-8 22:53
# @Author  : wangfei
# @File    : query_train.py

import requests
import urllib3
from station_code.stations import stations
from prettytable import PrettyTable
from colorama import Fore
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
__author__ = "wangfei"


class QueryTrain(object):
    def __init__(self, req, headers):
        self.req = req
        self.headers = headers

    def query_train(self, from_station, to_station, date):
        from_station = stations.get(from_station)
        to_station = stations.get(to_station)
        date = date
        query_url = 'https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date={}&leftTicketDTO.from_station={}&leftTicketDTO.to_station={}&purpose_codes=ADULT'.format(
            date, from_station, to_station)
        try:
            response = self.req.get(query_url, headers=self.headers, verify=False)
            response.encoding = "utf-8"
            # print(response.text)
            # 得到我们需要的数据
            return response.json()['data']['result']
        except Exception:
            print("查询车次异常，请稍后重试！")

    def get_train_dict(self, train_data):
        availabel_trains = [i.split('|') for i in train_data]
        trains_dict = {}
        for train in availabel_trains:
            trains_dict[train[3]] = train
        return trains_dict

    def trans_print_data(self, orgi_data):
        """
        格式化并输出数据
        :param orgi_data:
        :return:
        """
        query_train_data = [i.split('|') for i in orgi_data]
        pt = PrettyTable()
        pt._set_field_names(u"车次 车站 时间 历时 特等座 一等座 二等座 高级软卧 软卧 动卧 硬卧 软座 硬座 无座 备注".split())
        pt.padding_width = 1
        pt.align["车次"] = "l"
        pt.right_padding_width = 1

        # 翻转字典station
        stations_re = dict(zip(stations.values(), stations.keys()))

        # 循环添加每一行
        for train in query_train_data:
            train_no = train[3]
            from_station_code = train[6]
            to_station_code = train[7]
            start_time = train[8]
            arrive_time = train[9]
            time_duration = train[10]
            super_class_seat = train[25] or "--"
            first_class_seat = train[31] or "--"
            second_class_seat = train[30] or "--"
            vip_soft_sleep = train[21] or "--"
            soft_sleep = train[23] or "--"
            quick_sleep = train[33] or "--"
            hard_sleep = train[28] or "--"
            soft_seat = train[24] or "--"
            hard_seat = train[29] or "--"
            no_seat = train[26] or "--"
            mark = train[1] or "--"
            pt.add_row([
                train_no,
                '\n'.join([Fore.GREEN + stations_re.get(from_station_code) + Fore.RESET,
                           Fore.RED + stations_re.get(to_station_code) + Fore.RESET]),
                '\n'.join([Fore.GREEN + start_time + Fore.RESET, Fore.RED + arrive_time + Fore.RESET]),
                time_duration, super_class_seat, first_class_seat, second_class_seat, vip_soft_sleep,
                soft_sleep, quick_sleep, hard_sleep, soft_seat, hard_seat, no_seat, mark
            ])

        print(pt)


if __name__ == "__main__":
    headers = {
        "User-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
    }
    # 输入目的地，结束地，开始时间
    print("请输入出发地，目的地，出发日期，使用空格隔开")
    #query_input_data = input()
    query_input_data = '北京 武汉 2018-08-26'
    sp = query_input_data.split(" ")
    print("输入结果: 出发地:{},目的地:{},出发日期:{}".format(sp[0], sp[1], sp[2]))
    # 查询票
    qt = QueryTrain(requests.session(), headers)
    query_ticket_data = qt.query_train(sp[0], sp[1], sp[2])
    print("输出车次数据")
    # print(query_input_data)
    qt.trans_print_data(query_ticket_data)
