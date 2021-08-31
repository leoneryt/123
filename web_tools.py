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


def get_random_string(name_len):
    loop = 0
    string = ""
    if string == "":
        base_str = 'abcdefghigklmnopqrstuvwxyz0123456789'
        while loop < name_len:
            string += "".join(random.choice(base_str))
            loop += 1
    return string


def create_flow(driver, name):
    print("create flow")

    target = 'class="ud__button ud__button--filled ud__button--filled-default ud__button--size-md page-home__header__create-btn"'
    driver.click_element(target, "创建工作流")

    target = driver.process_data('id="flowName"')
    target.click()
    time.sleep(0.5)
    target.send_keys(name)
    target = 'class="connector-picker-item__title"'
    driver.click_element(target, "网址触发器")
    target = 'class="lark-btn lark-btn-primary footer-button-submit"'
    driver.click_element(target, "保存")

    driver.wait_until_element_displayed('class="flow-node_content"')
    url = driver.get_url()

    print("create flow success,flow url:" + url)
    return url


def delete_flow(driver, delete_target: str):
    data_to_del = driver.find_element_in_list('class="flow-card__header-title"', delete_target)
    driver.process_data('class="ud__button ud__button--icon ud__button--icon-default ud__button--icon-size-sm flow-action-dropdown--icon"')[data_to_del[0]].click()
    data_to_del = driver.find_element_in_list('class="ud__menu-normal-item ud__menu-normal-item-only-child"', "删除")
    assert data_to_del[1][data_to_del[0]].text == "删除"
    data_to_del[1][data_to_del[0]].click()

    driver.wait_until(lambda display: driver.process_data('class="ud__confirm__title"').is_displayed())
    assert driver.process_data('class="ud__confirm__title"').text == "确定删除此工作流？"
    data_to_del = driver.find_element_in_list('class="ud__button ud__button--filled ud__button--filled-default ud__button--size-md"', "确定")
    assert data_to_del[1][data_to_del[0]].text == "确定"
    data_to_del[1][data_to_del[0]].click()

    driver.wait_until(lambda display: driver.process_data('class="ud__notice__description-content"').is_displayed())
    try:
        assert driver.process_data('class="ud__notice__description-content"').text == "删除成功"
    except Exception(delete_target + "删除失败") as err:
        print(err)


def delete_all_flow_with_tag(driver, tag):
    while True:
        driver.wait_until(lambda display: driver.process_data('class="flow-card__header-title"')[0].is_displayed())
        data_to_del = driver.find_element_in_list('class="flow-card__header-title"', tag)
        if data_to_del is not None:
            if len(data_to_del[1]) > 0:
                delete_flow(driver, tag)
                driver.driver.refresh()
                time.sleep(2)
        else:
            break


if __name__ == '__main__':
    # data = "class=\"lark-menu-submenu lark-menu-submenu-inline top-level\""
    # data = "开发者工具"
    # data = "//*[@id=\"6907567266540978178$Menu\"]/li[4]/div[1]/span"
    # data = "/html/body/script"
    a = WebTools("https://open.feishu.cn/document/ukTMukTMukTM/uITNz4iM1MjLyUzM")
    # a.process_data(data).click()
    # e = a.process_data(data)
    # print(len(e))
    # a = re.match("[a-z]*=", data)
    # print(a is None)
