#!/usr/bin/env python
# -*- coding:utf-8 -*-

import SocketServer
import os
import time
import threading
from libs.fsocket import fsocket
import re
import json

class Spider(object):
    logFile = 'service.log'
    searches = ['baidu', 'google']
    result = {}

    def __init__(self):
        _dir = os.getcwd() + '/logs/'
        self.logFile = _dir + self.logFile
        if not os.path.exists(_dir):
            os.mkdir(_dir, 0777)

    def doProcess(self, kw):
        threads = []
        for i in self.searches:  
            t = threading.Thread(target=self.doAction, args=(i,kw))
            threads.append(t)
            t.setDaemon(True)
            t.start()

        for t in threads:
            t.join()

        #汇总处理    
        ret = []
        for k in self.result:
            ret.append(self.result[k])

        return ret

    def doAction(self, action='baidu', kw=''):
        if action == 'baidu':
            self.baiduAction(kw)

    def baiduAction(self, kw=''):
        url = 'https://www.baidu.com/s?wd='+kw
        html = fsocket().open(url)['html']

        match = re.search("id=\"content_left\">(.+)clear\:both\;height\:0\;", html, re.DOTALL)
        url = re.findall('<h3 class="t"><a[^>]+?href\s*=\s*"([^"]+)"[^>]+>(.*?)<\/a>', match.group(0),  re.DOTALL)
        ret = re.findall('class="c\-abstract">(.*?)<\/div>', match.group(0),  re.DOTALL)

        self.result['baidu'] = []
        i = 0
        for k, v in url:
            print k,v
            content = {}
            content['url'] = k
            content['urlContent'] = v
            if len(ret) > i:
                content['desc'] = ret[i]
            else:
                content['desc'] = ''
            self.result['baidu'].append(content)
            i += 1

    def log(self, data):
        fp = open(self.logFile, 'wb')
        
        content = time.strftime('%Y-%m-%d %H:%M:%S') + '\t'
        content += '\t'+repr(data) + '\n'
        fp.write(content)
        fp.close()


class MyTCPHandler(SocketServer.BaseRequestHandler):
    """
    The RequestHandler class for our server.

    It is instantiated once per connection to the server, and must
    override the handle() method to implement communication to the
    client.
    """

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print self.data
        # just send back the same data, but upper-cased
        self.request.sendall(json.dumps(self.doAction(self.data)))

    def doAction(self, data):
        return Spider().doProcess(data)

if __name__ == "__main__":
    HOST = ''
    PORT = 10086

    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

