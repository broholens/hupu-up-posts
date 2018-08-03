import time
from selenium import webdriver
from utils import save_cookies


class CookieGetter:
    """save cookie to json file"""
    def __init__(self, username, passwd):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        opts = webdriver.ChromeOptions()
        opts.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(chrome_options=opts)
        self.username = str(username)
        self.passwd = str(passwd)

    def login(self):
        self.driver.get('https://passport.hupu.com/pc/login')
        self.driver.find_element_by_id('J_username').send_keys(self.username)
        self.driver.find_element_by_id('J_pwd').send_keys(self.passwd)

    def wait_for_captcha(self):
        while self.driver.current_url != 'https://www.hupu.com/':
            time.sleep(3)

    def save_cookies(self):
        self.login()
        self.wait_for_captcha()
        save_cookies(self.driver, self.username)


if __name__ == '__main__':
    cookie_getter = CookieGetter('17121319220', 'aaaaa11111')
    cookie_getter.save_cookies()