import time
import json
import logging
from random import choice
# import arrow
from queue import Queue
from selenium import webdriver
from utils import save_cookies, send_mail
# from selenium.webdriver import Firefox
# from selenium.webdriver.firefox.options import Options


class HuPu:

    # 每人每天最多回复自己评论数
    max_comment_count = 300

    # 本日回帖数量
    comment_count = 0

    commentary = [
        '回收各种球鞋 aj 喷泡 椰子 实战 急用鞋换钱 闲置清理空间 全新二手皆可 打包优先 寻求多方合作 更多精彩尽在: clpro7',
        '朋友圈每日更新 各种秒价第一时间了解:clpro7',
        '最大限度发挥球鞋价值 接各种套现寄卖 全新二手都可以 加微信:clpro7 秒价实时更新',
        '加微信:clpro7 ',
        '接各种套现寄卖 全新二手都可以',
        '寻求多方合作',
        '回收各种球鞋',
        '急用鞋换钱 闲置清理空间 全新二手皆可'
    ]

    user_id = '131348617043133'

    start_at = 8

    end_with = 23

    post_count = 16

    def __init__(self, username):
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
        opts = webdriver.ChromeOptions()
        # opts.add_argument('headless')
        # opts.add_argument('no-sandbox')
        opts.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(chrome_options=opts)
        # opts = Options()
        # opts.add_argument('-headless')
        # profile = FirefoxProfile()
        # profile.set_preference("general.useragent.override", user_agent)
        # opts.add_argument(f'user-agent={user_agent}')
        # self.driver = Firefox(firefox_options=opts)
        # self.driver = Firefox('.geckodriver')
        self.driver.set_page_load_timeout(30)
        self.posts = Queue()
        self.max_error_num = 5
        self.error_counter = Queue(self.max_error_num)
        self.username = username
        self.config_log()
        self.load_cookies()

    def config_log(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s %(levelname)s %(message)s',
            datefmt='%d %b %Y %H:%M:%S',
            filename=self.username + '.log',
            filemode='w'
        )
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s %(levelname)s %(message)s',
            datefmt='%d %b %Y %H:%M:%S'
        )
        console.setFormatter(formatter)
        logging.getLogger('').addHandler(console)

    def get_posts_address(self):
        self.driver.get('https://www.hupu.com/')
        if not self.user_id:
            self.user_id = self.driver.find_element_by_id('g_m').get_attribute('iuid')
        return 'https://my.hupu.com/{}/topic'.format(self.user_id)

    def store_posts(self):
        posts_address = self.get_posts_address()
        self.request(posts_address)
        try:
            xp = '//table[@class="mytopic topiclisttr"]//a'
            links = self.driver.find_elements_by_xpath(xp)
            if self.post_count != 0:
                links = links[:self.post_count * 2]
            posts, plates = links[::2], links[1::2]
            posts = [
                post.get_attribute('href')
                for post, plate in zip(posts, plates)
                if plate.text in ['二手交易区']
            ]
            # deleted = [i.get('post_url') for i in DB.deleted.find()]
            # set无序 所以无序回帖
            for post in posts:  # set(posts).difference(set(deleted)):
                self.posts.put(post)
            logging.info('posts have been updated!')
        except:
            logging.error('update posts failed!')

    def request(self, url):
        try:
            self.driver.get(url)
            time.sleep(3)
            # update cookies
            save_cookies(self.driver, self.username)
        except:
            self.driver.execute_script('window.stop()')

    # def login(self):
    #     self.request('https://passport.hupu.com/pc/login')
    #     sleep_time = 8  # if third_party is 'qq' else 5
    #     # text = {'wechat': '微信登录', 'qq': 'QQ登录'}.get(third_party)
    #     try:
    #         self.driver.find_element_by_link_text('QQ登录').click()
    #         time.sleep(sleep_time)
    #         self.driver.get_screenshot_as_file('qrcode.png')
    #         logger.info('qrcode saved!')
    #     except:
    #         logger.error('二维码获取失败!')
    #         self.driver.close()

    def load_cookies(self):
        with open(self.username+'.json', 'r') as f:
            cookies = json.loads(f.read())
        self.driver.get('https://www.baidu.com/')
        self.driver.delete_all_cookies()
        for cookie in cookies:
            self.driver.add_cookie(cookie)

    # def is_logged_in(self):
    #     while True:
    #         if self.driver.current_url in 'https://www.hupu.com/':
    #             self.get_posts_address()
    #             break
    #         time.sleep(10)

    def comment_post(self, url, commentary):
        """添加评论"""
        try:
            self.request(url)
            self.driver.find_element_by_id('atc_content').send_keys(
                choice(commentary))
            self.driver.find_element_by_id('fastbtn').click()
            return True
        except:
            logging.error('find element error!')
        return False

    # def is_boundary(self):
    #     now = arrow.now()
    #     if now.hour >= self.end_with or \
    #             self.comment_count >= self.max_comment_count:
    #         logger.info('%s 正在休眠, 明天%s点再回帖', now, self.start_at)
    #         time.sleep((now.shift(days=1).replace(hour=self.start_at,
    #                                               minute=0) - now).seconds)
    #         self.comment_count = 0
    #     elif now.hour < self.start_at:
    #         logger.info('%s 正在休眠, %s点再回帖', now, self.start_at)
    #         time.sleep(
    #             (now.replace(hour=self.start_at, minute=0) - now).seconds)

    def comment_posts(self):
        # self.is_logged_in()
        while True:
            # self.is_boundary()

            while self.posts.empty():
                self.store_posts()
            post = self.posts.get()
            if self.comment_post(post, self.commentary) is False:
                continue
            time.sleep(30)

            current_url = 'post.php?action=reply'
            try:
                current_url = self.driver.current_url
            except:
                self.driver.execute_script('window.stop()')
            if current_url in 'https://bbs.hupu.com/post.php?action=reply':
                failed_reason = self.driver.find_element_by_xpath(
                    '//*[@id="search_main"]//span').text
                logging.error('%s %s!', failed_reason, post)
                if '银行总资产少于' in failed_reason:
                    logging.info('sending mail...')
                    send_mail(failed_reason)
                    exit(0)
                else:
                    if self.error_counter.full() is True:
                        logging.info('sending mail...')
                        send_mail(f'连续回帖{self.max_error_num}次出错')
                        exit(0)
                    self.error_counter.put(0)
            else:
                self.comment_count += 1
                logging.info('评论 %s 成功!　已评论: %s', post, self.comment_count)
                if self.error_counter.empty() is False:
                    self.error_counter.get()
            time.sleep(60 * 5)


if __name__ == '__main__':
    hupu = HuPu('17121319220')
    hupu.comment_posts()
