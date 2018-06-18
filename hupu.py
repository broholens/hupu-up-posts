import time
import logging
from random import choice, randrange
from itertools import cycle
from queue import Queue

import arrow
from requestium import Session

from report_exception import ExceptionReporter, send_mail

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s',
    datefmt='%d %b %Y %H:%M:%S',
)

logger = logging.getLogger('')

mail_uri = 'http://39.107.86.245:5000'
# def ensure_exception(unsure_statement, returns=False):
#     """
#     'window.stop()' does no effect to chromedriver
#     unsure_statement: str, selenium statement that may cause exception
#     returns: boolean, whether unsure statement returns value
#     """
#     try:
#         if returns is True:
#             return eval(unsure_statement)
#         eval(unsure_statement)
#     except:
#         pass


# def exception_reporter(exception_recoder, mail=None):
#     def exception_handler(func):
#         @wraps(func)
#         def func_handler(*args, **kwargs):
#             try:
#                 return func(*args, **kwargs)
#             except:
#                 recoder_num = len(exception_recoder)
#                 if recoder_num < 5:
#                     exception_recoder.append(time.time())
#                 else:
#                     if time.time() - exception_recoder[0] > 60*10:
#                         requests.post('http://39.107.86.245:5000', data=mail)
#                     else:
#                         exception_recoder.pop(0)
#         return func_handler
#     return exception_handler


user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'
s_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'Host': 'passport.hupu.com',
    'Origin': 'http://passport.hupu.com',
    'Referer': 'http://passport.hupu.com/pc/login?project=www&from=pc',
    'User-Agent': user_agent
}


class HuPu:

    commentaries = [
        '朋友圈每日更新 各种秒价第一时间了解:clpro7',
        '回收各种球鞋 aj 喷泡 椰子 实战 急用鞋换钱 闲置清理空间 全新二手皆可 打包优先 寻求多方合作 更多精彩尽在: clpro7',
        '最大限度发挥球鞋价值 接各种套现寄卖 全新二手都可以 加微信:clpro7 秒价实时更新'
    ]
    mail = {
        'recipient': 'zzwcng@126.com',
        'subject': 'HuPu',
        'content': '请重新登录 http://39.107.86.245:8080'
    }

    def __init__(self, comment_count=30, commentaries=None, start_at=8, end_with=23):
        self.s = Session(
            './chromedriver',
            'chrome',
            default_timeout=60,
            webdriver_options={'arguments': ['headless', 'disable-gpu', f'user-agent={user_agent}']}
        )
        self.s.headers.update(s_headers)
        self.comment_count = comment_count
        self.commentaries = commentaries
        self.start_at = start_at
        self.end_with = end_with
        self.posts = Queue()
        self.exception_recoder = []

    @ExceptionReporter
    def login(self, third_party):
        """
        third party can be vx or qq
        """
        third_parties = {'vx': 0, 'qq': 1}
        resp = self.s.get('https://passport.hupu.com/pc/login')
        qrcode_urls = resp.xpath('//div[@class="login-method"]/a/@data-href').extract()
        qrcode_url = qrcode_urls[third_parties.get(third_party)]
        if third_party == 'qq':
            qrcode_url = 'https://passport.hupu.com' + qrcode_url
        self.s.driver.get(qrcode_url)
        self.s.driver.get_screenshot_as_file('qrcode.png')
        logger.info('qrcode saved!')

    @ExceptionReporter
    def get_topic_url(self):
        """
        获取帖子主页链接
        """
        self.s.driver.get('https://www.hupu.com')
        iuid = self.s.driver.ensure_element_by_id('g_m').get_attribute('iuid')
        self.topic_url = f'https://my.hupu.com/{iuid}/topic'

    @ExceptionReporter
    def get_posts(self):
        """
        只评论二手交易区
        """
        logger.info('updating posts......')
        self.s.driver.get(self.topic_url)
        posts = self.s.driver.find_elements_by_xpath('//table[@class="mytopic topiclisttr"]//a')[:self.comment_count*2]
        links, plates = posts[::2], posts[1::2]
        for link, plate in zip(links, plates):
            if plate.text == '二手交易区':
                self.posts.put(link.get_attribute('href'))

    def up_post(self, post_url):
        """
        顶一条帖
        十条连续错误再发邮件报错
        """
        try:
            self.s.driver.get(post_url)
            self.s.driver.ensure_element_by_id('atc_content').send_keys(choice(self.commentaries))
            self.s.driver.ensure_element_by_id('fastbtn').ensure_click()
            time.sleep(randrange(60, 120))
            if 'post.php?action=reply' in self.s.driver.current_url:
                logger.error('up post error! %s', post_url)
                self.exception_recoder.append(False)
            else:
                logger.info('up post success! %s', post_url)
                self.exception_recoder.append(True)
        except:
            self.exception_recoder.append(False)
        if len(self.exception_recoder) < 10:
            return
        if any(self.exception_recoder) is True:
            self.exception_recoder.pop(0)
        else:
            send_mail()

    # @ExceptionReporter
    # def up_post(self, post_url):
    #     self.s.driver.get(post_url)
    #     self.s.driver.ensure_element_by_id('atc_content').send_keys(
    #         choice(self.commentaries))
    #     self.s.driver.ensure_element_by_id('fastbtn').ensure_click()
    #     time.sleep(randrange(60, 120))
    #     if 'post.php?action=reply' in self.s.driver.current_url:
    #         logger.error('up post error! %s', post_url)
    #         self.exception_recoder.append(False)
    #     else:
    #         logger.info('up post success! %s', post_url)
    #         self.exception_recoder.append(True)

    def is_boundary(self):
        """
        判断是否在指定时间段
        """
        now = arrow.now()
        if now.hour >= self.end_with:
            logger.info('%s 正在休眠, 明天%s点再回帖', now, self.start_at)
            time.sleep((now.shift(days=1).replace(hour=self.start_at, minute=0) - now).seconds)
        elif now.hour < self.start_at:
            time.sleep((now.replace(hour=self.start_at, minute=0) - now).seconds)
            logger.info('%s 正在休眠, %s点再回帖', now, self.start_at)

    def up_posts(self):
        """
        在指定时间段顶帖
        """
        while True:
            self.is_boundary()
            while self.posts.empty():
                self.get_posts()
            self.up_post(self.posts.get())