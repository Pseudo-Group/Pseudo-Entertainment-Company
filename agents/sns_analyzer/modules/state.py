"""
아래는 예시입니다.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated, TypedDict, List, Dict, Optional

from langgraph.graph.message import add_messages


@dataclass
class InstagramAnalysisState(TypedDict):
    """
    Instagram 성과 분석 Workflow의 상태를 정의하는 TypedDict 클래스

    Instagram API를 통한 데이터 수집 및 월간 성과 분석을 위한 상태 정보를 정의합니다.
    인플루언서의 계정 정보, API 데이터, 분석 결과 등을 관리합니다.
    """

    instagram_user_id: str  # Instagram 사용자 ID (예: "17841400455970028")
    access_token: str  # Instagram Basic Display API 액세스 토큰
    analysis_period: str  # 분석 기간 (예: "2024-01", "2024-01-01_2024-01-31")
    request_type: str  # 요청 유형 (예: "monthly_analysis", "content_analysis")

    response: Annotated[list, add_messages]  # 응답 메시지 목록

    account_insights: Optional[Dict[str, any]] = None  # 계정 레벨 인사이트 데이터
    media_list: Optional[List[Dict[str, any]]] = None  # 콘텐츠 목록
    media_insights: Optional[List[Dict[str, any]]] = None  # 콘텐츠별 인사이트 데이터
    audience_data: Optional[Dict[str, any]] = None  # 오디언스 데이터

    calculated_metrics: Optional[Dict[str, any]] = None  # 파생 KPI (참여율, 성장률 등)

    analysis_report: Optional[str] = None  # 최종 분석 보고서

    api_errors: Optional[List[str]] = None  # API 호출 중 발생한 오류 목록
