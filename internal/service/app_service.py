#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/12 21:00
@Author  : thezehui@gmail.com
@File    : app_service.py
"""
import uuid
from os import name

from pkg.flask_sqlalchemy import SQLAlchemy
from dataclasses import dataclass
from injector import inject
from internal.model import App

@inject
@dataclass
class AppService:
    """应用服务逻辑层"""
    db : SQLAlchemy

    def create_app(self) -> App:
        with self.db.auto_commit():
            app = App(name="测试机器人",account_id=uuid.uuid4(),icon="",describe="这是第一个机器人")
            self.db.session.add(app)
        return app

    def get_app(self,id : uuid.UUID) -> App:
        app = self.db.session.query(App).get(id)
        return app

    def update_app(self,id : uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            app.name = "刘志鑫专属机器人"
        return app

    def delete_app(self,id : uuid.UUID) -> App:
        with self.db.auto_commit():
            app = self.get_app(id)
            self.db.session.delete(app)
        return app



