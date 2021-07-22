#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author   : zhongxin
# @Time     : 2021/7/22 10:38
# @File     : lemonaction.py
# @Project  : selenium-po
# @Desc     :
import os

from selenium_po.elementoperator import ElementOperator

path = os.path.dirname(os.path.abspath(__file__))


class LemonAction(ElementOperator):
    def __init__(self, path=f"{path}/pages.yaml", file_name='lemon', driver=None):
        super(LemonAction, self).__init__(path, file_name, driver)
        self.url = 'http://127.0.0.1:4723/wd/hub'


if __name__ == '__main__':
    desired_caps = {
        'platformName': 'Android',
        'deviceName': '127.0.0.1:62001',
        'appPackage': 'com.lemon.lemonban',
        'appActivity': 'com.lemon.lemonban.activity.WelcomeActivity'
    }
    lemon = LemonAction()
    lemon.open(lemon.url, lemon.employment_info, driver="Android", desired_caps=desired_caps)
    lemon.screenshot_pic("l_1.png")
    lemon.click(lemon.employment_info)
    lemon.screenshot_pic("l_2.png")
    lemon.close()
