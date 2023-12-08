# -*- coding: utf-8 -*-
# @Time    : 2019/9/1 21:15
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : whotkey.py
# @Software: PyCharm


from ctypes import *
from ctypes.wintypes import *
# from inspect import isfunction
import threading

__all__ = ['HotkeyManager']


def singleton(cls):
    instance = {}

    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return wrapper


class HotkeyTask(threading.Thread):

    def __init__(self, parent, member_id, ascii, mod, target):
        super().__init__()
        self._parent = parent
        self._member_id = member_id
        self._ascii = ascii
        self._mod = mod
        self._target = target
        self._msg = parent._msg
        self._member_info = parent._member_info
        self._is_ok = True
        self._is_waitting_for_register = True
        self._quit = False

    def _register_hotkey(self, member_id, ascii, mod, target):
        # if not isfunction(target):
        #     return False

        ok = windll.user32.RegisterHotKey(None, member_id, mod, ascii)
        if ok:
            # 注册成功
            self._member_info[member_id] = {'mod': mod, 'ascii': ascii, 'target': target}
            return True
        else:
            # 注册失败
            return False

    def is_ok(self):
        return self._is_ok

    def wait(self):
        while self._is_waitting_for_register:
            pass

    def quit(self):
        self._quit = True

    def run(self):
        ok = self._register_hotkey(
            member_id = self._member_id,
            mod = self._mod,
            ascii = self._ascii,
            target = self._target
        )
        if not ok:
            self._is_ok = False
            self._is_waitting_for_register = False
            return
        self._is_waitting_for_register = False
        msg = self._msg
        while True:
            if self._quit:
                break
            if windll.user32.GetMessageA(msg, None, 0, 0) != 0:
                if self._quit:
                    break
                if msg.message == self._parent.WM_HOTKEY:
                    if msg.wParam == self._member_id:

                        t = threading.Thread(target = self._target)
                        t.start()
                        # member_info[member_id]['target']()

                windll.user32.TranslateMessage(byref(msg))
                windll.user32.DispatchMessageA(byref(msg))

    def is_waitting_for_register(self):
        return self._is_waitting_for_register


@singleton
class HotkeyManager:
    WM_HOTKEY = 0x0312
    MOD_ALT = 0x0001
    MOD_CONTROL = 0x0002
    MOD_SHIFT = 0x0004

    # WM_KEYUP = 0x0101
    def __init__(self):
        self._member_info = {}
        #  {int_id : {'mod': mod, 'ascii': ascii, 'target': target}, ...}
        self._msg = MSG()

        self._task_pool = {}
    def unregister_all(self):
        for id, task in self._task_pool.items():
            task.quit()
            windll.user32.UnregisterHotKey(None,id)
        self._task_pool = {}
        print('取消所有热键')



    def _register_hotkey(self, member_id, ascii, mod, target):
        task = HotkeyTask(self, member_id, ascii, mod, target)
        task.start()
        task.wait()
        if task.is_ok():
            # print('注册成功')
            self._task_pool[member_id] = task
            return True
        else:
            # print('注册失败')
            return False

    def add(self, *, hotkey_str, target):
        """
        key_str: ex. 'ctrl+a'
        """
        key_str_op = key_str = hotkey_str.upper()
        modifier = 0
        if 'CTRL' in key_str_op:
            key_str_op = key_str_op.replace('CTRL', '')
            modifier |= self.MOD_CONTROL
        if 'ALT' in key_str_op:
            key_str_op = key_str_op.replace('ALT', '')
            modifier |= self.MOD_ALT
        if 'SHIFT' in key_str_op:
            key_str_op = key_str_op.replace('SHIFT', '')
            modifier |= self.MOD_SHIFT
        key_str_op = key_str_op.strip('+').strip(' ')
        member_id = len(self._member_info)
        ok = self._register_hotkey(
            member_id = member_id, mod = modifier, ascii = ord(key_str_op), target = target
        )
        if ok:
            print('{} 注册成功'.format(key_str))
        else:
            member_id = None
            print('{} 注册失败'.format(key_str))

        return member_id

    def menber_info(self):
        return self._menber_info

    def member(self, member_id):
        return self._member_info.get(member_id)


if __name__ == '__main__':
    import sys
    from PyQt5.QtWidgets import *


    class MainWindow(QWidget):

        def __init__(self):
            super().__init__()
            self.setWindowTitle('_______')
            self.resize(800, 600)

            main_layout = QVBoxLayout()
            self.setLayout(main_layout)


    def _test():
        print(11111111111111111111111111111111111111)


    def _test2():
        print(2222222222222222222)


    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()

    hotkey_manager = HotkeyManager()
    id_ctrl_a = hotkey_manager.add(hotkey_str = 'ctrl+A', target = _test)
    id_ctrl_b = hotkey_manager.add(hotkey_str = 'ctrl+B', target = _test2)

    sys.exit(app.exec_())
