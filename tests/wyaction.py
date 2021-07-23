# -*- coding: utf-8 -*-
# @Time    : 2021/7/23 10:42 下午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : wyaction.py.py
import os
import time

from selenium_po.elementoperator import ElementOperator

path = os.path.dirname(os.path.abspath(__file__))


class WYAction(ElementOperator):
    def __init__(self, path=f"{path}/pages.yaml", file_name='wy', driver=None):
        super(WYAction, self).__init__(path, file_name, driver)
        self.url = 'https://wy.guahao.com/'


if __name__ == '__main__':
    wy = WYAction()
    wy.open(wy.url, wy.wrap, driver='chrome-h5')
    wy.screenshot_pic("wy_1.png")
    wy.click(wy.wrap)
    wy.screenshot_pic("wy_2.png")
    time.sleep(5)
    wy.screenshot_pic("wy_3.png")
    wy.close()
