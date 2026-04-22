#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/22
@Author  : thezehui@gmail.com
@File    : agent_router.py
"""
from flask import Flask, Blueprint, request
from injector import inject
from dataclasses import dataclass
from functools import wraps

from internal.handler import AgentHandler


@inject
@dataclass
class AgentRouter:
    """Agent 路由"""

    agent_handler: AgentHandler

    def register_routes(self, app: Flask):
        """注册 Agent 路由"""
        bp = Blueprint("agent", __name__, url_prefix="/agent")

        bp.add_url_rule("/invoke", methods=['POST'], view_func=self._wrap_invoke(self.agent_handler.invoke))

        app.register_blueprint(bp)

    @staticmethod
    def _wrap_invoke(func):
        @wraps(func)
        def wrapper():
            return func()
        return wrapper
