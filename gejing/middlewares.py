# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
from twisted.internet.error import TimeoutError, DNSLookupError, \
    ConnectionRefusedError, ConnectionDone, ConnectError, \
    ConnectionLost, TCPTimedOutError
from scrapy.core.downloader.handlers.http11 import TunnelError
from twisted.internet import defer
from twisted.web.client import ResponseFailed

import base64
import time
import paramiko
import re

'''
定义一个类，表示一台远端linux主机
'''
class Linux(object):
    # 通过IP, 用户名，密码，超时时间初始化一个远程Linux主机
    def __init__(self, ip, username, password, port, timeout=15):
        self.ip = ip
        self.username = username
        self.password = password
        self.timeout = timeout
        self.port = port
        # transport和chanel
        self.t = ''
        self.chan = ''
        # 链接失败的重试次数
        self.try_times = 3

    # 调用该方法连接远程主机
    def connect(self):
        while self.try_times > 0:
            # 连接过程中可能会抛出异常，比如网络不通、链接超时
            try:
                self.t = paramiko.Transport(sock=(self.ip, self.port))
                self.t.connect(username=self.username, password=self.password)
                self.chan = self.t.open_session()
                self.chan.settimeout(self.timeout)
                self.chan.get_pty()
                self.chan.invoke_shell()
                # 如果没有抛出异常说明连接成功，直接返回
                print('连接 %s 成功' % self.ip)
                # 接收到的网络数据解码为str
                # print(self.chan.recv(65535).decode('utf-8'))
                return
            # 这里不对可能的异常如socket.error, socket.timeout细化，直接一网打尽
            except Exception as e1:
                print(e1)
                if self.try_times != 0:
                    print('连接%s失败，进行重试' % self.ip)
                    self.try_times -= 1
                # else:
                #     print('重试 {} 3次失败，结束程序'.format(self.ip))
                #     # exit(1)


    # 断开连接
    def close(self):
        self.chan.close()
        self.t.close()

    # 发送要执行的命令
    def send(self, cmd):
        cmd += '\r'
        result = ''
        # 发送要执行的命令
        self.chan.send(cmd)
        # 回显很长的命令可能执行较久，通过循环分批次取回回显,执行成功返回true,失败返回false
        while True:
            time.sleep(0.5)
            ret = self.chan.recv(65535)
            ret = ret.decode('utf-8')
            result += ret
            return result


def get_ip():
    host = Linux(ip, 用户名, 密码, port)
    host.connect()
    host.send("adsl-stop")
    time.sleep(1)
    host.send("adsl-start")
    time.sleep(5)
    host.send("service tinyproxy restart")
    time.sleep(1)
    host.send("nginx -s reload")
    time.sleep(1)

    res = host.send("ifconfig")
    # print(res)
    p ="ppp0:\sflags=\d+<UP,POINTOPOINT,RUNNING,NOARP,MULTICAST>\s+mtu\s\d+\s+inet ([\s\S+]*?)  netmask 255.255.255.255"
    # print(re.findall(p, res))
    crawl_ip = re.findall(p, res)
    if len(crawl_ip) != 0:
        return crawl_ip[0] + ":8888"
        # print(crawl_ip[0])
    else:
        time.sleep(300)
        get_ip()

# 定义随机user-agent
ua = UserAgent()

class RandomUaIpMiddleware:
    ALL_EXCEPTIONS = (defer.TimeoutError, TimeoutError, DNSLookupError,
                      ConnectionRefusedError, ConnectionDone, ConnectError,
                      ConnectionLost, TCPTimedOutError, ResponseFailed,
                      IOError, TunnelError)

    def __init__(self):
        self.ip = get_ip()

    def process_request(self, request, spider):
        header = ua.random
        request.headers['User-Agent'] = header
        user_password = '用户名:密码'

        # spider.logger("[proxy]  {}".format(self.ip))
        request.meta["proxy"] = "http://" + self.ip

        b64_user_password = base64.b64encode(user_password.encode('utf-8'))
        request.headers['Proxy-Authorization'] = 'Basic' + b64_user_password.decode('utf-8')


    def process_response(self, request, response, spider):
        if response.status in [403, 400, 405, 301, 302]:
            # spider.logger.info("[proxy]   {}".format(self.proxy))
            while True:
                self.ip = get_ip()
                # spider.logger.info("[更的的新代理为]   {}".format(self.proxy))
                break
            new_request = request.copy()
            new_request_l = new_request.replace(url=request.url)
            return new_request_l
        return response

    def process_exception(self, request, exception, spider):
        # 捕获几乎所有的异常
        if isinstance(exception, self.ALL_EXCEPTIONS):
            # 在日志中打印异常类型
            # spider.logger.info("[Got exception]   {}".format(exception))
            # spider.logger.info("[需要更换代理重试]   {}".format(self.proxy))
            while True:
                self.ip = get_ip()
                # spider.logger.info("[更的的新代理为]   {}".format(self.proxy))
                break
            new_request = request.copy()
            new_request_l = new_request.replace(url=request.url)
            return new_request_l
        # spider.logger.info("[not contained exception]   {}".format(exception))

