# -*- coding: utf-8 -*-
# @Time    : 2019/8/14 0:23
# @Author  : Suyin
# @Email   : 820390693@qq.com
# @File    : 代码.py
# @Software: PyCharm


class 侠客:

    def __init__(self, 名字, 技能树_实例):
        self.名字 = 名字

        self.技能树 = 技能树_实例
        self.技能树.绑定角色(self)

        self.等级 = 1
        self.血量 = 100
        self.内力 = 100

    def 消耗内力(self, 数值):
        self.内力 -= 数值

    def 受到伤害(self, 数值):
        self.血量 -= 数值

    def 升级技能(self, 技能名称, 升级次数 = 1):  # 接口方法，方便调用
        技能 = eval('self.技能树.' + 技能名称)
        技能.升级(升级次数)

    def 发动技能(self, 技能名称, 目标):  # 接口方法，方便调用
        技能 = eval('self.技能树.' + 技能名称)
        技能.发动(目标)

    def 当前属性(self):
        当前属性 = """\
名字：{}
等级：{}
血量：{}
内力：{}
技能等级：
    快剑：{} """.format(self.名字, self.等级, self.血量, self.内力,self.技能树.快剑.等级)
        return 当前属性



class 侠客技能树:

    def __init__(self):
        self.角色 = None
        self.快剑 = None

    def 绑定角色(self, 角色_实例):
        self.角色 = 角色_实例
        self.快剑 = 侠客技能树.快剑(self.角色)

    class 快剑:

        def __init__(self, 角色_实例):
            self.角色 = 角色_实例
            self.等级 = 1

        def 消耗的内力(self):
            return 10 * self.等级

        def 造成的伤害(self):
            return 20 * self.等级

        def 发动(self, 目标):
            self.角色.消耗内力(self.消耗的内力())
            目标.受到伤害(self.造成的伤害())

        def 设置等级(self, 等级):
            self.等级 = 等级

        def 升级(self, 次数 = 1):
            self.设置等级(self.等级 + 次数)


侠客技能树A = 侠客技能树()
侠客A = 侠客('侠客A', 侠客技能树A)

侠客技能树B = 侠客技能树()
侠客B = 侠客('侠客B', 侠客技能树B)

# 侠客A.技能树.快剑.升级(3)
侠客A.升级技能('快剑', 3)
# print(侠客A.技能树.快剑.等级)

侠客A.发动技能('快剑', 侠客B)

print(侠客A.当前属性())
print(侠客B.当前属性())

