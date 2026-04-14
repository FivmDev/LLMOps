#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/13 15:53
@Author  : thezehui@gmail.com
@File    : sqlalchemy.py
"""
from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy
from contextlib import contextmanager

class SQLAlchemy(_SQLAlchemy):
    """重写flask_sqlalchemy"""

    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            self.session.rollback()
            raise e