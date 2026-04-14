#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/12 20:52
@Author  : thezehui@gmail.com
@File    : app_service.py
"""
import uuid
import datetime

from sqlalchemy import (
    Column, UUID, String, Text,DateTime, PrimaryKeyConstraint,Index,
)
from internal.extension.database import db

class App(db.Model):

    __tablename__ = "app"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index("app_idx_account_id", "account_id"),
    )

    id = Column(UUID, default=uuid.uuid4, nullable=False)
    account_id = Column(UUID, nullable=False)
    name = Column(String(255), default="", nullable=False)
    icon = Column(String(255), default="", nullable=False)
    describe = Column(Text, default="", nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.now(), onupdate=datetime.datetime.now(), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.now(), nullable=False)