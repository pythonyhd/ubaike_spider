# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 13:58
# @Author  : Yasaka.Yu
# @File    : unitest_demo.py
from selenium import webdriver
import unittest


class TestBaidu(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.implicitly_wait(5)
        # self.search = baidumodule(self.driver)  # 将driver传给aidumodule这个类
        self.driver.get('https://www.baidu.com')

    def tearDown(self) -> None:
        self.driver.close()

    def test_login(self):
        assert "百度一下" in self.driver.title

    def test_second(self):
        pass


if __name__ == '__main__':
    unittest.main()