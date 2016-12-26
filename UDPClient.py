import socket

target_host = "www.google.com"
target_port = 80

#make socket object
client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#send to host
client.sendto("HIHIHI",(target_host,target_port))

#receive from host
data, addr = client.recvfrom(4096)

print data