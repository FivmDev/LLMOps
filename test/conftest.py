#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/29 16:53
@Author  : thezehui@gmail.com
@File    : conftest.py
"""
import pytest
from app.http.app import app

@pytest.fixture
def client():
    """获取 Flask 的测试应用"""
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c