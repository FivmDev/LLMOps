#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 11:01
@Author  : thezehui@gmail.com
@File    : http_server.py
"""
from flask import Flask
from internal.router import Router
from config import Config
from internal.exception import CustomException
from pkg.flask_sqlalchemy import SQLAlchemy
from pkg.response import json,HttpResponse,HttpCode
import os
from internal.model import App
from internal.extension.migrate import Migrate


class Http(Flask):
    """http服务引擎"""

    def __init__(self,*args,router : Router,db : SQLAlchemy,migrate : Migrate,config : Config,**kwargs):
        super().__init__(*args,**kwargs)

        self.config.from_object(config)
        db.init_app(self)
        migrate.init_app(self, db, directory="internal/migration")
        # with self.app_context():
        #     _ = App()
        #     db.create_all()
        router.register_routes(self)
        self.register_error_handler(Exception,self._register_error_handler)


    def _register_error_handler(self,error : Exception):
        # 1.异常信息是不是我们的自定义异常，如果是可以提取message和code等信息
        if isinstance(error, CustomException):
            return json(HttpResponse(
                code=error.code,
                message=error.message,
                data=error.data if error.data is not None else {},
            ))
        # 2.如果不是我们的自定义异常，则有可能是程序、数据库抛出的异常，也可以提取信息，设置为FAIL状态码
        if self.debug or os.getenv("FLASK_ENV") == "development":
            raise error
        else:
            return json(HttpResponse(
                code=HttpCode.FAILED,
                message=str(error),
                data={},
            ))




