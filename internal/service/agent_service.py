#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/22
@Author  : thezehui@gmail.com
@File    : agent_service.py
"""
import os
import uuid
import tiktoken
from typing import List, Dict, Any, Optional, Tuple, Callable

from injector import inject
from dataclasses import dataclass, field
from langchain_openai import OpenAI, ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.graph import END, StateGraph
from sqlalchemy import text

from internal.model.agent import GraphState, Document
from internal.service.embedding_service import EmbeddingService
from pkg.flask_sqlalchemy import SQLAlchemy

MAX_TOKEN_LIMIT = 2800
SUMMARY_REFRESH_THRESHOLD = 2500
BUFFER_KEEP_ROUNDS = 3

SUMMARY_LLM = OpenAI(model="deepseek-chat",
                      api_key=os.getenv("DEEPSEEK_API_KEY"),
                      base_url=os.getenv("DEEPSEEK_BASE_URL"),
                      temperature=0)
MAIN_LLM = ChatOpenAI(model="deepseek-chat",
                      api_key=os.getenv("DEEPSEEK_API_KEY"),
                      base_url=os.getenv("DEEPSEEK_BASE_URL"),
                      temperature=0.7)
TOKEN_ENCODER = tiktoken.get_encoding("cl100k_base")

_session_memory_store: Dict[str, Dict[str, Any]] = {}
_message_store: Dict[str, List[Dict[str, Any]]] = {}


def _generate_message_id() -> str:
    return str(uuid.uuid4())


def _build_memory_key(tenant_id: str, session_id: str) -> str:
    return f"{tenant_id}:{session_id}"


def _load_session_memory(tenant_id: str, session_id: str) -> Tuple[Optional[str], List[Dict[str, Any]]]:
    key = _build_memory_key(tenant_id, session_id)
    memory = _session_memory_store.get(key)
    if not memory:
        return None, []
    return memory.get("session_summary"), memory.get("buffer", [])


def _save_session_memory(tenant_id: str, session_id: str, session_summary: str, buffer: List[Dict[str, Any]]):
    key = _build_memory_key(tenant_id, session_id)
    _session_memory_store[key] = {
        "session_summary": session_summary,
        "buffer": buffer
    }


def _persist_visitor_message(session_id: str, tenant_id: str, message_id: str, content: str):
    msg_key = f"{tenant_id}:{session_id}"
    if msg_key not in _message_store:
        _message_store[msg_key] = []
    _message_store[msg_key].append({
        "message_id": message_id,
        "direction": "toCore",
        "sender_type": "visitor",
        "sender_id": None,
        "content_type": "text",
        "content": content,
        "msg_status": "sent"
    })


def _persist_ai_message(session_id: str, tenant_id: str, message_id: str, content: str):
    msg_key = f"{tenant_id}:{session_id}"
    if msg_key not in _message_store:
        _message_store[msg_key] = []
    _message_store[msg_key].append({
        "message_id": message_id,
        "direction": "toUser",
        "sender_type": "ai",
        "sender_id": None,
        "content_type": "text",
        "content": content,
        "msg_status": "sent"
    })


def _vector_search(tenant_id: str, query_vector: List[float], top_k: int = 5) -> List[Document]:
    try:
        from internal.extension.database import db
        from internal.model.knowledge_qa_pair import KnowledgeQAPair

        results = db.session.query(
            KnowledgeQAPair.question,
            KnowledgeQAPair.answer,
            KnowledgeQAPair.question_vector
        ).filter(
            KnowledgeQAPair.tenant_id == tenant_id
        ).all()

        scored = []
        for q, a, vec in results:
            if vec is None:
                continue
            similarity = sum(qv * ev for qv, ev in zip(query_vector, vec))
            scored.append((similarity, q, a))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            Document(content=f"Q: {q}\nA: {a}", score=sim, source=None)
            for sim, q, a in scored[:top_k]
        ]
    except Exception:
        return []


@inject
@dataclass
class AgentService:
    embedding_service: EmbeddingService
    db: SQLAlchemy = field(default_factory=None)
    _stream_callback: Optional[Callable[[str], None]] = field(default=None, init=False)

    def set_stream_callback(self, callback: Optional[Callable[[str], None]]):
        self._stream_callback = callback

    def load_memory(self, state: GraphState) -> GraphState:
        session_summary, buffer = _load_session_memory(state.tenant_id, state.session_id)
        state.session_summary = session_summary or ""
        state.buffer = buffer

        buffer_str = self._format_buffer(buffer)
        state.context = f"{state.system_prompt}\n{state.session_summary}\n{buffer_str}\n用户：{state.user_input}"
        state.token_count = len(TOKEN_ENCODER.encode(state.context))
        return state

    def token_check(self, state: GraphState) -> str:
        if state.token_count > SUMMARY_REFRESH_THRESHOLD:
            return "update_summary"
        return "tool_decision"

    def update_summary(self, state: GraphState) -> GraphState:
        buffer_str = self._format_buffer(state.buffer)
        summary_prompt = PromptTemplate(
            template="请总结以下对话内容，保留核心信息，简洁明了，不超过300字：\n{content}",
            input_variables=["content"]
        )
        summary_chain = summary_prompt | SUMMARY_LLM
        new_summary = summary_chain.invoke({"content": f"{state.session_summary}\n{buffer_str}"})

        if len(state.buffer) > BUFFER_KEEP_ROUNDS:
            state.buffer = state.buffer[-BUFFER_KEEP_ROUNDS:]

        new_buffer_str = self._format_buffer(state.buffer)
        state.context = f"{state.system_prompt}\n{new_summary}\n{new_buffer_str}\n用户：{state.user_input}"
        state.session_summary = new_summary
        state.token_count = len(TOKEN_ENCODER.encode(state.context))
        return state

    def tool_decision(self, state: GraphState) -> str:
        decision_prompt = PromptTemplate(
            template="基于上下文：{context}\n判断用户问题「{user_input}」是否需要调用知识库检索工具？仅回答「需要」或「不需要」",
            input_variables=["context", "user_input"]
        )
        decision_chain = decision_prompt | MAIN_LLM
        decision = decision_chain.invoke({"context": state.context, "user_input": state.user_input})
        state.need_rag = (decision.strip() == "需要")
        return "rag_retrieval" if state.need_rag else "generate_response"

    def rag_retrieval(self, state: GraphState) -> GraphState:
        try:
            query_vector = self.embedding_service.embed_query(state.user_input)
            docs = _vector_search(state.tenant_id, query_vector, top_k=5)
            state.rag_documents = docs
            rag_str = "\n".join([f"知识库参考{idx+1}：{doc.content}" for idx, doc in enumerate(docs)])
            state.context = f"{state.context}\n{rag_str}"
        except Exception:
            state.rag_documents = []
        return state

    def generate_response(self, state: GraphState, stream_callback: Optional[Callable[[str], None]] = None) -> GraphState:
        response_prompt = PromptTemplate(
            template="{context}\n请结合上述信息，准确、简洁地回答用户问题，不要添加无关内容。",
            input_variables=["context"]
        )
        response_chain = response_prompt | MAIN_LLM
        callback = stream_callback or self._stream_callback
        if state.stream and callback:
            state.response = ""
            for chunk in response_chain.stream({"context": state.context}):
                state.response += chunk
                callback(chunk)
        elif state.stream:
            state.response = ""
            for chunk in response_chain.stream({"context": state.context}):
                state.response += chunk
        else:
            state.response = response_chain.invoke({"context": state.context})
        return state

    def save_memory(self, state: GraphState) -> GraphState:
        state.message_id = _generate_message_id()

        _persist_visitor_message(state.session_id, state.tenant_id, state.message_id, state.user_input)

        ai_message_id = _generate_message_id()
        _persist_ai_message(state.session_id, state.tenant_id, ai_message_id, state.response)

        state.buffer.append({
            "message_id": state.message_id,
            "sender_type": "visitor",
            "content": state.user_input
        })
        state.buffer.append({
            "message_id": ai_message_id,
            "sender_type": "ai",
            "content": state.response
        })

        _save_session_memory(state.tenant_id, state.session_id, state.session_summary or "", state.buffer)
        return state

    def _format_buffer(self, buffer: List[Dict[str, Any]]) -> str:
        if not buffer:
            return ""
        return "\n".join([
            f"用户：{item.get('content', '')}" if item.get('sender_type') == 'visitor'
            else f"助手：{item.get('content', '')}"
            for item in buffer
        ])

    def _build_workflow(self):
        workflow = StateGraph(GraphState)

        workflow.add_node("load_memory", self.load_memory)
        workflow.add_node("token_check", self.token_check)
        workflow.add_node("update_summary", self.update_summary)
        workflow.add_node("tool_decision", self.tool_decision)
        workflow.add_node("rag_retrieval", self.rag_retrieval)
        workflow.add_node("generate_response", self.generate_response)
        workflow.add_node("save_memory", self.save_memory)

        workflow.set_entry_point("load_memory")
        workflow.add_edge("load_memory", "token_check")
        workflow.add_edge("token_check", "update_summary")
        workflow.add_edge("token_check", "tool_decision")
        workflow.add_edge("update_summary", "tool_decision")
        workflow.add_edge("tool_decision", "rag_retrieval")
        workflow.add_edge("tool_decision", "generate_response")
        workflow.add_edge("rag_retrieval", "generate_response")
        workflow.add_edge("generate_response", "save_memory")
        workflow.add_edge("save_memory", END)

        return workflow.compile()

    def invoke_agent(self, tenant_id: str, session_id: str, user_input: str, system_prompt: str, stream: bool = False) -> Dict[str, Any]:
        graph = self._build_workflow()
        initial_state = GraphState(
            tenant_id=tenant_id,
            session_id=session_id,
            user_input=user_input,
            system_prompt=system_prompt,
            stream=stream
        )
        final_state = graph.invoke(initial_state)
        return {
            "response": final_state.response,
            "message_id": final_state.message_id,
            "need_rag": final_state.need_rag,
            "session_summary": final_state.session_summary or ""
        }
