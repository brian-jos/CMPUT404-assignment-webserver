#  coding: utf-8 
import socketserver, os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
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
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self): # Brian Rogador
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)

        base_directory = "www/" # start in www

        request_list = str(self.data).split() # split request into list by whitespaces
        method = request_list[0][2:] # indexes GET/POST/PUT/DELETE, excludes b'
        file_path = request_list[1][1:] # indexes file path, excludes /

        # check for methods other than GET
        if (method != "GET"): # check for method other than GET
            self.request.sendall(bytearray("HTTP/1.1 405 Method Not Allowed\r\nConnection: close\r\n\r\n",'utf-8'))
            return

        # if file path is empty, turn it into /
        if (len(file_path) == 0 ):
            file_path = "/"

        # https://stackoverflow.com/a/3926550
        # restrict ".." as a file to prevent navigation, but allow "..." (... is not reserved and is a viable file name)
        if (file_path.find("..") > -1 and file_path.find("...") == -1):
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n",'utf-8'))
            return

        # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        # check if file path ends in a directory
        is_directory = os.path.isdir(base_directory + file_path) 

        # for directory file paths that don't end with /, redirect with 301
        if (is_directory and file_path[-1] != "/"):
            self.request.sendall(bytearray(f"HTTP/1.1 301 Moved Permanently\r\nLocation: {file_path}/\r\nConnection: close\r\n\r\n",'utf-8'))
            return
        
        # for root directories, use index.html
        if (is_directory and file_path[-1] == "/"):
            file_path += "index.html"
        
        # try to extract the file extension
        file_extension = ""
        if (file_path.rfind(".") > file_path.rfind("/")): # look for a file extension before the last /
            file_extension = file_path[file_path.rfind("."):]

        # attempt to open and read the file contents
        try:
            f = open(base_directory + file_path)
            content = f.read()
            f.close()
        except:
            self.request.sendall(bytearray("HTTP/1.1 404 Not Found\r\nConnection: close\r\n\r\n",'utf-8'))
            return

        # use supported mimetype if .html or .css
        mimetype = "text/plain"
        if (file_extension == ".html"):
            mimetype = "text/html"
        elif (file_extension == ".css"):
            mimetype = "text/css"

        # send content
        # https://docs.python-requests.org/en/v0.10.7/user/quickstart/#make-a-post-request
        # https://stackoverflow.com/a/28056437
        # https://stackoverflow.com/questions/55895197/python-socket-programming-simple-web-server-trying-to-access-a-html-file-from-s
        self.request.sendall(bytearray(f"HTTP/1.1 200 OK\r\nContent-Type: {mimetype}\r\nConnection: close\r\n\r\n",'utf-8'))
        for i in content:
            self.request.sendall(bytearray(i,'utf-8'))

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
