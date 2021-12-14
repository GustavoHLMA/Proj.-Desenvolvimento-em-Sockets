from mimetypes import guess_type
from datetime import datetime
from socket import socket, AF_INET, SOCK_STREAM
import os


class Server:
    def __init__(self, host, port):
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((host, port))
        self.documentRoot = os.getcwd()


        self.html = ''
        self.status = 200
        self.server.listen()
        self.default_html()

        if not os.path.exists(self.documentRoot):
            os.mkdir(self.documentRoot)

        while True:
            (self.client_socket, self.address_client) = self.server.accept()
            data = self.recv()
            self.send(data)

    def recv(self):
        data = self.client_socket.recv(2048)
        print(data.decode())
        return data

    def send(self, data):
        methodList = ["HEAD", "POST", "PUT", "PATCH", "DELETE", "CONNECT", "OPTIONS", "TRACE"]
        msg_version = data.decode().split(" ")
        version = msg_version[2][5:8]
        path = self.documentRoot
        if msg_version[1] != '/favicon.ico':
            path = self.documentRoot + msg_version[1]
        command = msg_version[0]

        if command in methodList:
            self.status = 501

        elif command != "GET":
            self.status = 400

        if version != '1.1' and version != '1.0':
            self.status = 505

        try:
            if os.path.isdir(path):
                document_root_split = self.documentRoot.split('/')
                
                paths = [os.path.join(path, name) for name in os.listdir(path)]

                path_split = path.split('/')
                flag = False
                current_path = ''
                for file in path_split:
                    if flag:
                        current_path += ('/' + file)
                    elif file == document_root_split[-1]:
                        flag = True

                self.html = f'''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>Index of {current_path}</title>
                    </head>
                    <body>
                        <h1>Index of {current_path}</h1>
                        <table>
                            <tr>
                                <th>Name</th>
                                <th>Last Modified</th>
                                <th>Size</th>
                                <th>Description</th>
                            </tr>
                    '''

                for p in paths:
                    path_split = p.split('/')
                    flag = False
                    current_path = ''
                    for file in path_split:
                        if flag:
                            current_path += ('/' + file)
                        elif file == document_root_split[-1]:
                            flag = True
                    stamp = os.path.getmtime(p)
                    dt_object = datetime.fromtimestamp(stamp)
                    if not os.path.isdir(p):
                        self.html += f'''
                                <tr>
                                    <td><a href= {f'{current_path}'}>{os.path.basename(p)}</td>
                                    <td align= "right">{dt_object}</td>
                                    <td align= "right">{os.path.getsize(p)}</td>
                                    <td>&nbsp;</td>
                                </tr>
                        '''

                    else:
                        self.html += f'''
                                <tr>
                                    <td><a href= {f'{current_path}'}>{os.path.basename(p)}</td>
                                    <td align= "right">{dt_object}</td>
                                    <td align= "right"></td>
                                    <td>&nbsp;</td>
                                </tr>
                        '''

                self.html += '''
                        </table>
                        <h3>Servidor Nem Abre.</h3>
                    </body>
                    </html>
                '''
                file = self.html.encode()
                self.default_html()
            else:
                print(path)
                arq = open(path, 'rb')
                file = arq.read()
                arq.close()
        except FileNotFoundError:
            self.status = 404

        if self.status == 501:
            page = ('HTTP/1.1 501 not implemented\r\n'
                    'Date: Thu 19 Aug 2021 12:00:01 GMT\r\n'
                    'Allow: GET'
                    'Server: servidornemabre/0.0.1 (Windows)\r\n'
                    'Content-Type: text/html\r\n'
                    '\r\n')
            page += ('''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>501 not implemented</title>
                    </head>
                    <body>
                        <h1>501 not implemented.</h1>
                    </body>
                    </html>''')
            newpage = page.encode()
            self.status = 200

        elif self.status == 505:
            page = ('HTTP/1.1 505 HTTP Version Not Supported\r\n'
                    'Date: Thu 19 Aug 2021 12:00:01 GMT\r\n'
                    'Server: servidornemabre/0.0.1 (Windows)\r\n'
                    'Content-Type: text/html\r\n'
                    '\r\n')
            page += ('''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>505 HTTP Version Not Supported</title>
                    </head>
                    <body>
                        <h1>505 HTTP Version Not Supported</h1>
                    </body>
                    </html>''')
            newpage = page.encode()
            self.status = 200

        elif self.status == 400:
            page = ('HTTP/1.1 400 Bad Request\r\n'
                    'Date: Thu 19 Aug 2021 12:00:01 GMT\r\n'
                    'Server: servidornemabre/0.0.1 (Windows)\r\n'
                    'Content-Type: text/html\r\n'
                    '\r\n')
            page += ('''
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <title>400 Bad Request</title>
                    </head>
                    <body>
                        <h1>400 Bad Request</h1>
                    </body>
                    </html>''')
            newpage = page.encode()
            self.status = 200

        elif self.status == 404:
            page = ('HTTP/1.1 404 Not Found\r\n'
                    'Date: Thu 19 Aug 2021 12:00:01 GMT\r\n'
                    'Server: servidornemabre/0.0.1 (Windows)\r\n'
                    'Content-Type: text/html\r\n'
                    '\r\n')
            page += ('''
                        <!DOCTYPE html>
                        <html lang="en">
                        <head>
                            <meta charset="UTF-8">
                            <title>404 not found</title>
                        </head>
                        <body>
                            <h1>404 error not found</h1>
                            sorry, this file wasn't found.
                        </body>
                        </html>''')
            newpage = page.encode()
            self.status = 200

        else:
            page = ('HTTP/1.1 200 OK\r\n'
                    f'Date: {os.path.getatime(path)}\r\n'
                    'Server: servidornemabre/0.0.1 (Windows)\r\n'
                    f'Content-Type: {guess_type(path)[0]}\r\n'
                    f'Content-lenght: {os.path.getsize(path)}\r\n'
                    '\r\n')
            newpage = page.encode() + file

        self.client_socket.send(newpage)

    def default_html(self):
        self.html = '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Index of /</title>
        </head>
        <body>
            <h1>Index of /</h1>
            <table>
                <tr>
                    <th>Name</th>
                    <th>Last Modified</th>
                    <th>Size</th>
                    <th>Description</th>
                </tr>
            '''

    def close(self):
        print("Servidor encerrado")
        self.client_socket.close()


print("Ouvindo requisições\n\n")
server = Server("localhost", 8090)
