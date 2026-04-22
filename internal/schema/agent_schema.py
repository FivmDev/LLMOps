#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/22
@Author  : thezehui@gmail.com
@File    : agent_schema.py
"""
from pydantic import BaseModel


class AgentInvokeReq(BaseModel):
    tenant_id: str
    session_id: str
    user_input: str
    system_prompt: str = ""
    stream: bool = False


class AgentInvokeResp(BaseModel):
    response: str
    message_id: str
    need_rag: bool
    session_summary: str
