# -*- coding: utf-8 -*-
import socket
from urlparse import urlparse
import urllib
import re


""" 
fp = fsocket()
print fp.open('http://www.baidu.com/')['html']

"""
class fsocket:
    host = None
    hostSetValue = None
    port = 80
    timeout = 30
    crlf = '\r\n'
    bufSize = 1024 

    def __init__(self):
        pass

    def open(self, url, method='get', params={}, requestHeaders={}, host=None, port=0):
        self.host = self.hostSetValue
        self.port = 80

        headers = dict()
        httpStr = ''
        for (k, v) in self.parseUrlHeader(url, method):
            '''头部GET/http1.1'''
            if k is 0:
                httpStr = v
            else:
                headers[k] = v

        if host is not None:
            self.host = host
        if port > 0:
            self.port = port

        for k in requestHeaders:
            headers[k] = requestHeaders[k]
        
        postStr = urllib.urlencode(params)

        #处理post
        if method.lower() == 'post':
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            headers['Content-Length'] = len(postStr)
        
        elif method.lower() == 'get' and postStr != '':
            if httpStr.find('?') == -1:
                httpStr = httpStr + '?'

            httpStr = httpStr + postStr

        print 'http://'+headers['Host']+httpStr.split(' ')[1]

        httpStr = httpStr + ' HTTP/1.1'

        '''拼接头部'''
        streamStr = httpStr + self.crlf

        for k in headers:
            streamStr = streamStr + k + ': ' + headers[k] + self.crlf
        streamStr = streamStr + self.crlf

        if method.lower() == 'post':
            streamStr = streamStr + postStr

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.timeout)
        sock.connect((self.host, self.port))
        sock.sendall(streamStr)
        content = self.fgetAll(sock)
        sock.close()

        return {'content': content, 'header':self.getHeader(content), 'html':self.getHtml(content)} 

    def parseUrlHeader(self, url, method):
        o = urlparse(url)
        if o.hostname is None:
            raise UnicodeDecodeError('url error')

        if self.host is None:
            self.host = o.hostname

        httpStr = method.upper() + ' ' + o.path 
        if o.query != '':
            httpStr += '?' + o.query 

        hostStr = o.hostname
        if o.port is not None:
            self.port = o.port
            hostStr += ':'+ str(o.port)
       
        return [(0, httpStr), ('Host', hostStr), ('Connection', 'Close')]


    def fgetAll(self, sock):
        strs = ''
        data = sock.recv(self.bufSize)
        while data:
            strs = strs + data
            data = sock.recv(self.bufSize)
        else:
            return strs 
        return strs 

    def getHeader(self, content, key=None):
        arr = content.split(self.crlf * 2)
        if key is None:
            return arr[0]

        for line in arr[0].split(self.crlf):
            _arr = line.split(':')
            if key == _arr[0]:
                return _arr[1]

        return None

    def getHtml(self, content):
        arr = content.split(self.crlf * 2)
        if self.getHeader(content, 'Transfer-Encoding') is not None:
            return re.sub(r'\r\n[0-9A-Fa-f]+\r\n', '', self.crlf + arr[1] + self.crlf)
        return arr[1]

    def setHost(self, ip):
        self.hostSetValue = ip
        return self

    def setTimeout(self, seconds):
        seconds = int(seconds)
        if seconds > 0:
            self.timeout = seconds 
        return self


