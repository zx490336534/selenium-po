# -*- coding: utf-8 -*-
# @Time    : 2020/8/22 9:28 上午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : elementoperator.py
import os
import socket
import time

import yaml
from appium.webdriver.common.mobileby import MobileBy
from selenium import webdriver
from appium import webdriver as app_webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class Locator:
    def __init__(self, element, wait_sec=3, by_type='id', locator_name='', desc=''):
        self.element = element
        self.wait_sec = wait_sec
        self.by_type = by_type
        self.locator_name = locator_name
        self.desc = desc

    def __str__(self):
        return f'{self.desc}:(By{self.by_type},element:{self.element})'


class ElementOperator:
    def __init__(self, path=None, file_name=None, driver=None):
        """

        :param path: 元素定位yaml文件
        :param file_name: 页面名
        :param driver: 浏览器对象
        """
        self.driver = driver
        self.time_out = 10
        self.path = path
        self.file_name = file_name or os.path.split(path)[-1]
        self.data_dict = self._parse_yaml()
        self._locator_map = self.read_yaml()

    def _parse_yaml(self):
        """
        读取Yaml文件内容
        :return:
        """
        data_dict = {}
        try:
            with open(self.path, 'r+', encoding='utf-8') as f:
                data_dict = yaml.load(f, Loader=yaml.FullLoader) or {}
        except Exception as e:
            raise Exception(e)
        finally:
            return data_dict

    def read_yaml(self):
        """
        页面元素定位
        :return:
        """
        pages_list = self.data_dict["pages"]
        locator_map = dict()
        for page in pages_list:
            page_name = page["page"]["pageName"]
            page_desc = page["page"]["desc"]
            locator_map[page_name] = dict()
            locators_list = page["page"]["locators"]
            for locator in locators_list:
                by_type = locator["type"]
                element = locator["value"]
                wait_sec = int(locator["timeout"])
                locator_name = locator["name"]
                desc = f"{page_desc}_{locator['desc']}"
                tmp = Locator(element, wait_sec, by_type, locator_name, desc)
                locator_map[page_name][locator_name] = tmp
        return locator_map

    def __getattr__(self, item):
        if item in self._locator_map[self.file_name]:
            locator = self.get_locator(item)
            if locator:
                return locator
            else:
                return self[item]

    def open(self, url, locator, frame_locator=None, driver='chrome', desired_caps=None, deviceName='iPhone X'):
        """

        :param url: 打开的地址
        :param locator: 确认打开成功的元素
        :param frame_locator: 需要切换的frame
        :param driver: 浏览器驱动
        :param desired_caps: appium连接信息
        :param deviceName: h5测试设备型号
        :return:
        """
        flag = False
        driver = driver.lower()
        if driver in ['chrome', 'ie', 'chrome-h5']:
            try:
                socket.setdefaulttimeout(50)
                if not self.driver:
                    if driver == 'chrome':
                        chrome_option = Options()
                        # chrome_option.add_argument('--headless')
                        self.driver = webdriver.Chrome(chrome_options=chrome_option)
                    elif driver == 'chrome-h5':
                        chrome_option = Options()
                        chrome_option.add_experimental_option('mobileEmulation', {'deviceName': deviceName})
                        self.driver = webdriver.Chrome(chrome_options=chrome_option)
                    elif driver == 'ie':
                        ie_options = DesiredCapabilities.INTERNETEXPLORER  # 将忽略IE保护模式的参数设置为True
                        ie_options['ignoreProtectedModeSettings'] = True  # 忽略浏览器缩放设置
                        ie_options['ignoreZoomSetting'] = True  # 启动带有自定义设置的IE浏览器
                        self.driver = webdriver.Ie(capabilities=ie_options)
                self.driver.get(url)
                try:
                    self.driver.maximize_window()
                except Exception as e:
                    print(f"浏览器最大化失败:{e}")
                if frame_locator:
                    self.wait_element_visible(frame_locator)
                    self.switch_frame(frame_locator)
                self.wait_element_visible(locator)
                flag = True
            except Exception as e:
                raise Exception(e)
            if not flag:
                raise WebDriverException(f"打开浏览器进入{url}失败")
        else:
            if driver == 'android':
                # url = 'http://127.0.0.1:4723/wd/hub'
                self.driver = app_webdriver.Remote(url, desired_caps)
        self.wait_for(10)
        return self.driver

    def close(self):
        if self.driver:
            try:
                self.driver.close()
            except Exception as e:
                print(f"close浏览器失败：{e}")
            try:
                self.driver.quit()
            except Exception as e:
                print(f"quit浏览器失败：{e}")
            finally:
                self.driver = None

    def get_locator(self, locator_name):
        locator = self._locator_map.get(self.file_name)
        if locator:
            locator = locator.get(locator_name)
        return locator

    def wait_for(self, wait_sec):
        self.driver.implicitly_wait(wait_sec)

    def _wait_page_load(self):
        try:
            WebDriverWait(self.driver, self.time_out).until(lambda d: d.execute_script("return document.readyState"))
        except Exception as e:
            raise Exception(e)

    def wait_element_visible(self, locator):
        """
        检查元素是否存在
        :param locator:
        :return:
        """
        locator = self._get_locator_tuple(locator)
        ele = WebDriverWait(self.driver, self.time_out).until(
            expected_conditions.visibility_of_element_located(locator))
        return ele

    @staticmethod
    def _get_locator_tuple(locator):
        type_dict = {
            "id": By.ID,
            "xpath": By.XPATH,
            "link_text": By.LINK_TEXT,
            "partial_link_text": By.PARTIAL_LINK_TEXT,
            "name": By.NAME,
            "tag_name": By.TAG_NAME,
            "class_name": By.CLASS_NAME,
            "css_selector": By.CSS_SELECTOR,
            "ios_predicate": MobileBy.IOS_PREDICATE,
            "ios_uiautomation": MobileBy.IOS_UIAUTOMATION,
            "ios_class_chain": MobileBy.IOS_CLASS_CHAIN,
            "android_uiautomator": MobileBy.ANDROID_UIAUTOMATOR,
            "android_viewtag": MobileBy.ANDROID_VIEWTAG,
            "android_data_matcher": MobileBy.ANDROID_DATA_MATCHER,
            "android_view_matcher": MobileBy.ANDROID_VIEW_MATCHER,
            "windows_ui_automation": MobileBy.WINDOWS_UI_AUTOMATION,
            "accessibility_id": MobileBy.ACCESSIBILITY_ID,
            "image": MobileBy.IMAGE,
            "custom": MobileBy.CUSTOM,
        }
        locator_t = (type_dict[locator.by_type], locator.element)
        return locator_t

    def switch_frame(self, frame_locator):
        self.driver.switch_to.default_content()
        self.driver.switch_to.frame(frame_locator.element)

    def find_element(self, locator):
        self.wait_for(locator.wait_sec)
        web_ele = self._get_element(locator)
        return web_ele

    def find_elements(self, locator):
        self.wait_for(locator.wait_sec)
        web_eles = self._get_elements(locator)
        return web_eles

    def height_light(self, element):
        """
        元素高亮
        :param element:
        :return:
        """
        self.driver.execute_script("arguments[0].setAttribute('style',arguments[1]);",
                                   element, "border:2px solid red;")

    def _get_element(self, locator):
        start_time = time.time()
        while True:
            try:
                value_text = locator.desc
            except:
                value_text = ""
            try:
                locator_t = self._get_locator_tuple(locator)
                web_element = self.driver.find_element(*locator_t)
                try:
                    self.height_light(web_element)
                except Exception:
                    pass
                return web_element
            except NoSuchElementException as n:
                time.sleep(0.5)
                if time.time() - start_time >= self.time_out:
                    raise NoSuchElementException(f"{self.time_out}秒后仍没有找到元素「{value_text}」:{n}")
            except WebDriverException as w:
                time.sleep(0.5)
                if time.time() - start_time >= self.time_out:
                    raise WebDriverException(f"{self.time_out}秒后浏览器仍异常「{value_text}」:{w}")
            except Exception as e:
                raise Exception(f"查找元素异常：{e}")

    def _get_elements(self, locator):
        locator_t = self._get_locator_tuple(locator)
        web_element = self.driver.find_elements(*locator_t)
        return web_element

    def screenshot_pic(self, file_name):
        self.driver.save_screenshot(file_name)
        return file_name

    def input(self, locator, msg):
        ele = self.find_element(locator)
        print(f"往「{locator.desc}」输入「{msg}」")
        ele.clear()
        ele.send_keys(msg)

    def click(self, locator):
        ele = self.find_element(locator)
        print(f"点击「{locator.desc}」")
        ele.click()
