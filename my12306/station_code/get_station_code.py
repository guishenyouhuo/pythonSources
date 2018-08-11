#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018-8-8 22:24
# @Author  : wangfei
# @File    : get_station_code.py

import requests
import re
from pprint import pprint


def get_station():
    station_url = "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js?station_version=1.9028"
    response = requests.get(station_url, verify=False)
    print(response.text)
    station = re.findall(u'([\u4e00-\u95fa5]+)\|([A-Z]+)', response.text)
    print(station)
    pprint(dict(station), indent=4)


if __name__ == "__main__":
    get_station()
