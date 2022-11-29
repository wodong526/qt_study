# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.mel as mm
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)

class TimelineOverlay(QtWidgets.QWidget):
    def __init__(self):
        self.time_control = mm.eval('$tempVar = $gPlayBackSlider')
        time_control_ptr = omui.MQtUtil.findControl(self.time_control)
        time_control_widget = wrapInstance(int(time_control_ptr), QtWidgets.QWidget)
        super(TimelineOverlay, self).__init__(time_control_widget)

        self.keyFrame_color = QtGui.QColor(QtCore.Qt.green)
        self.frame_time = [1, 5, 26, 73, 100]

    def add_frame(self):
        current_time = mc.currentTime(q=True)#查询当前帧
        if current_time not in self.frame_time:#当当前帧不在已设置绘图的帧列表时
            self.frame_time.append(current_time)#将当前帧加入到绘图列表
            self.update()#刷新画板
        else:
            print '当前帧已有绘图事件。'

    def add_frames(self):#批量添加帧
        current_times = self.get_rangeTime()
        for frame in range(current_times[0], current_times[1]):
            if frame not in self.frame_time:  # 当当前帧不在已设置绘图的帧列表时
                self.frame_time.append(frame)  # 将当前帧加入到绘图列表
            else:
                print '帧{}已有绘图事件。'.format(frame)
        self.update()  # 刷新画板

    def remove_frame(self):
        current_time = mc.currentTime(q=True)
        if current_time in self.frame_time:#当当前帧在已设置绘图的帧列表时
            self.frame_time.remove(current_time)#将当前帧移出到绘图列表
            self.update()
        else:
            print '当前帧没有绘图事件。'

    def remove_frames(self):#批量删除帧
        current_times = self.get_rangeTime()
        for frame in range(current_times[0], current_times[1]):
            if frame in self.frame_time:  # 当当前帧不在已设置绘图的帧列表时
                self.frame_time.remove(frame)  # 将当前帧加入到绘图列表
                print '已删除帧{}上的绘图事件。'.format(frame)
        self.update()  # 刷新画板

    def get_rangeTime(self):#获取选中的帧范围
        sel_frames = mc.timeControl(self.time_control, q=True, ra=True)
        return [int(sel_frames[0]), int(sel_frames[1])]

    def set_context_menu_enabled(self, enabled):
        self.context_menu_enabled = enabled
        if enabled:
            print 3

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:#鼠标右键按下时
            if self.context_menu_enabled:
                context_menu = QtWidgets.QMenu()
                title_action = context_menu.addAction(u'时间线覆盖')
                title_action.setDisabled(True)
                context_menu.addSeparator()

                action = context_menu.addAction(u'添加帧')
                action.triggered.connect(self.add_frame)

                action = context_menu.addAction(u'在选中范围内添加帧')
                action.triggered.connect(self.add_frames)

                context_menu.addSeparator()#添加分割线

                action = context_menu.addAction(u'删除帧')
                action.triggered.connect(self.remove_frame)

                action = context_menu.addAction(u'在选中范围内删除所有帧')
                action.triggered.connect(self.remove_frames)


                context_menu.exec_(self.mapToGlobal(mouse_event.pos()))

                return
        mouse_event.ignore()

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:#鼠标右键松开时
            if self.context_menu_enabled:
                return
        mouse_event.ignore()

    def paintEvent(self, paint_event):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())#将控件大小与时间轴的大小做关联 控件大小将会随着时间轴的缩放而跟着缩放
            range_start = mc.playbackOptions(q=True, minTime=True)#时间轴下限
            range_end = mc.playbackOptions(q=True, maxTime=True)#时间轴上限
            displayed_frmae_count = range_end - range_start + 1

            padding = self.width() * 0.005#时间轴结尾有一段多余的距离
            frame_width = (self.width() * 0.99) / displayed_frmae_count#时间轴每帧的宽度

            frame_height = 0.333 * self.height()
            frame_y = self.height() - frame_height#控件要显示的高度

            painter = QtGui.QPainter(self)#实例化画布,画布位置为整个时间滑块
            pen = painter.pen()#实例化画笔
            pen.setWidth(1)#画笔宽度
            pen.setColor(self.keyFrame_color)#画笔颜色
            painter.setPen(pen)#将画布与画布匹配

            fill_color = QtGui.QColor(self.keyFrame_color)
            fill_color.setAlpha(63)

            for frame_time in self.frame_time:
                frame_x = padding + ((frame_time - range_start) * frame_width) + 0.5#画笔要画的位置

                painter.fillRect(frame_x, frame_y, frame_width, frame_height, fill_color)#绘制
                painter.drawRect(frame_x, frame_y, frame_width, frame_height)#绘制形状为矩形，矩形尺寸为这些参数


class TimelineOverlayDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TimelineOverlayDialog, self).__init__(parent)

        self.setWindowTitle(u'窗口抬头')
        if mc.about(ntOS=True):  # 判断系统类型
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # 删除窗口上的帮助按钮
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.timeline_overlay = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.cbx_overlay_visible = QtWidgets.QCheckBox(u'打开')
        self.cbx_context_menu = QtWidgets.QCheckBox(u'按钮')
        self.cbx_context_menu.setChecked(True)

        self.but_add_frame = QtWidgets.QPushButton(u'添加')
        self.but_remove_frame = QtWidgets.QPushButton(u'删除')

        self.but_close = QtWidgets.QPushButton(u'关闭')

    def create_layout(self):
        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.setSpacing(1)
        frame_layout.addWidget(self.but_add_frame)
        frame_layout.addWidget(self.but_remove_frame)
        frame_layout.addStretch()

        overlay_layout = QtWidgets.QVBoxLayout()
        overlay_layout.addWidget(self.cbx_overlay_visible)
        overlay_layout.addWidget(self.cbx_context_menu)
        overlay_layout.addLayout(frame_layout)

        options_grp = QtWidgets.QGroupBox(u'集合')
        options_grp.setLayout(overlay_layout)

        but_layout = QtWidgets.QHBoxLayout()
        but_layout.addStretch()
        but_layout.addWidget(self.but_close)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addWidget(options_grp)
        main_layout.addStretch()
        main_layout.addLayout(but_layout)


    def create_connections(self):
        self.cbx_overlay_visible.toggled.connect(self.set_overlay_visible)
        self.but_close.clicked.connect(self.close)

    def set_overlay_visible(self, visible):
        if visible:
            if not self.timeline_overlay:
                self.timeline_overlay = TimelineOverlay()
                self.timeline_overlay.set_context_menu_enabled(self.cbx_context_menu.isChecked())

                self.cbx_context_menu.toggled.connect(self.timeline_overlay.set_context_menu_enabled)
                self.but_add_frame.clicked.connect(self.timeline_overlay.add_frame)
                self.but_remove_frame.clicked.connect(self.timeline_overlay.remove_frame)

        if  self.timeline_overlay:
            self.timeline_overlay.setVisible(visible)

        #self.cbx_overlay_visible.setVisible(visible)

    def closeEvent(self, event):
        if self.timeline_overlay:
            self.timeline_overlay.setParent(None)
            self.timeline_overlay.close()
            self.timeline_overlay.deleteLater()
            self.timeline_overlay = None


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = TimelineOverlayDialog()
        my_window.show()