#coding=gbk
import traceback
import json
import time
import sys
from PyQt5 import QtCore, QtWidgets, QtNetwork


class ServerBase(QtCore.QObject):
    """
    ����������
    """
    PORT = 20201  #�˿�
    HEADER_SIZE = 10

    def __init__(self, parent):
        super(ServerBase, self).__init__(parent)

        self.port = self.__class__.PORT
        self.initialize()

    def initialize(self):
        """
        ����������ʵ��
        :return:
        """
        self.server = QtNetwork.QTcpServer(self)
        self.server.newConnection.connect(self.establish_connection)  #�µĿͻ������ӵ�������ʱ����

        if self.listen():
            print('[log] �˿ڣ�{}�����ɹ�'.format(self.port))
        else:
            print('[error] ����ʧ��')

    def listen(self):
        """
        ���������Ƿ��ڼ��������û����ʼ����
        :return: True:����������
                 False:��������ʧ��
        """
        if not self.server.isListening():  #��������ǰ�Ƿ�����������������
            #����TCP����������ʹ�俪ʼ����ָ����IP��ַ�Ͷ˿�
            return self.server.listen(QtNetwork.QHostAddress.LocalHost, self.port)  #��ַ���˿ڡ�true�ɹ��ر������򷵻�false.

        return True

    def establish_connection(self):
        """
        ������������ʱ���������׽��ֵ�����
        :return:
        """
        self.socket = self.server.nextPendingConnection()  #������һ�����������QTcpSocket����
        if self.socket.state() == QtNetwork.QTcpSocket.ConnectedState:  #���׽���״̬Ϊ������״̬ʱ
            self.socket.disconnected.connect(self.on_disconnect)  #���׽�����ͻ��˶Ͽ�����ʱ����
            self.socket.readyRead.connect(self.read)  #���׽��ֽ��յ��µ�����ʱ���ͻᴥ������ź�
            print('[log] ���ӳɹ�')

    def on_disconnect(self):
        self.socket.disconnected.disconnect()  #�Ͽ��źŲ۵�����
        self.socket.readyRead.disconnect()

        self.socket.deleteLater()  #ɾ���׽���
        print('[log] �Ͽ�����')

    def read(self):
        """
        ��ȡ�ӿͻ��˷��͹��������ݣ���Ҫ��������ʵ�֡�
        :return:
        """
        bytes_remaining = -1
        json_data = ''

        while self.socket.bytesAvailable():  #��ȡ��ǰ�׽��ֻ������пɹ���ȡ���ֽ���
            if bytes_remaining <= 0:  #ͷ��
                bytes_array = self.socket.read(ServerBase.HEADER_SIZE)  #���׽����ж�ȡָ���������ֽ�����
                if not isinstance(bytes_array, QtCore.QByteArray):  #��pyqt�з���bytes����pyside�з���QByteArray
                    #ֻ��QByteArray�в���toInt���������������int.from_bytes(bytes_array, byteorder='big')��bytesתΪint
                    bytes_array = QtCore.QByteArray(bytes_array)

                bytes_remaining, valid = bytes_array.toInt()  #������תΪʮ���Ƶ����������أ�ת�����ֵ��ת���Ƿ�ɹ�
                if not valid:  #ת���ɹ�˵���׽�����Ԥ���ڵ���Ϣ����ʼ�����岿�֣�ʧ��˵��������Ҫ����Ϣ��������ж�
                    bytes_remaining = -1
                    self.write_error('��Ч��ͷ')
                    self.socket.readAll()  #��ȡ�׽��ֻ������е����п�������
                    return

            if bytes_remaining > 0:  #����
                bytes_array = self.socket.read(bytes_remaining)  #������ֽ��Ƿ��Ͷ˷����Լ��������Ϸ���ͷ����ó�
                if not isinstance(bytes_array, QtCore.QByteArray):  #��pyqt�з���bytes����pyside�з���QByteArray
                    #������str����bytes_arrayתΪ���Ա�len������
                    bytes_array = QtCore.QByteArray(bytes_array)

                bytes_remaining -= len(bytes_array)  #��ȡ������ȷʱ������Ӧ����0
                json_data += bytes_array.data().decode()  #��ȡ����

                if bytes_remaining == 0:
                    bytes_remaining = -1  #��ǰ�ζ�ȡ�ɹ��󣬽���ȡ״̬���·���Ϊ-1���Ա��������

                    data = json.loads(json_data)  #���ֵ��ȡ����
                    self.process_data(data)
                    json_data = ''

    def write(self, reply):
        """
        ��ͻ���д�����ݣ���Ҫ��������ʵ�֡�
        :return:
        """
        json_reply = json.dumps(reply)  #�ֵ�תjson��ʽ
        if self.socket.state() == QtNetwork.QTcpSocket.ConnectedState:
            header = '{}'.format(len(json_reply.encode())).zfill(ServerBase.HEADER_SIZE)  #�׽��ֱ�ͷ����Ϣ����
            data = QtCore.QByteArray('{}{}'.format(header, json_reply).encode())  #����ͷ����Ϣ����ƴ��

            self.socket.write(data)  #��QByteArrayת��Ϊint

    def write_error(self, error_msg):
        reply = {'success': False,
                 'msg': error_msg}

        self.write(reply)

    def process_data(self, data):
        """
        ���÷����׽��ֵ�����
        :param data:�׽��ֱ����ֵ�
        :return:
        """
        reply = {'success': False}#Ҫ���ظ��ͻ��˵��׽����ֵ�

        cmd = data['cmd']  #��ȡ�ֵ��е���������
        if cmd == 'ping':  #�����ping�����Ƿ���ͨ����ֱ�����÷�������Ϊtrue
            reply['success'] = True
        else:
            self.process_cmd(cmd, data, reply)
            if not reply['success']:  #����Խ��յ���Ϣ������Ϊfalse��ʾ����ʧ��
                reply['cmd'] = cmd
                if 'msg' not in reply.keys():  #��������������
                    reply['msg'] = u'δ֪����'

        self.write(reply)

    def process_cmd(self, cmd, data, reply):
        """
        ����Ϣ������Ԥ��ʱ������������msg��Ϣ�����������ӡ����
        ��Ȼû�з���ֵ��������ֱ���޸ĵ�reply�ֵ䣬�����ⲿ�ֵ������ֱ�ӱ��޸�
        :param cmd: �׽����ֵ���cmd���������
        :param data: �׽��������ֵ�
        :param reply: �����������׽����Ƿ�ɹ����ֵ�
        :return:
        """
        reply['msg'] = '��Ч������({})'.format(cmd)  #��Ч����


class ExampleServer(ServerBase):
    """
    �������̳��࣬һ�����ⲿ�Ի���̳�ʹ��
    """
    PORT = 20201

    def __init__(self, parent_window):
        """
        ���е���initʱ�Զ����û����init����ʼ���������ṩ�Ķ˿�
        ���յ��׽��ֲ�����process_cmd����ʱ�����ȵ��ø����process_cmd����
        :param parent_window: �������ڶ���
        """
        super(ExampleServer, self).__init__(parent_window)

        self.window = parent_window

    def process_cmd(self, cmd, data, reply):
        """
        ��д����ĸ÷���
        :param cmd:�׽����ֵ���cmd���������
        :param data:�׽��������ֵ�
        :param reply:�����������׽����Ƿ�ɹ����ֵ�
        :return:
        """
        if cmd == 'echo':
            self.echo(data, reply)
        elif cmd == 'set_title':
            self.set_tite(data, reply)
        elif cmd == 'sleep':
            self.sleep(reply)
        else:  #�����յ���Ϣ��Ԥ��֮�⣬��̳л���÷��������ݣ�������Ч����
            super(ExampleServer, self).process_cmd(cmd, data, reply)

    def echo(self, data, reply):
        reply['result'] = data['text']
        reply['success'] = True

    def set_tite(self, data, reply):
        """
        ���ø������ڵı��⣨�׽������ݵ�ȡ����������
        :param data: �׽��������ֵ�
        :param reply: �����������׽����Ƿ�ɹ����ֵ�
        :return:
        """
        self.window.setWindowTitle(data['title'])

        reply['result'] = True
        reply['success'] = True

    def sleep(self, reply):
        """
        ��ͣ��Ӧ�������׽������ݵ�ȡ����������
        :param data: �׽��������ֵ�
        :param reply: �����������׽����Ƿ�ɹ����ֵ�
        :return:
        """
        for i in range(6):
            print('Sleeping {}'.format(i))
            time.sleep(1)

        reply['result'] = True
        reply['success'] = True


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    win = QtWidgets.QDialog()
    win.setWindowTitle('��������')
    win.setFixedSize(240, 150)
    QtWidgets.QPlainTextEdit(win)

    server = ExampleServer(win)

    win.show()

    app.exec_()
