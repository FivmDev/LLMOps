#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/27 23:01
@Author  : thezehui@gmail.com
@File    : __init__.py.py
"""
from internal.router.router import Router
from internal.router.document_router import DocumentRouter
from internal.router.agent_router import AgentRouter

__all__ = ["Router", "DocumentRouter", "AgentRouter"]