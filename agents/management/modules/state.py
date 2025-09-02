"""
아래는 예시입니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypedDict, Optional, Dict, Any

from langgraph.graph.message import add_messages


class ManagementState(TypedDict):
    user_input: Optional[str]
    content_verification_result: Optional[Dict[str, Any]]
    response: Optional[str]
    intent_result: Optional[Dict[str, Any]]
    verification_result: Optional[Dict[str, Any]]
    analysis: Optional[str]
    content_text: Optional[str]
    content_type: Optional[str]
    # 입력 스키마에 포함되지 않아 드롭되던 키들을 명시적으로 허용
    image_url: Optional[str]
    text_content: Optional[str]
