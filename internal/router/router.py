#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 10:38
@Author  : thezehui@gmail.com
@File    : router.py
"""
from flask import Flask,Blueprint
from internal.handler import AppHandler, app_handler
from dataclasses import dataclass
from injector import inject

@inject
@dataclass
class Router:
    """路由"""
    app_handler : AppHandler

    def register_routes(self, app: Flask):
        """注册路由"""
        #  1. 创建蓝图
        bp = Blueprint("llmops", __name__, url_prefix="")

        # 2. 将url与应用控制器相互绑定
        bp.add_url_rule("/ping",view_func=self.app_handler.ping)
        bp.add_url_rule("/app/completion",methods=['POST'],view_func=self.app_handler.completion)
        bp.add_url_rule("/app/create",methods=['POST'],view_func=self.app_handler.create_app)
        bp.add_url_rule("/app/<uuid:id>",methods=['GET'],view_func=self.app_handler.get_app)
        bp.add_url_rule("/app/<uuid:id>",methods=['POST'],view_func=self.app_handler.update_app)
        bp.add_url_rule("/app/delete/<uuid:id>",methods=['POST'],view_func=self.app_handler.delete_app)

        # 3. 注册蓝图
        app.register_blueprint(bp)
