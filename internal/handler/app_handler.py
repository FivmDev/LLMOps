#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 10:28
@Author  : thezehui@gmail.com
@File    : app_handler.py
"""
import uuid

from openai import OpenAI
import os
from internal.schema import CompletionReq
from pkg.response import success_json,validation_error_json,success_message
from internal.service import AppService
from injector import inject
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

@inject
@dataclass
class AppHandler:
    """APP应用控制器"""
    app_service : AppService

    def create_app(self):
        app = self.app_service.create_app()
        return success_message(f"应用创建成功，应用名称{app.name}")

    def get_app(self,id : uuid.UUID):
        app = self.app_service.get_app(id)
        return success_message(f"应用查询成功，应用名称为{app.name}")

    def delete_app(self,id : uuid.UUID):
        app = self.app_service.delete_app(id)
        return success_message("应用删除成功")

    def update_app(self,id : uuid.UUID):
        app = self.app_service.update_app(id)
        return success_message(f"应用名称修改成功，修改后的应用名称为{app.name}")

    def completion(self):
        """与DeepSeek交互"""
        req = CompletionReq()
        if not req.validate():
            return validation_error_json(req.errors)

        prompt = ChatPromptTemplate([
            ("system","You are a helpful assistant"),
            ("human","{query}")
        ])


        chat = ChatOpenAI(model="deepseek-chat",
                          api_key=os.getenv("DEEPSEEK_API_KEY"),
                          base_url=os.getenv("DEEPSEEK_BASE_URL"),)

        parser = StrOutputParser()

        chain = prompt | chat | parser

        content = chain.invoke({"query":req.query.data})

        return success_json({"content":content})

    def ping(self):
        return {"ping": "pong"}

