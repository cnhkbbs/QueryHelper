# -*- coding:utf-8 -*-
# --------------------
# 20230904
# by YQ
# --------------------
# 主程序
import os
import datetime
import requests
import server

build = 2


# 控制台信息风格
def print_info(message):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + message)


def print_error(error):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + "!!!!!" + error + " !!!!!")


def check_update():
    print_info("Checking for update...")
    try:
        version_info = eval(requests.get('https://cnhkbbs.github.io/staticcdn/QueryHelper/version.txt').text)
        if version_info[0] > build:
            print_info("Try to download the newest version...")
            newest_version = requests.get(version_info[1]).content
            with open(os.getcwd() + "\\QueryHelper_new.exe", 'wb') as file:
                file.write(newest_version)
            print_info("Succeed!")
            print_info("新版本QueryHelper_new.exe已下载完成,请手动删除旧版本后运行新版本")
            exit()
        else:
            print_info("You are running the last version!")
    except requests.exceptions.ConnectionError:
        print_error("Network error！")
        input("按回车键退出")
        exit()
    except SyntaxError:
        print_error("Syntax error!")
        input("按回车键退出")
        exit()


if __name__ == '__main__':
    print_info("版本:1.0   内部版本:" + str(build))
    print_info("问题反馈请提交Issue至https://github.com/cnhkbbs/QueryHelper")
    # 检查更新
    check_update()
    # 启动服务
    server.start_server()
