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
        self.connect(self.Stop_Button, SIGNAL("clicked()"), self.Stop_Proxy)
        self.ErrMsg = ""
        self.proxy_thread = ""
        self.server_loop = ""

    def setTextToDataEdit(self, text):
        self.Data_Edit.setText(text)

    def setTextToDataEditN(self, text):
        self.Data_Edit.append(text)

    def setPauseDataEdit(self, text):
        self.Data_Edit.setText(text)

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
            #self.connect(self.get_thread, SIGNAL("add_post(QString)"), self.add_post)
            self.server_loop = Server_Loop(local_host, local_port, remote_host, remote_port, receive_first)
            self.connect(self.server_loop, SIGNAL("setTextToDataEdit(QString)"), self.setTextToDataEditN)
            #self.connect(self.Forward_Button, SIGNAL("clicked()"), self.server_loop.response_handler)
            #self.connect(self.Forward_Button, SIGNAL("clicked()"), self.server_loop.request_handler)
            self.server_loop.start()

        else:
            if local_host is None:
                self.setTextToDataEdit("local_host empty")
            if local_port is None:
                self.setTextToDataEdit("local_port empty")
            if remote_host is None:
                self.setTextToDataEdit("remote_host empty")
            if remote_port is None:
                self.setTextToDataEdit("remote_port empty")
            return

    def Stop_Proxy(self):
        self.server_loop.terminate()
        self.setTextToDataEdit("Server Stopped")

class Server_Loop(QThread):
    def __init__(self, local_host, local_port, remote_host, remote_port, receive_first):
        QThread.__init__(self)
        self.local_host = local_host
        self.local_port = local_port
        self.remote_host = remote_host
        self.remote_port = remote_port
        self.receive_first = receive_first
        self.server = ""
        self.client_socket = ""
        self.addr = ""
        self.remote_buffer = ""

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
        self.emit(SIGNAL("setTextToDataEdit(QString)"), buffer)
        return buffer

    def request_handler(self, buffer):
        self.emit(SIGNAL("setTextToDataEdit(QString)"), buffer)
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
            self.remote_buffer = self.receive_from(self.remote_socket)
            #self.hexdump(self.remote_buffer)

        # send buffer to response handler
        self.remote_buffer = self.response_handler(self.remote_buffer)

        if len(self.remote_buffer):
            client_socket.send(self.remote_buffer)

        # localhsot <--> remotehost
        while True:

            local_buffer = self.receive_from(client_socket)

            if len(local_buffer):
                #self.hexdump(local_buffer)

                local_buffer = self.request_handler(local_buffer)

                self.remote_socket.send(local_buffer)

            self.remote_buffer = self.receive_from(self.remote_socket)

            if len(self.remote_buffer):
                #self.hexdump(self.remote_buffer)

                self.remote_buffer = self.response_handler(self.remote_buffer)

                client_socket.send(self.remote_buffer)

            if not len(local_buffer) or len(self.remote_buffer):
                client_socket.close()
                self.remote_socket.close()
                #                self.setTextToDataEditN("[END] No more data Closing Connetion!")
                break
        return

    def run(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.server.bind((self.local_host, self.local_port))
        except:
            QMessageBox.critical(None, "Server Loop",
                                 "Server Loop Failed",
                                 QMessageBox.Ok, QMessageBox.NoButton)
            return

        self.server.listen(10)
        self.emit(SIGNAL("setTextToDataEdit(QString)"), "Listening on %s : %d" %(self.local_host, self.local_port))
        #put listening signal

        while True:

            self.client_socket, self.addr = self.server.accept()

            self.proxy_handler(self.client_socket, self.remote_host, self.remote_port, self.receive_first)

def main():
    app = QApplication(sys.argv)
    window = ProxyWindow()
    window.show()
    sys.exit(app.exec_())

main()