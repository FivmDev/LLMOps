#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : document_handler.py
"""
import json
from injector import inject
from dataclasses import dataclass
from internal.schema import DocumentUploadReq
from internal.service import DocumentService
from internal.task import DocumentTaskProcessor
from pkg.response import success_json, success_message, validation_error_json, not_found_message


@inject
@dataclass
class DocumentHandler:
    """文档控制器"""

    document_service: DocumentService
    document_task_processor: DocumentTaskProcessor

    def upload(self):
        """POST /document/upload - 同步返回doc_id和pending状态"""
        req = DocumentUploadReq()
        if not req.validate():
            return validation_error_json(req.errors)

        metadata = None
        if req.metadata.data:
            try:
                metadata = json.loads(req.metadata.data)
            except json.JSONDecodeError:
                metadata = None

        document = self.document_service.upload_document(
            file=req.file.data,
            tenant_id=req.tenant_id.data,
            metadata=metadata
        )

        self.document_task_processor.submit(document.doc_id)

        return success_json({
            "doc_id": document.doc_id,
            "doc_name": document.doc_name,
            "status": document.status
        })

    def get_status(self, doc_id: str, tenant_id: str):
        """GET /document/{doc_id}/status - 查询处理状态"""
        document = self.document_service.get_document_status(doc_id, tenant_id)
        if not document:
            return not_found_message("文档不存在")

        return success_json({
            "doc_id": document.doc_id,
            "doc_name": document.doc_name,
            "doc_type": document.doc_type,
            "status": document.status,
            "total_pairs": document.total_pairs,
            "error_message": document.error_message,
            "uploaded_at": document.uploaded_at.isoformat() if document.uploaded_at else None,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None
        })

    def delete(self, doc_id: str, tenant_id: str):
        """DELETE /document/{doc_id} - 删除文档及QA对"""
        result = self.document_service.delete_document(doc_id, tenant_id)
        if not result:
            return not_found_message("文档不存在")

        return success_message("文档删除成功")