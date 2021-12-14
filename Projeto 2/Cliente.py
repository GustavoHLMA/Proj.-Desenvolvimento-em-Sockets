from socket import socket, AF_INET, SOCK_STREAM

sock = socket(AF_INET, SOCK_STREAM)

address = 'localhost',8090

sock.connect(address)

message = 'GET / HTTP/1.1\r\n'
message += 'Host: localhost\r\n'
message += '\r\n'

sock.send(message.encode())

data_recieved = sock.recv(2000)

print(data_recieved.decode())
