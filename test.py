#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/27 23:04
@Author  : thezehui@gmail.com
@File    : test.py
"""
from injector import Injector,inject
class A:
    name = "WOSHIA"

class B:
    @inject
    def __init__(self, a : A):
        self.a = a
    def print_a(self):
        print("DAYIN",self.a.name)

injector = Injector()
a = injector.get(B)
a.print_a()



