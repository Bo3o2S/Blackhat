import socket

target_ip = "www.google.com"
target_port = 80

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

client.sendto("HIHI", (target_ip, target_port))

data, addr = client.recvfrom(4096)

print data