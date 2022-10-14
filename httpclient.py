#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    # get status code
    def get_code(self, data):
        code = int(data.split('\r\n')[0].split(' ')[1])
        return code

    # get header
    def get_headers(self,data):
        response = data.split('\r\n\r\n')[0]
        return response

    # get body information
    def get_body(self, data):
        body = data.split('\r\n\r\n')[1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 500
        body = ""

        parse_result = urllib.parse.urlparse(url)

        # get host name, port number and scheme name
        host_name = parse_result.hostname
        port_number = parse_result.port
        scheme_name = parse_result.scheme

        # default port is 80
        if port_number == None and scheme_name == "http":
            port_number = 80
        elif port_number == None and scheme_name == "https":
            port_number = 443

        self.connect(host_name, port_number)

        # if path is none, set '/'
        if not parse_result.path:
            path = '/'
        else:
            path = parse_result.path
        
        request = 'GET ' + path + ' HTTP/1.1\r\nHost: ' + host_name + '\r\nConnection:closed\r\n\r\n'

        self.sendall(request)
        
        response = self.recvall(self.socket)

        code = int(self.get_code(response))
        body = self.get_body(response)

        self.close()

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        parsed_url = urllib.parse.urlparse(url)

        host_name = parsed_url.hostname
        port_number = parsed_url.port
        scheme_name = parsed_url.scheme
        
        # default port is 80
        if port_number == None and scheme_name == 'http':
            port_number = 80
        elif port_number == None and scheme_name == 'https':
            port_number = 443

        # check whether args is none
        if args == None:
            arguments = urllib.parse.urlencode('')
        else:
            arguments = urllib.parse.urlencode(args)

        self.connect(host_name, port_number)

        # Set path = '/' if it is none
        if not parsed_url.path:
            path = '/'
        else:
            path = parsed_url.path

        # length of argument
        argument_length = str(len(arguments))
        request = 'POST ' + path + ' HTTP/1.1\r\nHost: ' + host_name + '\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: ' + argument_length + '\r\nConnection: closed\r\n\r\n' + arguments
        
        self.sendall(request)

        response = self.recvall(self.socket)

        code = self.get_code(response)
        body = self.get_body(response)

        self.close()

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
