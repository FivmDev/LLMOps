#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/29 11:07
@Author  : thezehui@gmail.com
@File    : http_response.py
"""
from flask import jsonify
from pkg.response.http_code import HttpCode
from dataclasses import dataclass,field
from typing import Any


@dataclass
class HttpResponse:

    code : HttpCode = HttpCode.SUCCESS
    message : str = ""
    data : Any = field(default_factory=dict)


def json(data : HttpResponse = None):
    return jsonify(data),200

def success_json(data : Any = None):
    return json(HttpResponse(code=HttpCode.SUCCESS,message="",data=data))

def failure_json(data : Any = None):
    return json(HttpResponse(code=HttpCode.FAILED,message="",data=data))

def validation_error_json(errors: dict = None):
    first_key = next(iter(errors))
    if first_key is not None:
        msg = errors.get(first_key)[0]
    else:
        msg = ""
    return json(HttpResponse(code=HttpCode.VALIDATION_ERROR, message=msg, data={}))


def message(code : HttpCode, msg : str):
    return json(HttpResponse(code=code,message=msg,data={}))

def success_message(msg : str):
    return message(HttpCode.SUCCESS,msg)

def unauthorized_message(msg : str):
    return message(HttpCode.UNAUTHORIZED,msg)

def forbidden_message(msg : str):
    return message(HttpCode.FORBIDDEN,msg)

def not_found_message(msg : str):
    return message(HttpCode.NOT_FOUND,msg)