import socket
import sys
import threading

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic

form_class = uic.loadUiType("proxy.ui")[0]


class ProxyWindow(QWidget, form_class):
    def __init__(self):
        super(QWidget, self).__init__()
        super(form_class, self).__init__()
        self.setupUi(self)
        self.setWindowTitle("X-Proxy by Bo3o2S")
        self.connect(self.Start_Button, SIGNAL("clicked()"), self.Start_Proxy)
        self.ErrMsg = ""
        self.proxy_thread = ""

    def setTextToDataEdit(self, str):
        self.Data_Edit.setText(str)
        #self.show()
        QApplication.processEvents()
        # ret = self.exec_()
        # if ret is self.Accepted or ret is self.Rejected:
        #     self.close()


        #return self.exec_()
        #self.show()125.209.222.142
        #self.Data_Edit.show()
        #self.Data_Edit.exec_()
        #self.exec_()



    def setTextToDataEditN(self, str):
        self.Data_Edit.append(str)
        #self.Data_Edit.show()
        QApplication.processEvents()

        #sys.exit(self.exec_())



    def server_loop(self, local_host, local_port, remote_host, remote_port, receive_first):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind((local_host, local_port))
        except:
            self.setTextToDataEdit("[ERR] Failed to Listen on %s : %d" % (local_host, local_port))
            self.setTextToDataEditN("[ERR] Check for other listening socket or correct permisstions")

        server.listen(10)

        self.setTextToDataEdit("Listening on %s : %d" % (local_host, local_port))



        while True:
            if self.Stop_Button.isFlat() is True:
                self.setTextToDataEditN("Server Stopped")
                break

            client_socket, addr = server.accept()

            # print out the local connection information
            self.setTextToDataEditN("[==>] Receive incomming connection from %s : %d" % (addr[0], addr[1]))

            # start a thread to talk to the remote host

            # self.proxy_thread = threading.Thread(target=self.proxy_handler,
            #                                 args=(client_socket, remote_host, remote_port, receive_first))
            # self.proxy_thread.start()
            self.proxy_thread = Proxy_thread(client_socket, remote_host, remote_port, receive_first)
            self.proxy_thread.start()

    def Start_Proxy(self):
        local_host = self.Local_Host_Edit.toPlainText()
        local_port = int(self.Local_Port_Edit.toPlainText())
        remote_host = self.Remote_Host_Edit.toPlainText()
        remote_port = int(self.Remote_Port_Edit.toPlainText())

        receive_first = self.RF_checkBox.checkState()

        if(local_host is not None and local_port is not None
           and remote_host is not None and remote_port is not None):
            if receive_first is 2:
                receive_first = True
            else:
                receive_first = False
            # start server
            self.server_loop(local_host, local_port, remote_host, remote_port, receive_first)
        else:
            if local_host is None:
                self.setTextToDataEdit("local_host empty")
            if local_port is None:
                self.setTextToDataEdit("local_port empty")
            if remote_host is None:
                self.setTextToDataEdit("remote_host empty")
            if remote_port is None:
                self.setTextToDataEdit("remote_port empty")

class Proxy_thread(QThread, ProxyWindow):
    def __init__(self, client_socket, remote_host, remote_port, receive_first):
        QThread.__init__(self)
        super(ProxyWindow, self).__init__
        self.client_socket = client_socket
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.receive_first = receive_first
    def __del__(self):
        self.wait()

    def receive_from(self, connection):
        buffer = ""

        connection.settimeout(2)

        try:
            while True:
                data = connection.recv(4096)

                if not data:
                    break
                buffer += data
        except:
            pass
        return buffer

    def response_handler(self, buffer):
        self.setTextToDataEdit(buffer)
        while True:
            if self.Forward_Button.isFlat() is True:
                break
        return buffer

    def request_handler(self, buffer):
        self.setTextToDataEdit(buffer)
        while True:
            if self.Forward_Button.isFlat() is True:
                break
            if self.Drop_Button.isFlat() is True:
                buffer = ""
        return buffer

    def hexdump(self, src, length=16):
        result = []
        digits = 4 if isinstance(src, unicode) else 2

        for i in xrange(0, len(src), length):
            s = src[i:i + length]
            hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
            text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
            result.append(b"%04X   %-*s   %s" % (i, length * (digits + 1), hexa, text))

        print b'\n'.join(result)

    def proxy_handler(self, client_socket, remote_host, remote_port, receive_first):
        # connect to remote host
        self.remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.remote_socket.connect((remote_host, remote_port))

        # receive data from remote host if necesarry
        if receive_first:
            remote_buffer = self.receive_from(self.remote_socket)
            self.hexdump(remote_buffer)

        # send buffer to response handler
        remote_buffer = self.response_handler(remote_buffer)

        if len(remote_buffer):
            client_socket.send(remote_buffer)

        # localhsot <--> remotehost
        while True:

            local_buffer = self.receive_from(client_socket)

            if len(local_buffer):
                self.hexdump(local_buffer)

                local_buffer = self.request_handler(local_buffer)

                self.remote_socket.send(local_buffer)


            remote_buffer = self.receive_from(self.remote_socket)

            if len(remote_buffer):

                self.hexdump(remote_buffer)

                remote_buffer = self.response_handler(remote_buffer)

                client_socket.send(remote_buffer)



            if not len(local_buffer) or len(remote_buffer):
                client_socket.close()
                self.remote_socket.close()
                self.setTextToDataEditN("[END] No more data Closing Connetion!")
                break
        return

    def run(self):
        self.proxy_handler(self.client_socket, self.remote_host, self.remote_port, self.receive_first)
def main():
    app = QApplication(sys.argv)
    window = ProxyWindow()
    window.show()
    sys.exit(app.exec_())

main()