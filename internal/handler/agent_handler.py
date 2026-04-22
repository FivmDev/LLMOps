#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2026/4/22
@Author  : thezehui@gmail.com
@File    : agent_handler.py
"""
import threading
import queue
from flask import Response
from injector import inject
from dataclasses import dataclass

from internal.schema.agent_schema import AgentInvokeReq, AgentInvokeResp
from internal.service.agent_service import AgentService
from pkg.response import success_json, validation_error_json


@inject
@dataclass
class AgentHandler:
    """Agent 智能体控制器"""

    agent_service: AgentService

    def invoke(self) -> dict:
        req = AgentInvokeReq()
        if not req.model_validate(req.dict()):
            return validation_error_json(req.errors)

        if req.stream:
            return self._stream_response(req)
        else:
            return self._normal_response(req)

    def _normal_response(self, req: AgentInvokeReq) -> dict:
        result = self.agent_service.invoke_agent(
            tenant_id=req.tenant_id,
            session_id=req.session_id,
            user_input=req.user_input,
            system_prompt=req.system_prompt,
            stream=False
        )

        resp = AgentInvokeResp(
            response=result["response"],
            message_id=result["message_id"],
            need_rag=result["need_rag"],
            session_summary=result["session_summary"]
        )
        return success_json(resp.model_dump())

    def _stream_response(self, req: AgentInvokeReq) -> Response:
        chunk_queue: queue.Queue = queue.Queue()
        result_holder: dict = {}
        error_holder: list = []

        def stream_callback(chunk: str):
            chunk_queue.put(("chunk", chunk))

        def run_agent():
            try:
                self.agent_service.set_stream_callback(stream_callback)
                result = self.agent_service.invoke_agent(
                    tenant_id=req.tenant_id,
                    session_id=req.session_id,
                    user_input=req.user_input,
                    system_prompt=req.system_prompt,
                    stream=True
                )
                self.agent_service.set_stream_callback(None)
                result_holder["data"] = result
                chunk_queue.put(("done", None))
            except Exception as e:
                error_holder.append(e)
                chunk_queue.put(("error", str(e)))
            finally:
                self.agent_service.set_stream_callback(None)

        thread = threading.Thread(target=run_agent)
        thread.start()

        def generate():
            yield f"event: metadata\ndata: message_id: {req.session_id}\n\n"
            yield f"event: metadata\ndata: need_rag: false\n\n"
            yield f"event: metadata\ndata: session_summary: \n\n"

            while True:
                try:
                    event_type, data = chunk_queue.get(timeout=30)
                    if event_type == "done":
                        break
                    elif event_type == "error":
                        break
                    elif event_type == "chunk":
                        yield f"event: content\ndata: {data}\n\n"
                except queue.Empty:
                    yield "event: error\ndata: timeout\n\n"
                    break

            thread.join(timeout=5)
            yield "event: done\ndata: [DONE]\n\n"

        return Response(
            generate(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache',
                'X-Accel-Buffering': 'no',
                'Connection': 'keep-alive'
            }
        )
