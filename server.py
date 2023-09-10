# -*- coding:utf-8 -*-
# --------------------
# 20230904
# by YQ
# --------------------
# fastapi服务
import time

import requests
import uvicorn
from fastapi import FastAPI, Form, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import datetime
import asyncio
import cookfood
import spider

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"])
dev_mode = False


# 控制台信息风格
def print_info(message):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + message)


def print_error(error):
    print('[' + datetime.datetime.now().strftime('%H:%M:%S') + ']' + "!!!!!" + error + "!!!!!")


# 表单数据过滤
def filter_data(uname, server, safe_time, executions):
    global dev_mode
    if uname == "dev":
        if dev_mode:
            dev_mode = False
            print_info("开发者模式已关闭,条件过滤开启")
            return "*****开发者模式关闭*****"
        else:
            dev_mode = True
            print_info("开发者模式已启用,条件过滤关闭")
            return "*****开发者模式启用*****"
    if dev_mode:
        return "pass"
    else:
        if int(safe_time) < 2:
            return "安全时间过短"
        elif int(executions) > 10:
            return "单次执行次数过多"
        else:
            try:
                try_connect = requests.get(server).status_code
                if try_connect != 200:
                    return "网络错误,无法与目标服务器建立连接"
            except requests.exceptions.ConnectionError:
                return "由于目标计算机积极拒绝，无法连接。"
            except requests.exceptions.MissingSchema:
                return "非法的URL格式。正确的URL格式应类似于：http://127.0.0.1"
            except Exception as e:
                print_error("未知错误" + str(e))
                return "未知错误请留意驱动输出"
        return "pass"


# 后台任务
async def perform_tasks(uname, pwd, cname, host, header, gnmkdm, safe_time, executions):
    await asyncio.sleep(0)
    try:
        for i in range(int(executions)):
            print("*" * 100 + "\n第" + str(i + 1) + "次执行\n" + "*" * 100)
            if spider.zf_spider(uname, pwd, cname, host, int(header), gnmkdm, safe_time):
                print_error("*" * 50)
                print_error("本次任务已终止,如需继续执行请重新提交任务")
                print_error("*" * 50)
                break
            time.sleep(safe_time)
    except Exception as e:
        print_error("未知异常" + str(e))


@app.post("/")
async def index():
    return {"msg": "Hi", "code": 200}


@app.post("/submit")
async def submit(background_tasks: BackgroundTasks,
                 name: str = Form(...),
                 password: str = Form(...),
                 chinese_name: str = Form(...),
                 server: str = Form(...),
                 header: str = Form(...),
                 safe_time: str = Form(...),
                 executions: str = Form(...),
                 gnmkdm: str = Form(...)):
    filter_result = filter_data(name, server, safe_time, executions)
    if filter_result == "pass":
        background_tasks.add_task(perform_tasks, name, password, chinese_name, server, header, gnmkdm, int(safe_time),
                                  executions)
        return HTMLResponse(
            content="<a>任务提交成功,请留意驱动日志输出</a><hr><a href='https://sboxm.link/staticcdn/QueryHelper/'>点此返回</a>")
    else:
        return HTMLResponse(
            content="<a style='color: darkred;'>任务已被驳回," + filter_result
                    + "</a><br /><hr><a href='https://sboxm.link/staticcdn/QueryHelper/'>点此返回</a>")


@app.post("/getresult")
async def getresult():
    html_content = cookfood.CookFood()
    return HTMLResponse(content=html_content)


def start_server():
    uvicorn.run(app, host="127.0.0.1", port=2023)
