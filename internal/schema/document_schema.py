#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : document_schema.py
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField
from wtforms.validators import DataRequired
from wtforms.validators import Length


class DocumentUploadReq(FlaskForm):
    """文档上传请求验证"""

    file = FileField("file", validators=[
        FileRequired(message="文件是必填的"),
        FileAllowed(['docx', 'pdf', 'xlsx', 'csv'], message="只支持docx、pdf、xlsx、csv格式")
    ])
    tenant_id = StringField("tenant_id", validators=[
        DataRequired(message="租户ID是必填的"),
        Length(max=64, message="租户ID长度不得超过64")
    ])
    metadata = StringField("metadata")