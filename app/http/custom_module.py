#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/13 16:54
@Author  : thezehui@gmail.com
@File    : custom_module.py
"""
from flask_migrate import Migrate
from pkg.flask_sqlalchemy import SQLAlchemy
from injector import Module
from internal.extension.database import db
from internal.extension.migrate import migrate
from internal.service import DocumentService, EmbeddingService
from internal.task import DocumentTaskProcessor


class ExtensionModule(Module):
    def configure(self, binder):
        binder.bind(SQLAlchemy, to=db)
        binder.bind(Migrate, to=migrate)
        binder.bind(EmbeddingService)
        binder.bind(DocumentService)
        binder.bind(DocumentTaskProcessor)
