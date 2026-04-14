#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/29 11:05
@Author  : thezehui@gmail.com
@File    : http_code.py
"""
from enum import Enum

class HttpCode(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    UNAUTHORIZED = "unauthorized"
    FORBIDDEN = "forbidden"
    NOT_FOUND = "not_found"
    VALIDATION_ERROR = "validation_error"
