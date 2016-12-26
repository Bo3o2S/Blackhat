import getopt
import socket
import subprocess
import sys
import threading

listen             = False
command            = False
upload             = False
execute            = False
target             = ""
upload_destination = ""
port               = 0


def usage():
    pass
def run_command(command):

    command = command.rstrip()

    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Fail to execute command\r\n"

    return output

def client_handler(client_socket):
    global upload
    global execute
    global command

    if len(upload_destination):

        file_buffer = ""

        while True:
            data = client_socket.recv(1024)

            if not data:
                break
            else:
                file_buffer += data

        try:
                file_descriptor = open(upload_destination, "wb")
                file_descriptor.write(file_buffer)
                file_descriptor.close()

                client_socket.send("Success!!! : %s\r\n" %upload_destination)
        except:
                client_socket.send("Fail!!! : %s\r\n" %upload_destination)

    if len(execute):

        output = run_command(execute)
        client_socket.send(output)

    if command:

        while True:
            client_socket.send("<BHP:#> ")

            cmd_buffer =""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024)

            response = run_command(cmd_buffer)

            client_socket.send(response)

def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):
            client.send(buffer)

        while True:
            recv_len = 1
            response = ""

            while recv_len:
                data = client.recv(4096)
                recv_len = len(data)
                response += data

                if recv_len < 4096:
                    break

        print response

        buffer = raw_input("")
        buffer += "\n"

        client.send(buffer)
    except:
        print "Exception"

        client.close()

def server_loop():
    global target
    global port

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(target, port)

    server.listen(10)

    while True:
        client_socket, addr = server.accept()

        client_thread = threading.Thread(target=client_handler, args=(client_socket))
        client_thread.start()

def main():
    global listen
    global port
    global execute
    global target
    global command
    global upload_destination

    if not len(sys.argv[1:]):
        usage()

    try:
            getopt.getopt(sys.argv[1:], "hle:t:p:cu:", ["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
        print str(err)
        usage()

    if not listen and len(target) and port > 0:

        buffer = sys.stdin.read()

        #client
        client_sender(buffer)

        #server
    if listen:
        server_loop()
main()