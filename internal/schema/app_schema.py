#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 17:28
@Author  : thezehui@gmail.com
@File    : app_schema.py
"""
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length

class CompletionReq(FlaskForm):
    """AI模块Completion请求验证"""

    # 必填 & 长度不超过2000
    query = StringField("name", validators=[
        DataRequired(message="用户提问是必填的"),
        Length(max=2000,message="提问长度不得超过2000")])