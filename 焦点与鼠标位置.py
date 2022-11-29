# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class LineEdit(QtWidgets.QLineEdit):
    def __init__(self, parent=None):
        super(LineEdit, self).__init__(parent)

    def focusInEvent(self, focus_event):
        #�������ڸÿؼ�����ʱ
        print '1'

    def focusOutEvent(self, focus_event):
        #�������뿪�ÿؼ�ʱ
        print '2'

class ColorChangeWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(ColorChangeWidget, self).__init__(parent)

        self.setFixedSize(24, 24)
        self.color = QtCore.Qt.red

    def enterEvent(self, event):
        #����ڿؼ���ʱ
        self.color = QtCore.Qt.blue
        self.update()

    def leaveEvent(self, event):
        #��겻�ڿؼ���ʱ
        self.color = QtCore.Qt.red
        self.update()

    def paintEvent(self, paint_envent):
        painter = QtGui.QPainter(self)
        painter.fillRect(paint_envent.rect(), self.color)


class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle(u'����̧ͷ')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.lab_name = QtWidgets.QLabel(u'����')
        self.line_edit = LineEdit()
        self.but_color = ColorChangeWidget()

        self.but_hide = QtWidgets.QPushButton(u'����')

    def create_layout(self):
        self.hori_layout = QtWidgets.QHBoxLayout()
        self.vert_layout = QtWidgets.QVBoxLayout()

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.but_color)
        button_layout.addStretch()
        button_layout.addWidget(self.but_hide)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(self.hori_layout)
        main_layout.addLayout(self.vert_layout)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.but_hide.clicked.connect(self.hide)

    def showEvent(self, show_eent):
        print '�򿪴���'

    def hideEvent(self, hide_event):
        print '����'

    def closeEvent(self, close_event):
        if self.isVisible():
            #��ͨ��
            reply = QtWidgets.QMessageBox.question(self, u'ȡ��', u'ȷ����')
            if reply == QtWidgets.QMessageBox.No:
                close_event.ignore()

            '''����1��
            quitMsgBox = QtWidgets.QMessageBox(self)
            quitMsgBox.setWindowTitle(u'ȷ����ʾ')
            quitMsgBox.setText(u'ȷ���˳���')
            quitMsgBox.setStandardButtons(QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            but_yes = quitMsgBox.button(QtWidgets.QMessageBox.Yes)
            but_yes.setText(u'ȷ��')
            but_No = quitMsgBox.button(QtWidgets.QMessageBox.No)
            but_No.setText(u'ȡ��')
            quitMsgBox.exec_()
            if quitMsgBox.clickedButton() == but_yes:
                close_event.accept()#�ر������Ӧ��
            else:
                close_event.ignore()#���Թر��¼�'''

            '''����2��
            quitMsgBox = QtWidgets.QMessageBox(self)
            quitMsgBox.setWindowTitle(u'ȷ����ʾ')
            quitMsgBox.setText(u'ȷ���˳���')
            but_yes = QtWidgets.QPushButton(u'ȷ��')
            but_No = QtWidgets.QPushButton(u'ȡ��')
            quitMsgBox.addButton(but_yes, QtWidgets.QMessageBox.YesRole)
            quitMsgBox.addButton(but_No, QtWidgets.QMessageBox.NoRole)
            quitMsgBox.exec_()
            if quitMsgBox.clickedButton() == but_yes:
                close_event.accept()
            else:
                close_event.ignore()'''


    def resizeEvent(self, resize_event):
        if resize_event.size().width() > 250:
            self.hori_layout.addWidget(self.lab_name)
            self.hori_layout.addWidget(self.line_edit)
        else:
            self.vert_layout.addWidget(self.lab_name)
            self.vert_layout.addWidget(self.line_edit)


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()