# -*- coding:utf-8 -*-
# --------------------
# 20230904
# by YQ
# --------------------
# 爬虫
from bs4 import BeautifulSoup as bf
import requests
import ddddocr
import datetime
import urllib.parse
import time

headers = [{
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.42"},
    {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"},
    {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"},
    {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Mobile Safari/537.36"}]


# 控制台信息风格
def print_info(message):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + message)


def print_error(error):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + "!!!!!" + error + "!!!!!")


# 验证码处理
def check_code(url, head):
    img_url = url + 'CheckCode.aspx'
    try:
        check_code_img = requests.get(img_url, headers=head, stream=True).content
    except requests.exceptions:
        print_error('验证码识别模块异常')
        return False
    # with open('checkdoce.png', 'wb') as img:
    #     img.write(check_code_img)
    # 使用ddddocr进行验证码识别
    # 由于ddddocr没有对python11适配,在python11环境运行时需修改ddddocr的__init__.py文件中的
    # image = image.resize((int(image.size[0] * (64 / image.size[1])), 64), Image.LANCZOS).convert('L')
    ocr = ddddocr.DdddOcr()
    checkcode = ocr.classification(check_code_img)
    return checkcode


def zf_spider(username, password, name, host, header, gnmkdm, safe_time):
    print_info(f'参数信息 username: {username} password: {password} name: {name} header: {header} host: {host}')
    # 创建会话
    session = requests.Session()
    try:
        login_page = session.get(host, headers=headers[header])
    except requests.exceptions:
        print_error('尝试连接到目标服务器失败')
        return False
    if login_page.status_code != 200:
        print_error(host + ' 访问被拒绝')
        return False

    # 响应处理
    basic_url = login_page.url[0:49]
    print_info('响应url:' + basic_url)
    page_soup = bf(login_page.text, 'html.parser')
    try:
        viewstate = page_soup.find('input', {'name': '__VIEWSTATE'})['value']
        print_info('获取到的viewstate:' + viewstate)
    except TypeError:
        print_error('viewstate获取失败')
        return False
    time.sleep(safe_time)
    # 获取验证码
    checkcode = check_code(basic_url, headers[header])
    if not checkcode:
        print_error('验证码识别出错')
        return False
    else:
        print_info('获取到的验证码:' + str(checkcode))
    pass

    # 模拟登录请求
    login_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0", "Connection": "keep-alive", "Content-Length": "191",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": host[7:],
        "Origin": host,
        "Referer": basic_url + "default2.aspx",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": headers[header]["User-Agent"]
    }
    login_data = {
        "__VIEWSTATE": viewstate,
        "txtUserName": username,
        "TextBox2": password,
        "txtSecretCode": checkcode,
        "RadioButtonList1": "%D1%A7%C9%FA",
        "Button1": "",
        "lbLanguage": "",
        "hidPdrs": "",
        "hidsc": ""
    }
    try:
        try_login = requests.session().post(basic_url + "default2.aspx", data=login_data, headers=login_header)
    except requests.exceptions:
        print_error('Connection to target server failed')
        return False
    if try_login.status_code != 200:
        print_error('尝试登录失败')
        return False
    else:
        print_info('尝试登录成功')
    if safe_time > 0:
        print_info(f'获取新的VIEWSTATE安全时间已经设置{safe_time}秒')
    time.sleep(safe_time)

    # 获取新的VIEWSTATE
    new_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Connection": "keep-alive",
        "Host": host[7:],
        "Referer": basic_url + "xs_main.aspx?xh=" + username,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": headers[header]["User-Agent"]
    }
    time.sleep(safe_time)
    try:
        new_resp = requests.session().get(
            basic_url + "xscjcx.aspx?xh=" + username + "&xm=" + urllib.parse.quote(name) + "&gnmkdm=" + gnmkdm,
            headers=new_header)
    except requests.exceptions:
        print_error("request error")
        return False
    if new_resp.status_code != 200:
        print_error('获取新VIEWSTATE失败')
        return False
    else:
        print_info('获取新VIEWSTATE成功')
    new_page_soup = bf(new_resp.text, 'html.parser')
    new_viewstate = new_page_soup.find('input', {'name': '__VIEWSTATE'})['value']
    # 尝试获取成绩
    score_header = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,/;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        "Cache-Control": "max-age=0", "Connection": "keep-alive", "Content-Length": "191",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": host[7:],
        "Origin": host,
        "Referer": basic_url + "xscjcx.aspx?xh=" + username + "&xm=" + urllib.parse.quote(name) + "&gnmkdm=" + gnmkdm,
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": headers[header]["User-Agent"]
    }
    score_data = {
        'btn_zcj': '%C0%FA%C4%EA%B3%C9%BC%A8',
        'ddlXN': '',
        'ddlXQ': '',
        '__EVENTVALIDATION': '',
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__VIEWSTATE': new_viewstate,
        'hidLanguage': '',
        'ddl_kcxz': ''
    }
    # 发送查询请求
    if safe_time > 0:
        print_info(f'发送查询请求安全时间已经设置{safe_time}秒')
    time.sleep(safe_time)
    try:
        print_info('尝试发送查询请求，当前目标服务器收到大量并发请求，本次查询请求可能会持续数分钟,请耐心等待')
        score = requests.session().post(
            basic_url + "xscjcx.aspx?xh=" + username + "&xm=" + urllib.parse.quote(name) + "&gnmkdm=" + gnmkdm,
            data=score_data, headers=score_header, timeout=600)
    except requests.exceptions.ReadTimeout:
        print_error('远程服务器超时')
        return False
    except requests.exceptions:
        print_error('连接到目标服务器失败')
        return False

    if score.status_code != 200:
        print_error('获取查询响应失败')
        return False
    else:
        print_info('获取查询响应成功')

    html_response = score.text
    # 保存查询结果
    with open('score.txt', 'w', encoding='utf-8') as save:
        save.write(html_response)
    # 获取html_response的title
    soup = bf(html_response, 'html.parser')
    title = soup.title.string
    if title != '现代教学管理信息系统':
        print_error("目标服务器已经超载,返回无用响应, 本次查询失败")
        return False
    print_info("查询响应解析成功,请按“获取结果”按钮检查返回信息是否有价值")
    return True
