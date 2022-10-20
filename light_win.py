# -*- coding:GBK -*-
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui
from shiboken2 import wrapInstance

import maya.cmds as mc
import maya.OpenMayaUI as omui

from functools import partial
import logging

logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class CustomColorButton(QtWidgets.QWidget):
    color_changed = QtCore.Signal(QtGui.QColor)

    def __init__(self, color=QtCore.Qt.white, parent=None):
        '''
        ��Maya��colorSliderGrp�ؼ��ŵ�qt�Ĵ�����
        :param color:
        :param parent:
        '''
        super(CustomColorButton, self).__init__(parent)
        self.setObjectName('mayaColorButton')

        self.create_control()
        self.set_color(color)

    def create_control(self):
        # window = mc.window()
        color_grp = mc.colorSliderGrp()

        self._color_slider_obj = omui.MQtUtil.findControl(color_grp)
        self._color_slider_widget = wrapInstance(int(self._color_slider_obj), QtWidgets.QWidget)
        self._color_slider_widget.setFixedWidth(50)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setObjectName('main_layout')
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._color_slider_widget)

        self._slider_widget = self._color_slider_widget.findChild(QtWidgets.QWidget, 'slider')
        self._slider_widget.hide()

        mc.colorSliderGrp(self.get_full_name(), e=True, cc=partial(self.on_color_changed))

    def get_full_name(self):
        return omui.MQtUtil.fullName(int(self._color_slider_obj))

    def set_color(self, color):
        color = QtGui.QColor(color)
        mc.colorSliderGrp(self.get_full_name(), e=True, rgb=[color.redF(), color.greenF(), color.blueF()])
        #self.on_color_changed()

    def get_color(self):
        color = mc.colorSliderGrp(self.get_full_name(), q=True, rgb=True)
        color = QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)
        return color

    def on_color_changed(self, *args):
        '''
        ��colorSliderGrp����ɫ�仯ʱ�����źŷ�������
        :param args:
        :return:
        '''
        self.color_changed.emit(self.get_color())


class LightItem(QtWidgets.QWidget):
    node_delete = QtCore.Signal(str)

    def __init__(self, shape_nam, parent=None):
        '''
        Ϊÿ���ƹⴴ��������һ������Ϊÿ����Ҫ�޸ĵĿؼ�����scriptJob
        :param shape_nam:
        :param parent:
        '''
        super(LightItem, self).__init__(parent)
        self.setFixedHeight(26)

        self.typ_lis = ['ambientLight', 'areaLight', 'directionalLight', 'pointLight', 'spotLight', 'volumeLight']
        self.noEmit_lis = ['ambientLight']#��Щ�ƹ�û��������;��淴�����ԣ������ɿؼ���jobʱ��Ҫ����
        self.shape = shape_nam
        self.uuid = mc.ls(shape_nam, uid=True)
        self.script_jobs = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

        self.create_script_jobs()

    def create_widgets(self):
        self.but_light_type = QtWidgets.QPushButton()
        self.but_light_type.setFlat(True)  # ����ť�������ɫȥ��
        self.but_light_type.setFixedSize(20, 20)

        self.cbx_visibility = QtWidgets.QCheckBox()
        self.cbx_visibility.setMaximumWidth(15)

        self.lab_transform_nam = QtWidgets.QLabel()
        self.lab_transform_nam.setFixedWidth(120)
        self.lab_transform_nam.setAlignment(QtCore.Qt.AlignCenter)

        self.dubSpin_intensity = QtWidgets.QDoubleSpinBox()
        self.dubSpin_intensity.setMaximumWidth(40)
        self.dubSpin_intensity.setRange(0.0, 100.0)
        self.dubSpin_intensity.setDecimals(3)  # С��λ
        self.dubSpin_intensity.setSingleStep(0.1)  # ����
        self.dubSpin_intensity.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)  # ȡ����ͷ

        self.but_color = CustomColorButton()

        if self.get_lightType() not in self.noEmit_lis:
            self.cbx_diffuse = QtWidgets.QCheckBox()
            self.cbx_diffuse.setMaximumWidth(15)
            self.cbx_specular = QtWidgets.QCheckBox()
            self.cbx_specular.setMaximumWidth(15)

        self.update_values()

    def create_layout(self):
        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.but_light_type)  # �ƹ�����
        main_layout.addStretch(5)
        main_layout.addWidget(self.cbx_visibility)  # �ƹ���ʾ
        main_layout.addStretch(4)
        main_layout.addWidget(self.lab_transform_nam)  # �ƹ�����
        main_layout.addStretch(1)
        main_layout.addWidget(self.dubSpin_intensity)  # �ƹ�����
        main_layout.addStretch(6)
        main_layout.addWidget(self.but_color)  # �ƹ���ɫ
        if self.get_lightType() not in self.noEmit_lis:
            main_layout.addStretch(8)
            main_layout.addWidget(self.cbx_diffuse)  # ������
            main_layout.addStretch(15)
            main_layout.addWidget(self.cbx_specular)  # ���淴��
        else:
            main_layout.addStretch(29)

    def create_connections(self):
        self.but_light_type.clicked.connect(self.sel_light)
        self.cbx_visibility.toggled.connect(self.set_visibility)
        self.dubSpin_intensity.editingFinished.connect(self.set_intensity)
        self.but_color.color_changed.connect(self.set_color)
        if self.get_lightType() not in self.noEmit_lis:
            self.cbx_diffuse.toggled.connect(self.set_emitDiffuse)
            self.cbx_specular.toggled.connect(self.set_emitSpecular)

    def update_values(self):
        '''
        �ƹ����Ա仯ʱ�������е�������ˢ��ֵһ��
        :return: None
        '''
        self.but_light_type.setIcon(self.get_icon())
        self.cbx_visibility.setChecked(self.get_attribute(self.get_transform(), 'visibility'))
        self.lab_transform_nam.setText(self.get_transform())
        self.dubSpin_intensity.setValue(self.get_attribute(self.shape, 'intensity'))
        self.but_color.set_color(self.get_color())
        if self.get_lightType() not in self.noEmit_lis:
            self.cbx_diffuse.setChecked(self.get_diffuse())
            self.cbx_specular.setChecked(self.get_specular())

    def get_transform(self):
        return mc.listRelatives(self.shape, p=True)[0]

    def get_lightType(self):
        return mc.nodeType(self.shape)

    def get_icon(self):
        light_typ = self.get_lightType()
        if light_typ in self.typ_lis:
            icon = QtGui.QIcon(':{}.svg'.format(light_typ))
        else:
            icon = QtGui.QIcon(':Light.png')
        return icon

    def get_color(self):
        color = self.get_attribute(self.shape, 'color')[0]
        return QtGui.QColor(color[0] * 255, color[1] * 255, color[2] * 255)

    def get_diffuse(self):
        return self.get_attribute(self.shape, 'emitDiffuse')

    def get_specular(self):
        return self.get_attribute(self.shape, 'emitSpecular')

    def get_attribute(self, shp, attr):
        return mc.getAttr('{}.{}'.format(shp, attr))

    def set_attribute(self, nam, attr, *value):
        if attr == 'color':
            if self.get_color() == self.but_color.get_color():
                return
        elif value[0] == self.get_attribute(nam, attr):
            return
        mc.setAttr('{}.{}'.format(nam, attr), *value)
        log.info('�ѽ�{}��{}��������Ϊ{}��'.format(nam, attr, value))

    def sel_light(self):
        trs = self.get_transform()
        mc.select(trs)
        log.info('��ѡ��ƹ�{}��'.format(trs))

    def set_visibility(self, checked):
        self.set_attribute(self.get_transform(), 'visibility', checked)

    def set_intensity(self):
        self.set_attribute(self.shape, 'intensity', self.dubSpin_intensity.value())

    def set_color(self, color):
        if color != self.get_color():
            self.set_attribute(self.shape, 'color', color.redF(), color.greenF(), color.blueF())

    def set_emitDiffuse(self, checked):
        self.set_attribute(self.shape, 'emitDiffuse', checked)

    def set_emitSpecular(self, checked):
        self.set_attribute(self.shape, 'emitSpecular', checked)

    def create_script_jobs(self):
        self.delete_script_jobs()  # ȷ�������ظ�����
        self.add_attribute_change_script_job(self.get_transform(), 'visibility')
        self.add_attribute_change_script_job(self.shape, 'color')
        self.add_attribute_change_script_job(self.shape, 'intensity')
        if self.get_lightType() not in self.noEmit_lis:
            self.add_attribute_change_script_job(self.shape, 'emitDiffuse')
            self.add_attribute_change_script_job(self.shape, 'emitSpecular')

        self.script_jobs.append(mc.scriptJob(nd=(self.shape, partial(self.on_node_deleted))))
        self.script_jobs.append(mc.scriptJob(nnc=(self.shape, partial(self.on_name_changed))))

    def delete_script_jobs(self):
        '''
        ��ո��������job
        :return:
        '''
        for job in self.script_jobs:
            mc.evalDeferred('if mc.scriptJob(ex={0}):\tmc.scriptJob(k={0}, f=True)'.format(job))
        self.script_jobs = []

    def add_attribute_change_script_job(self, nam, attr):
        '''
        ��ÿ�����Զ���ؼ�����job
        :param nam:
        :param attr:
        :return:
        '''
        self.script_jobs.append(mc.scriptJob(ac=('{}.{}'.format(nam, attr), partial(self.update_values))))

    def on_node_deleted(self):
        '''
        ���ýڵ㱻ɾ��ʱ�������źţ�ʹ����ɾ������
        :return:
        '''
        self.node_delete.emit(self.shape)

    def on_name_changed(self):
        '''
        trsform���ı��shape�ڵ���Ҳ��ı䣬������uuid��¼�½ڵ�����ٸ���shape����
        :return: None
        '''
        self.shape = mc.ls(self.uuid)[0]
        self.update_values()


class LightPanel(QtWidgets.QDialog):
    def __init__(self, parent=maya_main_window()):
        super(LightPanel, self).__init__(parent)

        self.setWindowTitle(u'�ƹ����')
        if mc.about(ntOS=True):  # �ж�ϵͳ����
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)  # ɾ�������ϵİ�����ť
        elif mc.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumWidth(600)
        self.setMaximumWidth(600)

        self.light_items = []
        self.script_jobs = []

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.but_refresh = QtWidgets.QPushButton(u'ˢ��')
        self.lis_light_lab = []
        for txt in [u'��ʾ', u'����', u'����', u'��ɫ', u'������', u'���淴��']:
            lab = QtWidgets.QLabel(txt)
            self.lis_light_lab.append(lab)

        self.wdg_light_lis = QtWidgets.QWidget()
        self.area_light_lis = QtWidgets.QScrollArea()  # ����һ���л����Ŀؼ�
        self.area_light_lis.setMinimumHeight(300)
        self.area_light_lis.setWidgetResizable(True)
        self.area_light_lis.setWidget(self.wdg_light_lis)

    def create_layout(self):
        header_layout = QtWidgets.QHBoxLayout()
        for lab in self.lis_light_lab:
            header_layout.addStretch()
            header_layout.addWidget(lab)

        self.light_layout = QtWidgets.QVBoxLayout(self.wdg_light_lis)
        self.light_layout.setAlignment(QtCore.Qt.AlignTop)
        self.refresh_lights()
        for itm in self.light_items:
            self.light_layout.addWidget(itm)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.but_refresh)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.area_light_lis)
        main_layout.addStretch()
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.but_refresh.clicked.connect(self.refresh_lights)

    def refresh_lights(self):
        '''
        ˢ�µƹ��ɾ��light_layout���������������
        self.light_items��ɾ����ʱ����գ���ʱ���������µĵƹ����
        �ڵ�ɾ��job�ᴥ��ˢ��
        :return:
        '''
        self.clear_lights()
        for light in mc.ls(type='light'):
            light_item = LightItem(light)
            light_item.node_delete.connect(self.refresh_lights)

            self.light_layout.addWidget(light_item)
            self.light_items.append(light_item)

    def clear_lights(self):
        '''
        �Ƚ����������Ŀؼ���job������ɾ��
        �������еƹ��ÿɾ��һ�ξ���һ�� ֱ��Ϊ0ʱѭ���Ͽ�
        :return:
        '''
        for light in self.light_items:
            light.delete_script_jobs()

        self.light_items = []
        while self.light_layout.count() > 0:  # ��layout��������������
            light_item = self.light_layout.takeAt(0)  # ��layout��ڼ���
            if light_item.widget():  # ��ѯ��QtWidgets.QLayoutItem�ǲ���һ��QWidget�����Ƿ���none���Ƿ������item
                light_item.widget().deleteLater()

    def on_dag_object_change(self):
        '''
        ÿ���нڵ㱻�����ͳ�������ʱ���������볡���еƹ�����ͬ��ˢ�´���
        :return:
        '''
        if len(mc.ls(type='light')) != len(self.light_items):
            self.refresh_lights()
            log.info('�����ƹ�䶯�������ˢ�¡�����')

    def showEvent(self, event):
        '''
        ���ɴ���ʱ���ڵ㴴���ͳ�����job�뺯����������
        :param event:
        :return:
        '''
        self.script_jobs.append(mc.scriptJob(e=['DagObjectCreated', partial(self.on_dag_object_change)]))
        self.script_jobs.append(mc.scriptJob(e=['Undo', partial(self.on_dag_object_change)]))
        self.refresh_lights()

    def closeEvent(self, event):
        '''
        �رմ���ʱ��jobɾ��
        :param event:
        :return:
        '''
        for job in self.script_jobs:
            mc.scriptJob(k=job)
        self.script_jobs = []
        self.clear_lights()


if __name__ == '__main__':
    try:
        my_window.close()
        my_window.deleteLater()
    except:
        pass
    finally:
        my_window = LightPanel()
        my_window.show()