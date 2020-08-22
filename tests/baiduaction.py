# -*- coding: utf-8 -*-
# @Time    : 2020/8/22 10:07 上午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : baiduaction.py
import os
import time
from selenium_po.elementoperator import ElementOperator

path = os.path.dirname(os.path.abspath(__file__))


class BaiDuIndexAction(ElementOperator):
    def __init__(self, path=f"{path}/pages.yaml", file_name='index', driver=None):
        super(BaiDuIndexAction, self).__init__(path, file_name, driver)
        self.url = 'http://www.baidu.com'


if __name__ == '__main__':
    baidu = BaiDuIndexAction()
    baidu.open(baidu.url, baidu.index_input)
    baidu.input(baidu.index_input, "python")
    baidu.click(baidu.index_search)
    time.sleep(2)
    baidu.screenshot_pic("1.png")
    baidu.close()
