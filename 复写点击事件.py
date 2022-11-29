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


class MoveableWidget(QtWidgets.QWidget):
    def __init__(self, x, y, width, height, color, parent=None):
        super(MoveableWidget, self).__init__(parent)

        self.setFixedSize(width, height)
        self.move(x, y)
        self.color = color
        self.original_color = color

        self.move_enabled = False

    def mousePressEvent(self, mouse_event):
        '''
        当鼠标按下时执行
        '''
        #QtCore.Qt.ControlModifier是按下ctrl键
        #if mouse_event.button() == QtCore.Qt.LeftButton and mouse_event.modifiers() == QtCore.Qt.ControlModifier:
        if mouse_event.button() == QtCore.Qt.LeftButton:
            self.initial_pos = self.pos()
            self.global_pos = mouse_event.globalPos()

            self.move_enabled = True

    def mouseReleaseEvent(self, mouse_event):
        '''
        当鼠标释放时执行
        '''
        if self.move_enabled:
            self.move_enabled = False

    def mouseDoubleClickEvent(self, mouse_event):
        '''
        鼠标双击时执行
        '''
        if self.color == self.original_color:
            self.color = QtCore.Qt.yellow
        else:
            self.color = self.original_color

        self.update()#刷新控件，否则改变的颜色不会及时更新

    def mouseMoveEvent(self, mouse_event):
        '''
        鼠标移动时执行
        '''
        if self.move_enabled:
            diff = mouse_event.globalPos() - self.global_pos#记录下鼠标移动后位置与按下时位置的差
            self.move(self.initial_pos + diff)#将控件移动到当前位置加位置差的位置

    def paintEvent(self, paint_event):
        painter = QtGui.QPainter(self)
        painter.fillRect(paint_event.rect(), self.color)

class TestWindow(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TestWindow, self).__init__(parent)

        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumSize(400, 400)


        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.wdt_red = MoveableWidget(100, 100, 24, 24, QtCore.Qt.red, self)
        self.wdt_blue = MoveableWidget(200, 200, 24, 24, QtCore.Qt.blue, self)

    def create_layout(self):
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)

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