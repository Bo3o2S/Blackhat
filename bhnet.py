#define some global variables
import getopt
import socket
import sys

import thread

listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0

def client_sender():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
            client.connection((target, port))

            if len(buffer):
                client.send(buffer)

            while True:
                recv_len = 1
                response = ""

                while recv_len:
                    data         = client.recv(4096)
                    recv_len     = len(data)
                    response    += data

                    if recv_len < 4096:
                        break

            print response,

            #wait for more input
            buffer = raw_input("")
            buffer+= "\n"

            #send it off
            client.send(buffer)

    except:
        print "[*] Exception! Exiting."

        #close the connection
        client.close()

def server_loop():
    global target
    global port

    if not len(target):
        target = "0.0.0.0"

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target, port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        client_thread = thread.Threading(target=client_sender, args=(client_socket,))
        client_thread.start()

def usage():
    print "Compatible Netcat"
    print
    print "Usage: bhpnet.py -t target_host -p port"
    print "-l --listen              - listen on [host]:[port] for incommin connections"
    print "-e --execute=file_to_run - execute the given file upon receiving a connection"
    print "-c --ceommand             - initialize a command shell"
    print "-u --upload=destination  - upon receiving connection upload a file and write to [destination]"
    print
    print
    print "Examples: "
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -c"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -u=c:\\target.exe"
    print "bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\""
    print "echo 'ABCDEFGHI' | ./bhpnet.py -t 192.168.11.12 -p 135"
    sys.exit(0)

#main func
def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):
        usage()

    # read the commandline options
    try:
            opts, args = getopt.getopt(sys.argv[1:], "hle:t:p:cu:",["help","listen","execute","target","port","command","upload"])
    except getopt.GetoptError as err:
            print str(err)
            usage()

    #save option to variables
    for o,a in opts:
        if o in ("-h","--help"):
            usage()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--commandshell"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False, "Unhandled Option"

    #send date from stdin
    if not listen and len(target) and port > 0:

        #send data from stdin
        buffer = sys.stdin.read()

        #send data off
        client_sender(buffer)

    if listen:
        server_loop()


main()