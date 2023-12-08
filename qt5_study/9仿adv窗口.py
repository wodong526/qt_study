try:
    from PyQt5.QtWidgets import *
    from PyQt5.QtCore import *
    from PyQt5.QtGui import *
except:
    from PySide2.QtWidgets import *
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    import maya.cmds as mc

import sys
import json
import logging
from functools import partial

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


class myButton(QWidget):
    try:
        clicked = pyqtSignal()
    except:
        clicked = Signal()

    def __init__(self, id, parent=None):
        super(myButton, self).__init__(parent)
        self._id = id  #图片名称
        self._obj = None  #该按钮对应的控制器名
        self._is_select = False
        self._is_keys = False
        self._set_state = 'normal'  #'normal为正常显示、‘light’为高亮、‘enter’为按下’、‘gray’为灰色

        self._pix_info = {'color_normal': self.get_pix('OffK0'),  #正常显示
                          'select_normal': self.get_pix('OnK0'),  #对象被选中时
                          'key_normal': self.get_pix('OffK1'),  #对象有被k帧时
                          'all_normal': self.get_pix('OnK1')}  #既被选中又有k帧
        self.setFixedSize(self._pix_info['color_normal'].size())
        self.setMask(self._pix_info['color_normal'].mask())  #按钮默认是矩形，做一个遮罩让按钮和图片有效内容一样的范围

    def get_pix(self, typ):
        path = 'F:/qt5_open/data/image/{}_{}.png'.format(self._id, typ)
        return QPixmap(path)

    def set_obj(self, obj):
        self._obj = obj
        self.update()

    def set_is_select(self, sel_bool):
        self._is_select = sel_bool

    def set_is_keys(self, keys_bool):
        self._is_keys = keys_bool

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        is_transparent = None
        transparent_pix = QPixmap(self.size())

        if self._obj is None:  #没有添加预设时
            if self._set_state == 'normal':  #鼠标没碰到控件
                pix = self._pix_info['color_normal']
                is_transparent = 3
            elif self._set_state == 'light':  #鼠标放到控件上
                pix = self._pix_info['color_normal']
                is_transparent = 1
            else:  #鼠标按下
                pix = self._pix_info['color_normal']
                is_transparent = 2
        else:#已经添加预设时
            if self._is_select and self._is_keys:#选择和k帧都开启时
                pix = self._pix_info['all_normal']
            elif self._is_select:#选择开启时
                pix = self._pix_info['select_normal']
            elif self._is_keys:#k帧开启时
                pix = self._pix_info['key_normal']
            else:#都没开启时
                if self._set_state == 'normal':  #鼠标没碰到控件
                    pix = self._pix_info['color_normal']
                elif self._set_state == 'light':  #鼠标放到控件上
                    pix = self._pix_info['color_normal']
                    is_transparent = 1
                else:  #鼠标按下
                    pix = self._pix_info['color_normal']
                    is_transparent = 2

        p.drawPixmap(self.rect(), pix)
        if is_transparent == 1:
            transparent_pix.fill(QColor(255, 255, 255, 100))
            p.drawPixmap(self.rect(), transparent_pix)
        elif is_transparent == 2:
            transparent_pix.fill(QColor(0, 0, 0, 50))
            p.drawPixmap(self.rect(), transparent_pix)
        elif is_transparent == 3:
            transparent_pix.fill(QColor(0, 0, 0, 150))
            p.drawPixmap(self.rect(), transparent_pix)

        p.end()

    def enterEvent(self, event):  #鼠标进入控件时
        self._set_state = 'light'
        self.update()

    def leaveEvent(self, event):  #鼠标离开控件时
        self._set_state = 'normal'
        self.update()

    def mousePressEvent(self, event):  #鼠标按下控件时
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
            if self.rect().contains(event.pos()):  #鼠标是否在控件内，有可能鼠标按下不放然后拖出控件
                self._set_state = 'enter'
            else:
                self._set_state = 'normal'
            self.update()
        else:
            super(myButton, self).mousePressEvent(event)#将除开点击左键外的信息继续用父类QWidget的mousePressEvent函数运行，以便达到右键移动窗口

    def mouseReleaseEvent(self, event):  #鼠标松开控件时
        if event.button() == Qt.LeftButton:
            self._set_state = 'light'
            self.update()
        else:
            super(myButton, self).mouseReleaseEvent(event)

class PickerUi(QWidget):
    def __init__(self, parent=None):
        super(PickerUi, self).__init__()
        self.setFixedSize(320, 240)

        with open('F:/qt5_open/test.json', 'r') as f:
            self.result = json.load(f)  #读取json，result是返回的字典

        self.button_lis = []
        for id, pos in self.result.items():
            but = myButton(id, self)
            but.move(*pos)
            but.clicked.connect(partial(self._on_but_clicked, parent, but))
            self.button_lis.append(but)

    def _on_but_clicked(self, p, but):
        if p._is_edit_mode:  #当前为编辑预设时
            sel = mc.ls(sl=True)
            if sel:
                if mc.nodeType(mc.listRelatives(sel[0], s=True)[0]) == 'nurbsCurve':
                    but.set_obj(sel[0])
                else:
                    log.warning('选中对象不是控制器类型。')
            else:
                log.warning('没有选中有效对象。')
        else:  #当前为选择控制器时
            if but._obj:
                mc.select(but._obj)
            else:
                log.error('该按键没有对应控制器。')

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        #设置背景颜色
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(Qt.darkGray))
        p.drawRect(self.rect())

        #设置背景图片
        pix = QPixmap('F:/qt5_open/data/biped_background.png')
        p.drawPixmap(self.rect(), pix)

        p.end()

class Picker:
    def __init__(self):
        self._is_edit_mode = False

        self._ui = PickerUi(self)

    def clear_all_objs(self):
        for but in self._ui.button_lis:
            but.set_obj(None)

    def set_eit_mode(self, bool_value):
        self._is_edit_mode = bool_value

    def set_select_vis(self, obj):
        self.set_all_no_select_vis()
        obj._is_select = True
        obj.update()

    def set_all_no_select_vis(self):
        for but in self._ui.button_lis:
            but._is_select = False
        self._ui.update()

    def set_keys_vis(self, obj):
        obj._is_keys = True
        obj.update()

    def set_all_no_keys_vis(self):
        for but in self._ui.button_lis:
            but._is_keys = False
        self._ui.update()

    def export_data(self):
        data = {}
        for but in self._ui.button_lis:
            data[but._id] = but._obj

        result = QFileDialog.getSaveFileName(None, u'选择保存文件', 'F:/qt5_open/data/ctl_data.json', '(*.json)')#获取导出fbx路径
        if result[0]:
            with open(result[0], 'w') as f:
                json.dump(data, f, indent=4)  #写入json，mat_dir是要写入的字典
        else:
            log.warning('没有选择有效对象。')

    def import_data(self):
        result = QFileDialog.getOpenFileName(None, '选择控制器预设文件', 'F:/qt5_open/data/', '(*.json)')
        if result[0]:
            with open(result[0], 'r') as f:
                ctr_dir = json.load(f)  #读取json，result是返回的字典

            for but in self._ui.button_lis:
                but.set_obj(ctr_dir[but._id])
        else:
            log.warning('没有选中有效对象，请重新指定路径')

    def get_ui(self):
        return self._ui

class ToolBarUi(QWidget):
    def __init__(self, parent=None):
        super(ToolBarUi, self).__init__(parent)
        self.setFixedSize(150, 240)

        self.cbx_edit_mode = QCheckBox('编辑模式')
        self.cbx_select = QCheckBox('显示选择')
        self.cbx_key = QCheckBox('显示k帧')

        self.but_clear_all = QPushButton('清空当前预设')
        self.but_clear_all.setEnabled(False)
        self.but_import = QPushButton('导入预设')
        self.but_export = QPushButton('导出预设')
        self.but_close = QPushButton('关闭窗口')

        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.cbx_edit_mode)
        main_layout.addWidget(self.cbx_select)
        main_layout.addWidget(self.cbx_key)
        main_layout.addWidget(self.but_clear_all)
        main_layout.addWidget(self.but_import)
        main_layout.addWidget(self.but_export)
        main_layout.addStretch()
        main_layout.addWidget(self.but_close)

    def paintEvent(self, event):
        p = QPainter()
        p.begin(self)
        p.setPen(Qt.NoPen)
        p.setBrush(QBrush(Qt.lightGray))
        p.drawRect(self.rect())

class ToolBar:
    def __init__(self):
        self._ui = ToolBarUi()

    def get_ui(self):
        return self._ui

class MainWindow(QWidget):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle('拉拉')
        self.resize(1, 1)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint | self.windowFlags() | Qt.FramelessWindowHint)#窗口置顶且无边框

        self.scriptJob_lis = []

        self._last_mouse_pos = None#鼠标移动起始点
        self._current_mouse_pos = None#鼠标移动结束点
        self._is_moving = False#鼠标是否在移动状态下

        self.picker = Picker()
        self.picker_ui = self.picker.get_ui()

        self.toolbar = ToolBar()
        self.toolbar_ui = self.toolbar.get_ui()

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addWidget(self.picker_ui)
        main_layout.addWidget(self.toolbar_ui)

        self.toolbar_ui.cbx_edit_mode.stateChanged.connect(self._setup_edit_mode)#打开编辑模式
        self.toolbar_ui.cbx_select.stateChanged.connect(self.is_select)#是否显示选择对象
        self.toolbar_ui.cbx_key.stateChanged.connect(self.is_keys)#是否显示k帧对象
        self.toolbar_ui.but_clear_all.clicked.connect(self.picker.clear_all_objs)#清空预设
        self.toolbar_ui.but_import.clicked.connect(self.picker.import_data)
        self.toolbar_ui.but_export.clicked.connect(self.picker.export_data)#导出预设
        self.toolbar_ui.but_close.clicked.connect(self.close)#关闭窗口

        self.add_scriptJob()

    def _setup_edit_mode(self):
        state = self.toolbar_ui.cbx_edit_mode.isChecked()
        self.picker.set_eit_mode(state)
        self.toolbar_ui.but_clear_all.setEnabled(state)

    def is_select(self):#当选中对象且选择复选框打开时，查选择对象是否已被加载，是就改变图标，空选或复选框关闭时清除所有绿色图标
        sel = mc.ls(sl=True)[0]
        if sel and self.toolbar_ui.cbx_select.isChecked():
            for but in self.picker_ui.button_lis:
                if sel == but._obj:
                    self.picker.set_select_vis(but)
        else:
            self.picker.set_all_no_select_vis()

        self.is_keys()

    def is_keys(self):
        if self.toolbar_ui.cbx_key.isChecked():
            self.picker.set_all_no_keys_vis()
            for but in self.picker_ui.button_lis:
                if but._obj and mc.keyframe(but._obj, iv=True, q=True):
                    self.picker.set_keys_vis(but)
        else:
            self.picker.set_all_no_keys_vis()


    def add_scriptJob(self):
        self.scriptJob_lis.append(mc.scriptJob(e=('SelectionChanged', partial(self.is_select))))#添加选择变化的信号

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self._last_mouse_pos = QCursor.pos()
            self._is_moving = True

    def mouseMoveEvent(self, event):
        if self._is_moving:
            self._current_mouse_pos = QCursor.pos()
            delta = self._current_mouse_pos - self._last_mouse_pos
            self.move(delta + self.pos())
            self._last_mouse_pos = self._current_mouse_pos

    def mouseReleaseEvent(self, event):
        self._last_mouse_pos = None
        self._current_mouse_pos = None
        self._is_moving = False

    def closeEvent(self, event):
        super(MainWindow, self).closeEvent(event)
        for job in self.scriptJob_lis:
            mc.scriptJob(k=job)

if __name__ == '__main__':  #__name__是模块的一个属性，代表模块的名字，运行时它为程序的主入口，即为__main__
    #使窗口支持高分辨率缩放，必须写到QApplication(sys.argv)前面，Maya中无法设置，pyqt5.6后才有
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app = QApplication(sys.argv)
    #sys.argv储存当前运行的字符串
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())

