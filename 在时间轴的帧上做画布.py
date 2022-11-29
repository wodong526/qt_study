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
        current_time = mc.currentTime(q=True)#��ѯ��ǰ֡
        if current_time not in self.frame_time:#����ǰ֡���������û�ͼ��֡�б�ʱ
            self.frame_time.append(current_time)#����ǰ֡���뵽��ͼ�б�
            self.update()#ˢ�»���
        else:
            print '��ǰ֡���л�ͼ�¼���'

    def add_frames(self):#�������֡
        current_times = self.get_rangeTime()
        for frame in range(current_times[0], current_times[1]):
            if frame not in self.frame_time:  # ����ǰ֡���������û�ͼ��֡�б�ʱ
                self.frame_time.append(frame)  # ����ǰ֡���뵽��ͼ�б�
            else:
                print '֡{}���л�ͼ�¼���'.format(frame)
        self.update()  # ˢ�»���

    def remove_frame(self):
        current_time = mc.currentTime(q=True)
        if current_time in self.frame_time:#����ǰ֡�������û�ͼ��֡�б�ʱ
            self.frame_time.remove(current_time)#����ǰ֡�Ƴ�����ͼ�б�
            self.update()
        else:
            print '��ǰ֡û�л�ͼ�¼���'

    def remove_frames(self):#����ɾ��֡
        current_times = self.get_rangeTime()
        for frame in range(current_times[0], current_times[1]):
            if frame in self.frame_time:  # ����ǰ֡���������û�ͼ��֡�б�ʱ
                self.frame_time.remove(frame)  # ����ǰ֡���뵽��ͼ�б�
                print '��ɾ��֡{}�ϵĻ�ͼ�¼���'.format(frame)
        self.update()  # ˢ�»���

    def get_rangeTime(self):#��ȡѡ�е�֡��Χ
        sel_frames = mc.timeControl(self.time_control, q=True, ra=True)
        return [int(sel_frames[0]), int(sel_frames[1])]

    def set_context_menu_enabled(self, enabled):
        self.context_menu_enabled = enabled
        if enabled:
            print 3

    def mousePressEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:#����Ҽ�����ʱ
            if self.context_menu_enabled:
                context_menu = QtWidgets.QMenu()
                title_action = context_menu.addAction(u'ʱ���߸���')
                title_action.setDisabled(True)
                context_menu.addSeparator()

                action = context_menu.addAction(u'���֡')
                action.triggered.connect(self.add_frame)

                action = context_menu.addAction(u'��ѡ�з�Χ�����֡')
                action.triggered.connect(self.add_frames)

                context_menu.addSeparator()#��ӷָ���

                action = context_menu.addAction(u'ɾ��֡')
                action.triggered.connect(self.remove_frame)

                action = context_menu.addAction(u'��ѡ�з�Χ��ɾ������֡')
                action.triggered.connect(self.remove_frames)


                context_menu.exec_(self.mapToGlobal(mouse_event.pos()))

                return
        mouse_event.ignore()

    def mouseReleaseEvent(self, mouse_event):
        if mouse_event.button() == QtCore.Qt.RightButton:#����Ҽ��ɿ�ʱ
            if self.context_menu_enabled:
                return
        mouse_event.ignore()

    def paintEvent(self, paint_event):
        parent = self.parentWidget()
        if parent:
            self.setGeometry(parent.geometry())#���ؼ���С��ʱ����Ĵ�С������ �ؼ���С��������ʱ��������Ŷ���������
            range_start = mc.playbackOptions(q=True, minTime=True)#ʱ��������
            range_end = mc.playbackOptions(q=True, maxTime=True)#ʱ��������
            displayed_frmae_count = range_end - range_start + 1

            padding = self.width() * 0.005#ʱ�����β��һ�ζ���ľ���
            frame_width = (self.width() * 0.99) / displayed_frmae_count#ʱ����ÿ֡�Ŀ��

            frame_height = 0.333 * self.height()
            frame_y = self.height() - frame_height#�ؼ�Ҫ��ʾ�ĸ߶�

            painter = QtGui.QPainter(self)#ʵ��������,����λ��Ϊ����ʱ�们��
            pen = painter.pen()#ʵ��������
            pen.setWidth(1)#���ʿ��
            pen.setColor(self.keyFrame_color)#������ɫ
            painter.setPen(pen)#�������뻭��ƥ��

            fill_color = QtGui.QColor(self.keyFrame_color)
            fill_color.setAlpha(63)

            for frame_time in self.frame_time:
                frame_x = padding + ((frame_time - range_start) * frame_width) + 0.5#����Ҫ����λ��

                painter.fillRect(frame_x, frame_y, frame_width, frame_height, fill_color)#����
                painter.drawRect(frame_x, frame_y, frame_width, frame_height)#������״Ϊ���Σ����γߴ�Ϊ��Щ����


class TimelineOverlayDialog(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(TimelineOverlayDialog, self).__init__(parent)

        self.setWindowTitle(u'����̧ͷ')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.timeline_overlay = None

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.cbx_overlay_visible = QtWidgets.QCheckBox(u'��')
        self.cbx_context_menu = QtWidgets.QCheckBox(u'��ť')
        self.cbx_context_menu.setChecked(True)

        self.but_add_frame = QtWidgets.QPushButton(u'���')
        self.but_remove_frame = QtWidgets.QPushButton(u'ɾ��')

        self.but_close = QtWidgets.QPushButton(u'�ر�')

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

        options_grp = QtWidgets.QGroupBox(u'����')
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