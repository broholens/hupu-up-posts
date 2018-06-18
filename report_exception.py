
import requests

mail_uri = 'http://39.107.86.245:5000'
mail = {
    'recipient': 'zzwcng@126.com',
    'subject': 'HuPu',
    'content': '请重新登录 http://39.107.86.245:8080'
}


def send_mail():
    requests.post(mail_uri, data=mail)


class ExceptionReporter(object):

    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        try:
            return self.func(*args, **kwargs)
        except:
            send_mail()



# @ExceptionReporter
# def a(x):
#     print(a)
#
# @ExceptionReporter
# def b(x):
#     print(x)
#
# @ExceptionReporter
# def c(b):
#     print(c)
#
# @ExceptionReporter
# def d():
#     print(c)
#
# @ExceptionReporter
# def e():
#     print(c)
#
# @ExceptionReporter
# def f():
#     print(c)
#
# a()
# b(1)
# c()
# d()
# e()
# f()