import json
import requests


def save_cookies(driver, username):
    """save driver cookie to file"""
    json_cookies = json.dumps(driver.get_cookies())
    with open(username+'.json', 'w') as f:
        f.write(json_cookies)


def send_mail(content):
    mail_uri = 'http://39.107.86.245:5000'
    mail = {
        'recipient': 'zzwcng@126.com',
        'subject': 'HuPu',
        'content': content
    }
    requests.post(mail_uri, mail)
