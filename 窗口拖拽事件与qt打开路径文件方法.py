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

class CustomTextEditor(QtWidgets.QPlainTextEdit):
    def __init__(self, parent=None):
        super(CustomTextEditor, self).__init__(parent)

    def set_drop_enabled(self, enabled):
        self.setAcceptDrops(enabled)

    def dragEnterEvent(self, drag_event):
        #有拖拽到控件内时触发
        mime_data = drag_event.mimeData()
        #if mime_data.hasFormat('text/plain') or mime_data.hasFormat('text/uri-list'):#限定可被拖拽的内容，此时只能拖拽纯文本
        if mime_data.hasText() or mime_data.hasUrls():#此时可以拖拽文本和文件
            drag_event.acceptProposedAction()

    def dragLeaveEvent(self, drag_event):
        #当拖拽拖拽时鼠标移出控件
        print 22

    def dragMoveEvent(self, drag_event):
        #拖拽在控件中移动时触发
        drag_event.setAccepted(drag_event.pos().x() < 100)#当鼠标位置在控件中的位置x轴小于100时可以放下，否则不能拖入
    
    def dropEvent(self, drop_event):
        #当拖拽对象被放入控件时
        if drop_event.mimeData().hasUrls():#当拖入的是文件或文件夹时
            urls = drop_event.mimeData().urls()#获取拖入对象的路径（是个列表，里面是QtCore.QUrl类型的路径）
            file_path = urls[0].toLocalFile()#获取拖入对象列表里第一个文件的路径
            self.open_file(file_path)
        super(CustomTextEditor, self).dropEvent(drop_event)

    def open_file(self, file_path):
        if file_path:
            file_info = QtCore.QFileInfo(file_path)#将路径转为QtCore.QFileInfo类型
            if file_info.exists() and file_info.isFile():#当文件路径存在且文件存在时
                f = QtCore.QFile(file_info.absoluteFilePath())#拿到这个路径里指定的文件对象，类型为QtCore.QFile
                if f.open(QtCore.QFile.ReadOnly | QtCore.QFile.Text):#打开文件，读取里面所有文本内容
                    text_stream = QtCore.QTextStream(f)
                    text_stream.setCodec('UTF-8')#用万国码读取
                    text = text_stream.readAll()
                    f.close()

                    self.setPlainText(text)

class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.editor = CustomTextEditor()


    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(self.editor)

    def create_connections(self):
        pass


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TestWindow()
        my_window.show()