#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : knowledge_document.py
"""
import uuid
import datetime

from sqlalchemy import (
    Column, String, Text, Integer, DateTime, Boolean,
    PrimaryKeyConstraint, Index, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from internal.extension.database import db


class KnowledgeDocument(db.Model):

    __tablename__ = "knowledge_documents"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index("idx_kd_tenant", "tenant_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(64), nullable=False)
    doc_id = Column(String(64), unique=True, nullable=False)
    doc_name = Column(String(256), nullable=False)
    doc_type = Column(String(32), nullable=False)
    doc_url = Column(Text)
    total_pairs = Column(Integer, default=0)
    status = Column(String(16), default='pending')
    error_message = Column(Text)
    document_metadata = Column(JSONB)
    is_active = Column(Boolean, default=True)
    uploaded_at = Column(DateTime, default=datetime.datetime.now)
    processed_at = Column(DateTime)