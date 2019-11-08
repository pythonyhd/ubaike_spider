# -*- coding: utf-8 -*-
# @Time    : 2019/9/23 17:40
# @Author  : Yasaka.Yu
# @File    : main.py
from scrapy.cmdline import execute
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

execute("scrapy crawl ubaike".split())  # 红盾网