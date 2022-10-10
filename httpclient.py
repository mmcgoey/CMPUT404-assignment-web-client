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



'''
CITATIONS: 
My get_headers(self,data) and get_body(self,data) function is based off the code snippet from the stack over flow website linked below
https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res
These functions are based off an answer provided by bogdan on Dec 12, 2011

My get_remote_ip(self,host) function is taken from the provided code in lab 2 client.py 

Other sites and resources I referred to while completing the assignment:

The 404 lecture slides on HTTP

https://stackoverflow.com/questions/45695168/send-raw-post-request-using-socket,
https://www.internalpointers.com/post/making-http-requests-sockets-python,
https://www.geeksforgeeks.org/get-post-requests-using-python/,
https://stackoverflow.com/questions/28670835/python-socket-client-post-parameters,
https://www.w3schools.com/python/ref_requests_get.asp




'''
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):

    # The purpose of this function is to get the port number that is provided in the url
    # If no port number is provided in the url then I will default the port number to 80
    def get_host_port(self,url):
        port_num = urllib.parse.urlparse(url).port
        
        if port_num == None:
            port_num = 80
        
        return port_num
        
    
    def get_remote_ip(self,host):
        # CITATION: This function was taken from lab 2 client.py
        
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

    # The purpose of this function is to get the status code returned by the server
    def get_code(self, data):
        code = int(data.split()[1])
        return code

    # The purpose of this function is to get the headers returned by the server
    def get_headers(self,data):
        # CITATION BELOW
        # https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res

        # I used the ideas suggested in this stack over flow post to seperate the body from the headers


        find_index = data.find('\r\n\r\n')

        header_str = ""
        # if find_index is -1 then '\r\n\r\n' has not been found
        if find_index == -1:
            return data
        else:
            # The body and the headers are seperated by '\r\n\r\n' so to get headers I am returning the string from the beginning till \r\n\r\n is reached
            for i in data[0:find_index]:
                header_str += i
            
            return header_str
        
    # The purpose of this function is to get the body returned by the server
    def get_body(self, data):
        # CITATION BELOW
        # https://stackoverflow.com/questions/8474745/how-do-i-get-the-body-of-a-http-response-from-a-string-containing-the-entire-res

        # I used the ideas suggested in the stack over flow post to seperate the body from the headers

        find_index = data.find('\r\n\r\n')

        body_str = ""
        # if find_index is -1 then 'r\n\r\n' has not be found 
        if find_index == -1:
            return data
        else:
            # return body. The body is from \r\n\r\n to the end of the string 
            find_index_len = len('\r\n\r\n')
            # need to add the find_index_len so that the \r\n\r\n is not included in the body output
            for i in data[find_index + find_index_len:]:
                body_str += i
            return body_str
            
        
    
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
 
        # Getting host name
        host = urllib.parse.urlparse(url).hostname
        
        # Getting host ip address using the host name
        host_ip = self.get_remote_ip(host)


        port = self.get_host_port(url)

        response = 'GET %s HTTP/1.1\r\nHost: %s\r\nAccept: */*\r\nConnection: close\r\n\r\n'%(url,host)
        
        # establish a connection
        self.connect(host_ip,port)

        # send request
        self.sendall(response)

        # get servers response
        recv_info = self.recvall(self.socket)

        print(recv_info)

        is_headers = self.get_headers(recv_info)
        
        code = self.get_code(recv_info)

        body = self.get_body(recv_info)

        
        self.socket.close()
  
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        host = urllib.parse.urlparse(url).hostname

        host = str(host)
        
        host_ip = self.get_remote_ip(host)

        port = self.get_host_port(url)

        # If args are provided then encode the args into query string formate.
        # If no args are provided then there's no need to encode anything
        if args != None:
            args_encode = urlencode(args)
  
            response = 'POST %s HTTP/1.1\r\nHost: %s:%d\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: application/x-www-form-urlencoded\r\nContent-Length: %d\r\nConnection: close\r\n\r\n'%(url,host,port,len(args_encode)) + args_encode 
        else:
            response = 'POST %s HTTP/1.1\r\nHost: %s:%d\r\nContent-Type: application/x-www-form-urlencoded\r\nAccept: application/x-www-form-urlencoded\r\nContent-Length: 0\r\nConnection: close\r\n\r\n'%(url,host,port) 

        # establish a connection
        self.connect(host_ip,port)

        # send request
        self.sendall(response)
      
        # get servers response
        recv_info = self.recvall(self.socket)

        print(recv_info)
        
        code = self.get_code(recv_info)

        body = self.get_body(recv_info)
        
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
        
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        
        print(client.command( sys.argv[1] ))
