# -*- coding: utf-8 -*-
# @Time    : 2019/9/1 16:21
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : ui.py
# @Software: PyCharm

import os
import sys
from functools import partial

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from wscreenshot import WScreenshot
from whotkey import HotkeyManager
from decos import singleton


@singleton
class Tray:

    def __init__(self):
        icon = QIcon('./source/logo.png')
        self.tray = QSystemTrayIcon()
        self.tray.setIcon(icon)

        tray_menu = QMenu()
        ac_run_screen_shot = QAction("截图 (&S)", tray_menu, triggered = self.run_screen_shot)
        ac_quit_app = QAction("退出 (&Q)", tray_menu, triggered = self.quit_app)  # 退出APP

        tray_menu.addSeparator()
        tray_menu.addAction(ac_run_screen_shot)
        tray_menu.addAction(ac_quit_app)
        self.tray.setContextMenu(tray_menu)

    def run_screen_shot(self):
        CreateWScreenShot().to_create.emit()

    def show(self):
        self.tray.show()

    def delete(self):
        self.tray.hide()
        self.tray.deleteLater()

    def quit_app(self):
        App.quit()


@singleton
class CreateWScreenShot(QObject):
    to_create = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.to_create.connect(self.create)

    def create(self):
        WScreenshot.run()
        WScreenshot.getPixmapGot().connect(self._save_image)

    def _save_image(self, pixmap, reason):
        if reason == WScreenshot.REASON_CENTER:
            path, _ = QFileDialog.getSaveFileName(WScreenshot.instance, '保存图片（标题）', 'D:/test.png')
            pixmap.save(path, 'PNG', 100)

        QApplication.clipboard().setPixmap(pixmap)


class App:
    _app = None
    _tray = None
    _hotkey_manager = None
    _create_wscreenshot = CreateWScreenShot()

    @classmethod
    def quit(cls):
        cls._hotkey_manager.unregister_all()
        cls._tray.delete()
        QApplication.quit()
        os._exit(0)

    @classmethod
    def run(cls):
        cls._app = QApplication(sys.argv)
        cls._tray = Tray()
        cls._tray.show()
        cls._setup_hotkey()
        sys.exit(cls._app.exec_())

    @classmethod
    def _setup_hotkey(cls):
        cls._hotkey_manager = HotkeyManager()

        def on_ctrl_q():
            print('q')
            cls._create_wscreenshot.to_create.emit()

        # def on_ctrl_z():
        #     print('z')
        #     cls._hotkey_manager.unregister_all()
        #
        # def on_ctrl_x():
        #     print('x')
        #     cls._hotkey_manager.add(hotkey_str = 'ctrl+q', target = on_ctrl_q)

        cls._hotkey_manager.add(hotkey_str = 'ctrl+q', target = on_ctrl_q)
        # cls._hotkey_manager.add(hotkey_str = 'ctrl+z', target = on_ctrl_z)
        # cls._hotkey_manager.add(hotkey_str = 'ctrl+x', target = on_ctrl_x)


if __name__ == '__main__':
    App.run()
