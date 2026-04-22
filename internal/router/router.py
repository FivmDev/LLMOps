#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 10:38
@Author  : thezehui@gmail.com
@File    : router.py
"""
from flask import Flask,Blueprint
from internal.handler import AppHandler
from internal.router.document_router import DocumentRouter
from internal.router.agent_router import AgentRouter
from dataclasses import dataclass
from injector import inject

@inject
@dataclass
class Router:
    """路由"""
    app_handler : AppHandler
    document_router: DocumentRouter
    agent_router: AgentRouter

    def register_routes(self, app: Flask):
        """注册路由"""
        #  1. 创建蓝图
        bp = Blueprint("llmops", __name__, url_prefix="")

        # 2. 将url与应用控制器相互绑定
        bp.add_url_rule("/ping",view_func=self.app_handler.ping)

        # 3. 注册蓝图
        app.register_blueprint(bp)

        # 4. 注册文档路由
        self.document_router.register_routes(app)

        # 5. 注册 Agent 路由
        self.agent_router.register_routes(app)
