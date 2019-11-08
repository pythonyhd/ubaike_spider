# -*- coding: utf-8 -*-
# @Time    : 2019/9/25 11:33
# @Author  : Yasaka.Yu
# @File    : test_yj.py
import pytest
from selenium import webdriver


class TestBaidu:
    @pytest.yield_fixture(autouse=True)
    def classSetUp(self):
        """
        所有的测试用例都可以复用，yield_fixture，既可以准备也可以完成自动清理，不加yield只有准备
        :return:
        """
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        yield
        self.driver.quit()

    def test_title(self):
        self.driver.get("https://www.baidu.com")
        assert "百度一下" in self.driver.title

    def test_login(self):
        pass


# pytest -v -s test_yj.py