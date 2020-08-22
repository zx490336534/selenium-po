# -*- coding: utf-8 -*-
# @Time    : 2020/8/22 10:07 上午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : baiduaction.py
import time
from selenium_po.elementoperator import ElementOperator


class BaiDuAction(ElementOperator):
    def __init__(self, path="/Users/zhongxin/PycharmProjects/selenium-po/selenium_po/tests/pages.yaml",
                 file_name='index', driver=None):
        super(BaiDuAction, self).__init__(path, file_name, driver)

    def input(self, msg):
        self.find_element(self.kw).clear()
        self.find_element(self.kw).send_keys(msg)

    def search(self):
        self.find_element(self.su).click()


if __name__ == '__main__':
    baidu = BaiDuAction()
    baidu.open('http://www.baidu.com', baidu.kw)
    time.sleep(2)
    baidu.input("python")
    baidu.search()
    baidu.screenshot_pic("1.png")
    baidu.close()
