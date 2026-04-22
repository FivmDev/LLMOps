#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : document_task.py
"""
from concurrent.futures import ThreadPoolExecutor
from injector import inject
from dataclasses import dataclass
from internal.service import DocumentService


@inject
@dataclass
class DocumentTaskProcessor:
    """文档异步处理器"""

    document_service: DocumentService

    def __post_init__(self):
        self.executor = ThreadPoolExecutor(max_workers=3)

    def submit(self, doc_id: str):
        """提交文档处理任务"""
        future = self.executor.submit(self._process, doc_id)
        return future

    def _process(self, doc_id: str):
        """后台执行: 解析 -> QA生成 -> 向量化 -> 存储"""
        document = self.document_service.get_document_by_doc_id(doc_id)
        if not document:
            return

        try:
            self.document_service.update_document_status(doc_id, 'processing')

            documents = self.document_service.parse_to_documents(
                document.doc_url,
                document.doc_type
            )

            split_documents = self.document_service.split_documents(documents)

            qa_pairs = self.document_service.generate_qa_pairs(split_documents)

            stored_count = self.document_service.vectorize_and_store(doc_id, qa_pairs)

            self.document_service.update_document_status(doc_id, 'completed')

        except Exception as e:
            self.document_service.update_document_status(
                doc_id,
                'failed',
                error_message=str(e)
            )