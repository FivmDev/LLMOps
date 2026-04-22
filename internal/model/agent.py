#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/22
@Author  : thezehui@gmail.com
@File    : agent.py
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Document(BaseModel):
    content: str
    score: float
    source: Optional[str] = None


class GraphState(BaseModel):
    tenant_id: str
    session_id: str
    user_input: str
    system_prompt: str
    context: str = ""
    session_summary: Optional[str] = None
    buffer: List[Dict[str, Any]] = Field(default_factory=list)
    token_count: int = 0
    need_rag: bool = False
    rag_documents: List[Document] = Field(default_factory=list)
    response: str = ""
    message_id: Optional[str] = None
    stream: bool = False
