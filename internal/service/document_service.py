#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : document_service.py
"""
import os
import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional

from injector import inject
from langchain_community.document_transformers import DoctranQATransformer
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from internal.model import KnowledgeDocument, KnowledgeQAPair
from internal.service.embedding_service import EmbeddingService
from internal.service.parser_factory import ParserFactory
from pkg.flask_sqlalchemy import SQLAlchemy


@inject
@dataclass
class DocumentService:
    """文档上传、解析、向量化服务"""

    db: SQLAlchemy
    embedding_service: EmbeddingService
    _qa_transformer: DoctranQATransformer = field(init=False)

    def __post_init__(self):
        self._qa_transformer = DoctranQATransformer()

    def upload_document(self, file, tenant_id: str, metadata: Optional[Dict] = None) -> KnowledgeDocument:
        """上传文档：保存文件，创建记录，返回doc_id"""
        doc_id = str(uuid.uuid4())
        doc_name = file.filename
        doc_type = self._get_doc_type(doc_name)

        storage_dir = f"storage/documents/{tenant_id}/{doc_id}"
        os.makedirs(storage_dir, exist_ok=True)
        file_path = os.path.join(storage_dir, doc_name)

        file_content = file.read()
        with open(file_path, 'wb') as f:
            f.write(file_content)

        document = KnowledgeDocument(
            tenant_id=tenant_id,
            doc_id=doc_id,
            doc_name=doc_name,
            doc_type=doc_type,
            doc_url=file_path,
            status='pending',
            document_metadata=metadata
        )

        with self.db.auto_commit():
            self.db.session.add(document)

        return document

    def get_document_by_doc_id(self, doc_id: str) -> Optional[KnowledgeDocument]:
        """根据doc_id查询文档"""
        return self.db.session.query(KnowledgeDocument).filter_by(doc_id=doc_id).first()

    def get_document_status(self, doc_id: str, tenant_id: str) -> Optional[KnowledgeDocument]:
        """查询文档处理状态"""
        return self.db.session.query(KnowledgeDocument).filter_by(
            doc_id=doc_id, tenant_id=tenant_id
        ).first()

    def parse_document(self, file_path: str, doc_type: str) -> str:
        """按文件类型解析文档，返回纯文本"""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return ParserFactory.parse(file_content, doc_type)

    def parse_to_documents(self, file_path: str, doc_type: str) -> List[Document]:
        """按文件类型解析文档，返回LangChain Document列表"""
        with open(file_path, 'rb') as f:
            file_content = f.read()
        return ParserFactory.parse_to_documents(file_content, doc_type)

    def split_documents(self, documents: List[Document]) -> List[Document]:
        """使用LangChain文本分割器切割Document列表"""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        return text_splitter.split_documents(documents)

    def generate_qa_pairs(self, documents: List[Document]) -> List[Dict]:
        """使用DoctranQATransformer从文档生成QA对"""
        if not documents:
            return []

        qa_pairs = []

        try:
            qa_documents = self._qa_transformer.transform_documents(documents)

            for qa_doc in qa_documents:
                if hasattr(qa_doc, 'metadata') and qa_doc.metadata:
                    questions = qa_doc.metadata.get('questions', [])
                    if isinstance(questions, list):
                        for qa in questions:
                            if isinstance(qa, dict) and 'question' in qa and 'answer' in qa:
                                qa_pairs.append({
                                    "question": qa['question'],
                                    "answer": qa['answer']
                                })
        except Exception:
            pass

        return qa_pairs

    def vectorize_and_store(self, doc_id: str, qa_pairs: List[Dict]) -> int:
        """使用LangChain Embedding向量化并存储，返回存储的对数"""
        if not qa_pairs:
            return 0

        document = self.get_document_by_doc_id(doc_id)
        if not document:
            return 0

        questions = [pair["question"] for pair in qa_pairs]
        vectors = self.embedding_service.embed_texts(questions)

        stored_count = 0
        for pair, vector in zip(qa_pairs, vectors):
            qa_pair = KnowledgeQAPair(
                tenant_id=document.tenant_id,
                doc_id=doc_id,
                pair_id=str(uuid.uuid4()),
                question=pair["question"],
                answer=pair["answer"],
                question_vector=vector
            )
            self.db.session.add(qa_pair)
            stored_count += 1

        document.total_pairs = stored_count

        with self.db.auto_commit():
            pass

        return stored_count

    def update_document_status(self, doc_id: str, status: str,
                                error_message: Optional[str] = None):
        """更新文档状态"""
        document = self.get_document_by_doc_id(doc_id)
        if document:
            document.status = status
            if error_message:
                document.error_message = error_message
            if status == 'completed':
                import datetime
                document.processed_at = datetime.datetime.now()
            with self.db.auto_commit():
                pass

    def delete_document(self, doc_id: str, tenant_id: str) -> bool:
        """删除文档及关联的QA对"""
        document = self.get_document_status(doc_id, tenant_id)
        if not document:
            return False

        self.db.session.query(KnowledgeQAPair).filter_by(doc_id=doc_id).delete()

        with self.db.auto_commit():
            self.db.session.delete(document)

        if os.path.exists(document.doc_url):
            try:
                os.remove(document.doc_url)
                doc_dir = os.path.dirname(document.doc_url)
                if os.path.isdir(doc_dir) and not os.listdir(doc_dir):
                    os.rmdir(doc_dir)
            except Exception:
                pass

        return True

    def _get_doc_type(self, filename: str) -> str:
        """从文件名获取文档类型"""
        if '.' not in filename:
            return ''
        return filename.rsplit('.', 1)[-1].lower()