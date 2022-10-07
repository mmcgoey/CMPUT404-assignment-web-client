#!/usr/bin/env python3
# coding: utf-8
# Copyright 2022 Abram Hindle, Mark McGoey, https://github.com/tywtyw2002, and https://github.com/treedust
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

from ast import arg
from fileinput import close
from sqlite3 import connect
import sys
import socket
import re
import json
from urllib import response
from urllib.parse import urlencode
from sys import getsizeof
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port(self,url):
        port_num = urllib.parse.urlparse(url).port
        #print("HOST NAME",urllib.parse.urlparse(url).hostname)
        return port_num
        #print("WHAT IS PARSE",port_num)
    
    def get_remote_ip(self,host):
        #Note this method was provided in the lab 2 code
        #print(f'Getting IP for {host}')
        try:
            remote_ip = socket.gethostbyname( host )
        except socket.gaierror:
            print ('Hostname could not be resolved. Exiting')
            sys.exit()

        print (f'Ip address of {host} is {remote_ip}')
        return remote_ip
    

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def get_code(self, data):
        code = int(data.split()[1])
        return code

    def get_headers(self,data):
        # https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res
        # I used the cite above to solve this problem
        find_delimitter = data.find('\r\n\r\n')
        if find_delimitter >= 0:
            return data[:find_delimitter]
        return data

    def get_body(self, data):
        # https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res
        # I used the cite above to solve this problem
        find_delimitter = data.find('\r\n\r\n')
        if find_delimitter >= 0:
            return data[find_delimitter +4:]
        return data
    
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

        host = urllib.parse.urlparse(url).hostname
        #print ("IS HOST RETURNING?",host)
        #host_name = socket.gethostbyname(host)
        
        host_ip = self.get_remote_ip(host)


        port = self.get_host_port(url)

        if port == None:
            port = 80
            #print("FOUND PROBLEMMMMM")

        #print("is port now 80?",port)
        #print("WHAT IS IP",host_ip)
        #print("WHAT IS THE URL",url)

        response = 'GET %s HTTP/1.1\r\nHost: %s\r\nAccept: */*\r\nConnection: close\r\n\r\n'%(url,host)
        #response = 'GET / HTTP/1.1\r\nHost: %s\r\n\r\n'%(host)

        self.connect(host_ip,port)

        self.sendall(response)

        #self.socket.shutdown(socket.SHUT_WR)

        recv_info = self.recvall(self.socket)

        print(recv_info)

        is_headers = self.get_headers(recv_info)
        #print("CHECK IF GET_HEADERS WORKS",is_headers)

        #print("IS RECV_INFO EMPTY",recv_info)
        #code = recv_info.split()
        code = self.get_code(recv_info)

        body = self.get_body(recv_info)
        #body += recv_info
        #print("WHAT IS CODE",body)

        self.socket.close()

        
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host = urllib.parse.urlparse(url).hostname

        host = str(host)
        
        #print("WHAT ARE THE ARGS",args)

        
        
        host_ip = self.get_remote_ip(host)


        port = self.get_host_port(url)

        if port == None:
            port = 80
            #print("FOUND PROBLEMMMMM")

        #print("is port now 80?",port)
        #print("WHAT IS IP",host_ip)
        #print("WHAT IS THE URL",url)

       

        if args != None:
            args_encode = urlencode(args)
            #print("WHAT IS args_encode",args_encode)
            response = 'POST %s HTTP/1.1\r\nHost: %s:%d\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: application/x-www-form-urlencoded\r\nContent-Length: %d\r\nConnection: close\r\n\r\n'%(url,host,port,len(args_encode)) + args_encode 
        else:
            response = 'POST %s HTTP/1.1\r\nHost: %s:%d\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nConnection: close\r\n\r\n'%(url,host,port) 


       

        #print("WHAT IS MY RESPONSE", response)
        

        self.connect(host_ip,port)

        self.sendall(response)
      

        #self.socket.shutdown(socket.SHUT_WR)

        recv_info = self.recvall(self.socket)

        print(recv_info)
        

        #print("IS RECV_INFO EMPTY",recv_info)
       

        code = self.get_code(recv_info)

        body = self.get_body(recv_info)
        

        #print("WHAT IS CODE IF NOT 200?",body)
       

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
        print("is <=1 called!")
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print("TEST WHAT ARGV[2] IS",sys.argv[2])
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print("TEST WHAT ARGV[1] IS",sys.argv[1])
        print(client.command( sys.argv[1] ))
