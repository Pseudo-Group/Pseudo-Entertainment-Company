"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.

아래는 예시입니다.
"""

from agents.base_node import BaseNode
from agents.sns_analyzer.modules.chains import set_instagram_data_collection_chain
from agents.sns_analyzer.modules.state import InstagramAnalysisState
from agents.sns_analyzer.modules.tools import (
    get_account_insights,
    get_media_list,
    get_media_insights,
    calculate_engagement_metrics,
    calculate_follower_growth,
    get_content_performance_by_type,
)
from agents.sns_analyzer.modules.errors import (
    InstagramError,
    InvalidParameterError,
    DataProcessingError,
    is_retryable_error,
    get_retry_delay,
)
from typing import List, Dict, Any, Tuple
import time
import calendar


class InstagramDataCollectorNode(BaseNode):
    """
    Instagram API를 통해 계정 인사이트, 미디어 목록, 개별 미디어 인사이트를 수집하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        self.chain = (
            set_instagram_data_collection_chain()
        )  # Instagram 데이터 수집 체인 설정

    def execute(self, state: InstagramAnalysisState) -> dict:
        """
        Instagram API를 호출하여 계정 및 콘텐츠 데이터를 수집합니다.
        """
        user_id = state["instagram_user_id"]
        access_token = state["access_token"]
        analysis_period = state["analysis_period"]
        api_errors = []

        try:
            # 1. 계정 인사이트 수집
            account_insights = self._collect_account_insights(
                user_id, access_token, api_errors
            )

            # 2. 미디어 목록 수집
            media_list = self._collect_media_list(
                user_id, access_token, analysis_period, api_errors
            )

            # 3. 개별 미디어 인사이트 수집
            media_insights = self._collect_media_insights(
                media_list, access_token, api_errors
            )

            # 4. 파생 메트릭 계산
            calculated_metrics = self._calculate_derived_metrics(
                account_insights, media_list, media_insights
            )

            # 5. 상태 업데이트
            self._update_state(
                state,
                account_insights,
                media_list,
                media_insights,
                calculated_metrics,
                api_errors,
            )

            # 6. 체인을 통해 결과 처리 (현재는 패스스루)
            result = self.chain.invoke(state)  # noqa: F841

            # 수집 결과 요약
            summary = self._create_summary(
                account_insights,
                media_list,
                media_insights,
                calculated_metrics,
                api_errors,
            )

            return {"response": f"Instagram 데이터 수집 완료: {summary}"}

        except Exception as e:
            error_msg = f"데이터 수집 중 예외 발생: {str(e)}"
            state["api_errors"] = api_errors + [error_msg]
            return {"response": error_msg}

    def _collect_account_insights(
        self, user_id: str, access_token: str, api_errors: List[str]
    ) -> Dict[str, Any]:
        """계정 레벨 인사이트를 수집합니다."""
        print("📊 계정 인사이트 수집 중...")

        account_insights = {}

        # 각 타입별 인사이트 수집
        insight_configs = [
            ("monthly", ["impressions", "reach"], "days_28"),
            (
                "daily",
                ["impressions", "reach", "profile_views", "follower_count"],
                "day",
            ),
            (
                "audience",
                ["audience_gender_age", "audience_country", "audience_city"],
                "lifetime",
            ),
        ]

        for insight_type, metrics, period in insight_configs:
            try:
                insights = get_account_insights(user_id, access_token, metrics, period)
                account_insights[insight_type] = insights

            except InstagramError as e:
                error_msg = f"계정 인사이트 ({insight_type}) 수집 실패: {e.message}"
                api_errors.append(error_msg)
                print(f"❌ {error_msg}")

                # 빈 데이터로 설정하여 다른 처리 계속 진행
                account_insights[insight_type] = {"data": []}

            except Exception as e:
                error_msg = (
                    f"계정 인사이트 ({insight_type}) 수집 중 예상치 못한 오류: {str(e)}"
                )
                api_errors.append(error_msg)
                print(f"❌ {error_msg}")
                account_insights[insight_type] = {"data": []}

        return account_insights

    def _collect_media_list(
        self,
        user_id: str,
        access_token: str,
        analysis_period: str,
        api_errors: List[str],
    ) -> List[Dict[str, Any]]:
        """미디어 목록을 수집합니다."""
        print("📋 미디어 목록 수집 중...")

        try:
            # 분석 기간 파싱
            since_date, until_date = self._parse_analysis_period(analysis_period)

            media_data = get_media_list(user_id, access_token, since_date, until_date)
            media_list = media_data.get("data", [])

            print(f"📊 {len(media_list)}개 콘텐츠 발견")
            return media_list

        except InstagramError as e:
            error_msg = f"미디어 목록 수집 실패: {e.message}"
            api_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return []

        except Exception as e:
            error_msg = f"미디어 목록 수집 중 예상치 못한 오류: {str(e)}"
            api_errors.append(error_msg)
            print(f"❌ {error_msg}")
            return []

    def _collect_media_insights(
        self, media_list: List[Dict[str, Any]], access_token: str, api_errors: List[str]
    ) -> List[Dict[str, Any]]:
        """개별 미디어 인사이트를 수집합니다."""
        print("🔍 개별 콘텐츠 인사이트 수집 중...")

        media_insights = []

        for i, media in enumerate(media_list):
            media_id = media.get("id")
            media_type = media.get("media_type", "unknown")

            if not media_id:
                print(f"⚠️ {i + 1}번째 미디어의 ID가 없습니다. 건너뜁니다.")
                continue

            try:
                # 미디어 타입별 메트릭 설정
                metrics = self._get_metrics_by_media_type(media_type)

                # API 호출
                insight_data = get_media_insights(media_id, access_token, metrics)
                media_insights.append(insight_data)

                print(f"✅ {i + 1}/{len(media_list)} 완료")

            except InstagramError as e:
                error_msg = f"미디어 {media_id} 인사이트 수집 실패: {e.message}"
                api_errors.append(error_msg)
                print(f"❌ {error_msg}")

                # 재시도 가능한 에러인 경우 짧은 대기 후 한 번 더 시도
                if is_retryable_error(e):
                    retry_delay = get_retry_delay(e) or 2
                    print(f"🔄 {retry_delay}초 후 재시도...")
                    time.sleep(retry_delay)

                    try:
                        insight_data = get_media_insights(
                            media_id, access_token, metrics
                        )
                        media_insights.append(insight_data)
                        print(f"✅ {i + 1}/{len(media_list)} 재시도 성공")
                    except Exception:
                        print(f"❌ {i + 1}/{len(media_list)} 재시도 실패")

                continue

            except Exception as e:
                error_msg = (
                    f"미디어 {media_id} 인사이트 수집 중 예상치 못한 오류: {str(e)}"
                )
                api_errors.append(error_msg)
                print(f"❌ {error_msg}")
                continue

            # API 호출 제한 방지를 위한 지연
            if i > 0 and i % 10 == 0:
                time.sleep(1)

        return media_insights

    def _calculate_derived_metrics(
        self,
        account_insights: Dict[str, Any],
        media_list: List[Dict[str, Any]],
        media_insights: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """파생 메트릭을 계산합니다."""
        print("📈 파생 메트릭 계산 중...")

        calculated_metrics = {}

        # 참여 메트릭 계산
        if media_insights:
            try:
                engagement_metrics = calculate_engagement_metrics(media_insights)
                calculated_metrics["engagement"] = engagement_metrics
                print("✅ 참여 메트릭 계산 완료")
            except (InvalidParameterError, DataProcessingError) as e:
                print(f"❌ 참여 메트릭 계산 실패: {e.message}")
            except Exception as e:
                print(f"❌ 참여 메트릭 계산 중 예상치 못한 오류: {str(e)}")

        # 팔로워 성장률 계산
        daily_insights = account_insights.get("daily", {})
        if (
            daily_insights
            and isinstance(daily_insights, dict)
            and "data" in daily_insights
        ):
            try:
                follower_growth = calculate_follower_growth(daily_insights)
                calculated_metrics["follower_growth"] = follower_growth
                print("✅ 팔로워 성장률 계산 완료")
            except Exception as e:
                print(f"❌ 팔로워 성장률 계산 실패: {str(e)}")

        # 콘텐츠 타입별 성과 계산
        if media_list and media_insights:
            try:
                content_performance = get_content_performance_by_type(
                    media_list, media_insights
                )
                calculated_metrics["content_performance"] = content_performance
                print("✅ 콘텐츠 타입별 성과 계산 완료")
            except Exception as e:
                print(f"❌ 콘텐츠 타입별 성과 계산 실패: {str(e)}")

        return calculated_metrics

    def _update_state(
        self,
        state: InstagramAnalysisState,
        account_insights: Dict[str, Any],
        media_list: List[Dict[str, Any]],
        media_insights: List[Dict[str, Any]],
        calculated_metrics: Dict[str, Any],
        api_errors: List[str],
    ) -> None:
        """상태를 업데이트합니다."""
        state["account_insights"] = account_insights
        state["media_list"] = media_list
        state["media_insights"] = media_insights
        state["calculated_metrics"] = calculated_metrics
        state["api_errors"] = api_errors if api_errors else None

    def _create_summary(
        self,
        account_insights: Dict[str, Any],
        media_list: List[Dict[str, Any]],
        media_insights: List[Dict[str, Any]],
        calculated_metrics: Dict[str, Any],
        api_errors: List[str],
    ) -> Dict[str, Any]:
        """수집 결과 요약을 생성합니다."""
        summary = {
            "account_insights_collected": len(
                [k for k, v in account_insights.items() if "error" not in v]
            ),
            "media_count": len(media_list),
            "media_insights_collected": len(media_insights),
            "calculated_metrics": list(calculated_metrics.keys()),
            "api_errors_count": len(api_errors),
        }

        print(f"✨ 데이터 수집 완료: {summary}")
        return summary

    def _parse_analysis_period(self, period: str) -> Tuple[str, str]:
        """
        분석 기간을 파싱하여 시작/종료 날짜를 반환합니다.

        Args:
            period (str): 분석 기간 (예: "2024-01" 또는 "2024-01-01_2024-01-31")

        Returns:
            Tuple[str, str]: (since_date, until_date)
        """
        if "_" in period:
            # "2024-01-01_2024-01-31" 형식
            since_date, until_date = period.split("_")
        else:
            # "2024-01" 형식 -> 해당 월의 첫날과 마지막날
            year, month = period.split("-")
            since_date = f"{year}-{month}-01"

            # 마지막 날 계산
            last_day = calendar.monthrange(int(year), int(month))[1]
            until_date = f"{year}-{month}-{last_day:02d}"

        return since_date, until_date

    def _get_metrics_by_media_type(self, media_type: str) -> List[str]:
        """
        미디어 타입에 따라 조회할 메트릭을 결정합니다.

        Args:
            media_type (str): 미디어 타입 ("IMAGE", "VIDEO", "CAROUSEL_ALBUM", "STORY")

        Returns:
            List[str]: 조회할 메트릭 목록
        """
        # 공통 메트릭
        common_metrics = [
            "impressions",
            "reach",
            "likes",
            "comments",
            "saved",
            "shares",
        ]

        if media_type in ["VIDEO", "REEL"]:
            return common_metrics + ["plays", "video_views"]
        elif media_type == "STORY":
            return [
                "impressions",
                "reach",
                "taps_forward",
                "taps_back",
                "exits",
                "replies",
            ]
        else:  # 이미지, 캐러셀 등
            return common_metrics
