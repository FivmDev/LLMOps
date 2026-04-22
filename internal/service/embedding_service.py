#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : embedding_service.py
"""
import os
from typing import List
from langchain_openai import OpenAIEmbeddings
from injector import inject
from dataclasses import dataclass


@inject
@dataclass
class EmbeddingService:
    """LangChain Embedding服务"""

    def __post_init__(self):
        self.embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_api_base=os.getenv("OPENAI_API_BASE")
        )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """批量向量化文本"""
        return self.embeddings.embed_documents(texts)

    def embed_query(self, text: str) -> List[float]:
        """向量化单个查询文本"""
        return self.embeddings.embed_query(text)