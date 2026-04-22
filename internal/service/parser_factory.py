#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/21
@Author  : thezehui@gmail.com
@File    : parser_factory.py
"""
from typing import Iterator, List
import tempfile
import os

from langchain_core.document_loaders import Blob
from langchain_core.document_loaders.base import BaseBlobParser
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, UnstructuredFileLoader
from langchain_community.document_loaders.excel import UnstructuredExcelLoader
from langchain_community.document_loaders.csv_loader import CSVLoader


class DocxBlobParser(BaseBlobParser):
    """使用LangChain Blob解析docx文件"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        temp_path = self._save_temp(blob)
        loader = UnstructuredFileLoader(temp_path)
        for doc in loader.load():
            doc.metadata["source"] = blob.source or "docx"
            yield doc
        self._cleanup_temp(temp_path)

    def _save_temp(self, blob: Blob) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as f:
            if blob.data is not None:
                f.write(blob.data)
            else:
                with blob.as_bytes_io() as source:
                    f.write(source.read())
            return f.name

    def _cleanup_temp(self, path: str):
        try:
            os.remove(path)
        except Exception:
            pass


class PdfBlobParser(BaseBlobParser):
    """使用LangChain Blob解析pdf文件"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        temp_path = self._save_temp(blob)
        loader = PyPDFLoader(temp_path)
        for doc in loader.load():
            doc.metadata["source"] = blob.source or "pdf"
            yield doc
        self._cleanup_temp(temp_path)

    def _save_temp(self, blob: Blob) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as f:
            if blob.data is not None:
                f.write(blob.data)
            else:
                with blob.as_bytes_io() as source:
                    f.write(source.read())
            return f.name

    def _cleanup_temp(self, path: str):
        try:
            os.remove(path)
        except Exception:
            pass


class ExcelBlobParser(BaseBlobParser):
    """使用LangChain Blob解析xlsx文件"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        temp_path = self._save_temp(blob)
        loader = UnstructuredExcelLoader(temp_path)
        for doc in loader.load():
            doc.metadata["source"] = blob.source or "xlsx"
            yield doc
        self._cleanup_temp(temp_path)

    def _save_temp(self, blob: Blob) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as f:
            if blob.data is not None:
                f.write(blob.data)
            else:
                with blob.as_bytes_io() as source:
                    f.write(source.read())
            return f.name

    def _cleanup_temp(self, path: str):
        try:
            os.remove(path)
        except Exception:
            pass


class CsvBlobParser(BaseBlobParser):
    """使用LangChain Blob解析csv文件"""

    def lazy_parse(self, blob: Blob) -> Iterator[Document]:
        temp_path = self._save_temp(blob)
        loader = CSVLoader(temp_path)
        for doc in loader.load():
            doc.metadata["source"] = blob.source or "csv"
            yield doc
        self._cleanup_temp(temp_path)

    def _save_temp(self, blob: Blob) -> str:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as f:
            if blob.data is not None:
                f.write(blob.data)
            else:
                with blob.as_bytes_io() as source:
                    f.write(source.read())
            return f.name

    def _cleanup_temp(self, path: str):
        try:
            os.remove(path)
        except Exception:
            pass


class ParserFactory:
    """基于LangChain Blob的解析器工厂"""

    _parsers = {
        'docx': DocxBlobParser,
        'pdf': PdfBlobParser,
        'xlsx': ExcelBlobParser,
        'csv': CsvBlobParser,
    }

    @classmethod
    def get_parser(cls, doc_type: str) -> BaseBlobParser:
        parser_class = cls._parsers.get(doc_type.lower())
        if not parser_class:
            raise ValueError(f"Unsupported document type: {doc_type}")
        return parser_class()

    @classmethod
    def parse(cls, file_content: bytes, doc_type: str) -> str:
        parser = cls.get_parser(doc_type)
        blob = Blob(data=file_content)
        return "\n".join(doc.page_content for doc in parser.lazy_parse(blob))

    @classmethod
    def parse_to_documents(cls, file_content: bytes, doc_type: str) -> List[Document]:
        parser = cls.get_parser(doc_type)
        blob = Blob(data=file_content)
        return list(parser.lazy_parse(blob))