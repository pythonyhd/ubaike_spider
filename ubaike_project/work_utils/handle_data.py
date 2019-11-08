# -*- coding: utf-8 -*-
# @Time    : 2019/9/24 14:35
# @Author  : Yasaka.Yu
# @File    : handle_data.py
import re


def deal_with_data(data):
    if data:
        data = re.sub(r'[\r\n\t\s]', '', data)
        data = re.sub(r'[,：\:]', '', data)
        return data
    return None