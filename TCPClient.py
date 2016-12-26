import socket

target_host = "127.0.0.1"

target_port = 9999

#make socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to host
client.connect((target_host, target_port))

#send to host
client.send("12345")

#recieve from host
response = client.recv(4096)

print response