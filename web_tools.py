import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver import ActionChains
import re, random
import json


class WebTools(object):
    def __init__(self, url: str, cookies: str or list = None):
        self.driver = webdriver.Chrome()
        self.driver.get(url)
        self.driver.maximize_window()
        self.driver.implicitly_wait(20)
        if cookies is not None:
            if type(cookies) == str:
                with open(cookies, "r", encoding="utf8") as cookies_file:
                    cookies_data = json.loads(cookies_file.read())
                for cookie in cookies_data:
                    self.driver.add_cookie(cookie)
                self.driver.get(url)
            elif type(cookies) == list:
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                self.driver.get(url)
            else:
                raise TypeError
        self._waite = WebDriverWait(self.driver, 10, 0.5)
        self.action = ActionChains(self.driver)

    def _choice_method(self, method: str):
        all_method = {
            "id": By.ID,
            "class": By.CLASS_NAME,
            "css": By.CSS_SELECTOR,
            "link_text": By.LINK_TEXT,
            "name": By.NAME,
            "tag_name": By.TAG_NAME,
            "xpath": By.XPATH
        }
        return all_method.get(method)

    def _find_element(self, data: list):
        if data[0] in ["xpath", "tag_name", "link_text"]:
            return self.driver.find_element(self._choice_method(data[0]), data[1])
        else:
            elements = self.driver.find_elements(self._choice_method(data[0]), data[1])
            if len(elements) > 1:
                return elements
            elif len(elements) == 1:
                return elements[0]

    def process_data(self, data: str):
        if re.match("([\u4e00-\u9fa5]*)", data).group() != "":
            new_data = ["link_text", data]
        elif re.match("[a-z]*=", data) is None:
            new_data = ["xpath", data]
        else:
            new_data = data.split("=")
            if (new_data[0] == "class") and (" " in new_data[1]):
                new_data[0] = "css"
                new_data[1] = re.sub(" |\"", ".", new_data[1]).rstrip(".")
            else:
                new_data[1] = new_data[1].strip("\"")
        return self._find_element(new_data)

    def click_element(self, data, tag: str = None):
        self.wait_until_element_displayed(data)
        self._assertion_and_click(self.process_data(data), tag)

    def close_driver(self):
        self.driver.close()

    def move_element(self, element1, element2):
        self.action.drag_and_drop(element1, element2).perform()

    def change_page(self, url: str):
        self.driver.get(url)

    def change_user(self, cookies: str or list):
        self.driver.delete_all_cookies()
        if type(cookies) == str:
            with open(cookies, "r", encoding="utf8") as cookies_file:
                cookies_data = json.loads(cookies_file.read())
            for cookie in cookies_data:
                self.driver.add_cookie(cookie)
        elif type(cookies) == list:
            for cookie in cookies:
                self.driver.add_cookie(cookie)

    def get_url(self):
        url = self.driver.current_url
        return url

    def find_element_in_list(self, data: str, target: str):
        target_list = self.process_data(data)
        count = 0
        for i in target_list:
            if target in i.text:
                return count, target_list
            else:
                count += 1

    def wait_until(self, method):
        self._waite.until(method=method)

    def wait_until_element_displayed(self, data: str):
        target = self.process_data(data)
        if type(target) == list:
            target = target[0]
        return self._waite.until(lambda display: target.is_displayed())

    def _assertion_and_click(self, data, tag_str: str = None):
        if type(data) == list:
            for i in data:
                if i.text == tag_str:
                    i.click()
                    print("clicked " + i.text, end=", ")
                    break
        else:
            if tag_str is not None:
                assert data.text == tag_str
                print("clicked " + data.text, end=", ")
            data.click()
