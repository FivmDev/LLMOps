#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 17:37
@Author  : thezehui@gmail.com
@File    : config.py
"""
import os
from typing import Any
from .default_config import DEFAULT_CONFIG


def _get_env(key : str) -> Any:
    value = os.getenv(key,DEFAULT_CONFIG.get(key))
    return value

def _get_bool_env(key : str) -> bool:
    value : str = _get_env(key)

    return value.lower() == "true" if value is not None  else False

class Config:

    def __init__(self):
        # 关闭CSRF保护
        self.WTF_CSRF_ENABLED = False
        self.FLASK_ENV = 'development'
        self.FLASK_DEBUG = True
        self.SQLALCHEMY_DATABASE_URI = _get_env('SQLALCHEMY_DATABASE_URI')
        self.SQLALCHEMY_ECHO= _get_bool_env('SQLALCHEMY_ECHO')
        self.SQLALCHEMY_POOL_SIZE= int(_get_env('SQLALCHEMY_POOL_SIZE'))
        self.SQLALCHEMY_POOL_RECYCLE = int(_get_env('SQLALCHEMY_POOL_RECYCLE'))