# -*- coding: utf-8 -*-
# @Time    : 2019/9/2 0:07
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : decos.py
# @Software: PyCharm


def singleton(cls):
    instance = {}

    def wrapper(*args, **kwargs):
        if cls not in instance:
            instance[cls] = cls(*args, **kwargs)
        return instance[cls]

    return wrapper
