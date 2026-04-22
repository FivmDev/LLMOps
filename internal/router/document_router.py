#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : document_router.py
"""
from flask import Flask, Blueprint, request
from injector import inject
from dataclasses import dataclass
from functools import wraps
from internal.handler import DocumentHandler


@inject
@dataclass
class DocumentRouter:
    """文档路由"""

    document_handler: DocumentHandler

    def register_routes(self, app: Flask):
        """注册文档路由"""
        bp = Blueprint("document", __name__, url_prefix="/document")

        bp.add_url_rule("/upload", methods=['POST'], view_func=self._wrap_upload(self.document_handler.upload))
        bp.add_url_rule("/<doc_id>/status", methods=['GET'], view_func=self._wrap_get_status(self.document_handler.get_status))
        bp.add_url_rule("/<doc_id>", methods=['DELETE'], view_func=self._wrap_delete(self.document_handler.delete))

        app.register_blueprint(bp)

    @staticmethod
    def _wrap_upload(func):
        @wraps(func)
        def wrapper():
            return func()
        return wrapper

    @staticmethod
    def _wrap_get_status(func):
        @wraps(func)
        def wrapper(doc_id: str):
            tenant_id = request.args.get('tenant_id', '')
            return func(doc_id, tenant_id)
        return wrapper

    @staticmethod
    def _wrap_delete(func):
        @wraps(func)
        def wrapper(doc_id: str):
            tenant_id = request.args.get('tenant_id', '')
            return func(doc_id, tenant_id)
        return wrapper