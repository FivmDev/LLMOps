#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/3/28 10:28
@Author  : thezehui@gmail.com
@File    : app_handler.py
"""
import uuid
import os
from internal.schema import CompletionReq
from pkg.response import success_json,validation_error_json,success_message
from injector import inject
from dataclasses import dataclass
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import FileChatMessageHistory
from langchain_core.runnables import Runnable,RunnablePassthrough,RunnableLambda

@inject
@dataclass
class AppHandler:
    """APP应用控制器"""
    def completion(self):
        """与DeepSeek交互"""
        req = CompletionReq()
        if not req.validate():
            return validation_error_json(req.errors)

        file_chat_history = FileChatMessageHistory(file_path="./storage/memory/history.txt")

        prompt = ChatPromptTemplate([
            ("system","You are a helpful assistant"),
            MessagesPlaceholder("history"),
            ("human","{query}")
        ])


        chat = ChatOpenAI(model="deepseek-chat",
                          api_key=os.getenv("DEEPSEEK_API_KEY"),
                          base_url=os.getenv("DEEPSEEK_BASE_URL"),)

        parser = StrOutputParser()

        chain = (RunnablePassthrough.assign(history=RunnableLambda(lambda _ : file_chat_history.messages))
                 | prompt
                 | chat
                 | parser)

        content = chain.invoke({"query":req.query.data})

        file_chat_history.add_user_message(req.query.data)
        file_chat_history.add_ai_message(content)

        return success_json({"content":content})

    def ping(self):
        return {"ping": "pong"}

