# -*- coding: utf-8 -*-
# @Time    : 2019/9/1 18:38
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : hotkey.py
# @Software: PyCharm

from whotkey import HotkeyManager

def test():
    print(1233)


m = HotkeyManager()
m.add(hotkey_str='ctrl+q', target = test)
while True:
    pass