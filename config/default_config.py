#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/12 19:48
@Author  : thezehui@gmail.com
@File    : default_config.py
"""
DEFAULT_CONFIG = {
    "SQLALCHEMY_DATABASE_URI":"postgresql://gripai:liuzhixin134.@47.108.132.169:5432/llm_ops",
    "SQLALCHEMY_ECHO":True,
    "SQLALCHEMY_POOL_SIZE":6,
    "SQLALCHEMY_POOL_RECYCLE":3600,
}