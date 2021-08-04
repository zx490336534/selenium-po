# -*- coding: utf-8 -*-
# @Time    : 2020/8/22 9:28 上午
# @Author  : zhongxin
# @Email   : 490336534@qq.com
# @File    : elementoperator.py
import base64
import os
import random
import socket
import time

import yaml
from PIL import Image
from appium.webdriver.common.mobileby import MobileBy
from selenium import webdriver
from appium import webdriver as app_webdriver
from selenium.common.exceptions import WebDriverException, NoSuchElementException
from selenium.webdriver import DesiredCapabilities, ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
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
        self.url = '/'
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
                wait_sec = int(locator.get("timeout", 3))
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
                        chrome_option.add_experimental_option('w3c', False)
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

    def input(self, locator, msg, many=False, num=0):
        if many:
            ele = self.find_elements(locator)[num]
        else:
            ele = self.find_element(locator)
        print(f"往「{locator.desc}」输入「{msg}」")
        ele.clear()
        time.sleep(0.2)
        ele.send_keys(msg)
        time.sleep(0.2)

    def send_keys(self, locator, key):
        """

        :param locator: 元素对象
        :param key:
            * BACK_SPACE 后退
            * SPACE 空格
            * ENTER 回车
        :return:
        """
        ele = self.find_element(locator)
        ele.send_keys(getattr(Keys, key.upper()))
        time.sleep(0.2)

    def click(self, locator, many=False, num=0):
        if many:
            ele = self.find_elements(locator)[num]
        else:
            ele = self.find_element(locator)
        print(f"点击「{locator.desc}」")
        ele.click()
        time.sleep(0.2)

    def get_text(self, locator, many=False, num=0):
        if many:
            ele = self.find_elements(locator)[num]
        else:
            ele = self.find_element(locator)
        print(f"获取「{locator.desc}」")
        return ele.text

    def refresh(self):
        """
        刷新页面
        :return:
        """
        self.driver.refresh()
        time.sleep(1)

    def scroll_to(self, num):
        """
        下拉至一定位置
        :param num:下拉的位置
        :return:
        """
        js = f'window.scrollTo(0,{100 * num})'
        self.driver.execute_script(js)

    def back(self):
        """
        返回上一页
        :return:
        """
        self.driver.back()

    def forward(self):
        """
        返回下一页
        :return:
        """
        self.driver.forward()

    def get_cookies(self):
        """
        获取cookies
        :return:
        """
        cookies = self.driver.get_cookies()
        return cookies

    def add_cookie(self, cookie_dict):
        """
        添加cookie
        :return:
        """
        self.driver.add_cookie(cookie_dict)

    def delete_all_cookies(self):
        """
        清除全部cookie
        :return:
        """
        self.driver.delete_all_cookies()

    def join_url(self, base_url, url):
        if not base_url.endswith('/'):
            base_url += '/'
        if url.startswith('/'):
            url.replace('/', '', 1)
        return base_url + url

    def open_url(self, url):
        self.driver.get(url)

    def add_attribute(self, locator, attributeName, value):
        """
        向页面标签添加新属性
        """
        ele = self.find_element(locator)
        js = "arguments[0].%s=arguments[1]" % attributeName
        self.driver.execute_script(js, ele, value)

    def set_attribute(self, locator, attributeName, value):
        """
        设置页面对象的属性值
        """
        ele = self.find_element(locator)
        js = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(js, ele, attributeName, value)

    def get_attribute(self, locator, attributeName):
        """
        获取页面对象的属性值
        """
        ele = self.find_element(locator)
        return ele.get_attribute(attributeName)

    def remove_attribute(self, locator, attributeName):
        """
        删除页面属性
        """
        ele = self.find_element(locator)
        js = "arguments[0].removeAttribute(arguments[1])"
        self.driver.execute_script(js, ele, attributeName)

    def alert_sleep(self, t, msg=None):
        if not msg:
            msg = f'等待{t}秒'
        self.driver.execute_script(f"window.alert('{msg}');")
        time.sleep(t)
        try:
            alert = self.driver.switch_to.alert
            alert.accept()
        except Exception:
            pass


class AccessCode(object):
    """
    极验操作
    """

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 20)
        self.border = 6

    def save_img(self, img_name, class_name):
        """

        :param img_name: 保存图片的名字
        :param class_name: 需要保存的canvas的className
        :return:
        """
        getImgJS = 'return document.getElementsByClassName("' + class_name + '")[0].toDataURL("image/png");'
        img = self.driver.execute_script(getImgJS)
        base64_data_img = img[img.find(',') + 1:]
        image_base = base64.b64decode(base64_data_img)
        file = open(img_name, 'wb')
        file.write(image_base)
        file.close()

    def get_track(self, distance):
        """
        根据偏移量获取移动轨迹
        :param distance: 偏移量
        :return: 移动轨迹
        """
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        mid = distance * 4 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0
        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
            else:
                # 加速度为负3
                a = -3
            # 初速度v0
            v0 = v
            # 当前速度v = v0 + at
            v = v0 + a * t
            # 移动距离x = v0t + 1/2 * a * t^2
            move = v0 * t + 1 / 2 * a * t * t
            # 当前位移
            current += move
            # 加入轨迹
            track.append(round(move))
        return track

    def move_to_gap(self, slider, track):
        """
        拖动滑块到缺口处
        :param slider: 滑块
        :param track: 轨迹
        :return:
        """
        ActionChains(self.driver).click_and_hold(slider).perform()
        for x in track:
            ActionChains(self.driver).move_by_offset(xoffset=x, yoffset=0).perform()
            time.sleep(0.1 * random.random())
        ActionChains(self.driver).release().perform()

    def get_slider(self):
        """
        获取滑块
        :return: 滑块对象
        """
        slider = self.wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, 'geetest_slider_button')))
        return slider

    def is_similar_color(self, x_pixel, y_pixel):
        """
        判断颜色是否相近
        :param x_pixel:
        :param y_pixel:
        :return:
        """
        for i, pixel in enumerate(x_pixel):
            if abs(y_pixel[i] - pixel) > 50:
                return False
        return True

    def get_offset_distance(self, cut_image, full_image):
        """
        计算距离
        :param cut_image:
        :param full_image:
        :return:
        """
        for x in range(cut_image.width):
            for y in range(cut_image.height):
                cpx = cut_image.getpixel((x, y))
                fpx = full_image.getpixel((x, y))
                if not self.is_similar_color(cpx, fpx):
                    img = cut_image.crop((x, y, x + 50, y + 40))
                    # 保存一下计算出来位置图片，看看是不是缺口部分
                    img.save('gap.png')
                    return x

    def crack(self):
        """
        验证操作
        :return:
        """
        full_path = 'full.jpg'
        cut_path = '{cut.jpg'
        # 保存原始图片
        self.save_img(full_path, 'geetest_canvas_fullbg')
        # 保存缺口图片
        self.save_img(cut_path, 'geetest_canvas_bg')
        full_image = Image.open(full_path)
        cut_image = Image.open(cut_path)
        # 计算滑动距离
        distance = self.get_offset_distance(cut_image, full_image)
        # 减去缺口位移
        distance -= self.border
        # 获取滑块对象
        slider = self.get_slider()
        # 模拟人为滑动轨迹
        track = self.get_track(distance)
        # 拖动滑块
        self.move_to_gap(slider, track)
        time.sleep(2)
        try:
            track = self.get_track(distance - 65)
            self.move_to_gap(slider, track)
        except Exception:
            pass
