#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/29 16:13
@Author  : thezehui@gmail.com
@File    : exception.py
"""
from pkg.response import HttpCode
from typing import Any
from dataclasses import field

class CustomException(Exception):
    code : HttpCode = HttpCode.FAILED
    message : str = ""
    data : Any = field(default_factory=dict)

    def __init__(self, message: str = None, data: Any = None):
        super().__init__()
        self.message = message
        self.data = data

class FailedException(CustomException):
    pass

class UnauthorizedException(CustomException):
    code : HttpCode = HttpCode.UNAUTHORIZED

class ForbiddenException(CustomException):
    code : HttpCode = HttpCode.FORBIDDEN

class NotFoundException(CustomException):
    code : HttpCode = HttpCode.NOT_FOUND

class ValidationException(CustomException):
    code : HttpCode = HttpCode.VALIDATION_ERROR