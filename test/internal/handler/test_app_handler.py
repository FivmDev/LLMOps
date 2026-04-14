#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/29 16:40
@Author  : thezehui@gmail.com
@File    : test_app_handler.py
"""
import pytest
from pkg.response import HttpCode

class TestAppHandler:
    """app控制器的测试类"""

    @pytest.mark.parametrize("query", [None, "你好"])
    def test_completion(self,query,client):
        # 测试 /app/completion 接口
        res = client.post("/app/completion",json={"query":query})
        assert res.status_code == 200
        if query is None:
            assert res.json["code"] == HttpCode.VALIDATION_ERROR
        else:
            assert res.json["code"] == HttpCode.SUCCESS