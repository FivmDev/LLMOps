#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : knowledge_qa_pair.py
"""
import uuid
import datetime

from sqlalchemy import (
    Column, String, Text, DateTime,
    PrimaryKeyConstraint, Index, ForeignKey
)
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector
from internal.extension.database import db


class KnowledgeQAPair(db.Model):

    __tablename__ = "knowledge_qa_pairs"
    __table_args__ = (
        PrimaryKeyConstraint("id"),
        Index("idx_kqp_tenant", "tenant_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(String(64), nullable=False)
    doc_id = Column(String(64), nullable=False)
    pair_id = Column(String(64), unique=True, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    question_vector = Column(Vector(1536))
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)