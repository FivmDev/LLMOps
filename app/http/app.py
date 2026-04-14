#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 11:04
@Author  : thezehui@gmail.com
@File    : app_service.py
"""
from flask_migrate import Migrate

from internal.server import Http
from internal.router import Router
from injector import Injector
from config import Config
import dotenv
from app.http.custom_module import ExtensionModule
from pkg.flask_sqlalchemy import SQLAlchemy

# 加载配置到环境变量
dotenv.load_dotenv()

injector = Injector([ExtensionModule])

app = Http(__name__,config=Config(),db=injector.get(SQLAlchemy),migrate=injector.get(Migrate),router = injector.get(Router))

if __name__ == '__main__':
    app.run(debug=True)