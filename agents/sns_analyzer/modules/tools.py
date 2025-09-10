"""Instagram API 호출 및 데이터 처리를 위한 도구 함수 모듈

Instagram Basic Display API를 사용하여 인플루언서의 성과 데이터를 수집하고
분석을 위한 메트릭을 계산하는 함수들을 제공합니다.

주요 기능:
- 계정 레벨 인사이트 조회
- 콘텐츠 목록 및 개별 인사이트 조회
- 오디언스 데이터 수집
- 파생 KPI 계산
"""

import requests
from typing import Dict, List, Optional, Any

from agents.sns_analyzer.modules.errors import (
    handle_requests_exception,
    InvalidParameterError,
    DataValidationError,
    DataProcessingError,
)


def get_account_insights(
    user_id: str, access_token: str, metrics: List[str], period: str = "day"
) -> Dict[str, Any]:
    """
    Instagram 계정 레벨 인사이트를 조회합니다.

    Args:
        user_id (str): Instagram 사용자 ID
        access_token (str): API 액세스 토큰
        metrics (List[str]): 조회할 메트릭 목록
        period (str): 조회 기간 ("day", "days_28", "lifetime")

    Returns:
        Dict[str, Any]: 계정 인사이트 데이터

    Raises:
        InvalidParameterError: 잘못된 매개변수가 전달된 경우
        InstagramAPIError: API 호출 실패 시
    """

    url = f"https://graph.instagram.com/{user_id}/insights"

    params = {
        "metric": ",".join(metrics),
        "period": period,
        "access_token": access_token,
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise handle_requests_exception(e, f"계정 인사이트 조회 (user_id: {user_id})")


def get_media_list(
    user_id: str,
    access_token: str,
    since: Optional[str] = None,
    until: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Instagram 미디어 목록을 조회합니다.

    Args:
        user_id (str): Instagram 사용자 ID
        access_token (str): API 액세스 토큰
        since (str): 시작 날짜 (YYYY-MM-DD 형식)
        until (str): 종료 날짜 (YYYY-MM-DD 형식)

    Returns:
        Dict[str, Any]: 미디어 목록 데이터

    Raises:
        InvalidParameterError: 잘못된 매개변수가 전달된 경우
        InstagramAPIError: API 호출 실패 시
    """

    url = f"https://graph.instagram.com/{user_id}/media"

    params = {
        "fields": "id,media_type,timestamp,caption,permalink,thumbnail_url,media_url",
        "access_token": access_token,
    }

    if since:
        params["since"] = since
    if until:
        params["until"] = until

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise handle_requests_exception(e, f"미디어 목록 조회 (user_id: {user_id})")


def get_media_insights(
    media_id: str, access_token: str, metrics: List[str]
) -> Dict[str, Any]:
    """
    특정 미디어의 인사이트를 조회합니다.

    Args:
        media_id (str): 미디어 ID
        access_token (str): API 액세스 토큰
        metrics (List[str]): 조회할 메트릭 목록

    Returns:
        Dict[str, Any]: 미디어 인사이트 데이터

    Raises:
        InvalidParameterError: 잘못된 매개변수가 전달된 경우
        InstagramAPIError: API 호출 실패 시
    """

    url = f"https://graph.instagram.com/{media_id}/insights"

    params = {"metric": ",".join(metrics), "access_token": access_token}

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise handle_requests_exception(
            e, f"미디어 인사이트 조회 (media_id: {media_id})"
        )


def calculate_engagement_metrics(
    media_insights: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    미디어 인사이트 데이터로부터 참여 메트릭을 계산합니다.

    Args:
        media_insights (List[Dict[str, Any]]): 미디어별 인사이트 데이터 목록

    Returns:
        Dict[str, Any]: 계산된 참여 메트릭

    Raises:
        InvalidParameterError: 잘못된 매개변수가 전달된 경우
        DataProcessingError: 데이터 처리 중 오류 발생 시
    """

    if not media_insights:
        raise InvalidParameterError(
            "media_insights", media_insights, "비어있지 않은 리스트"
        )

    try:
        # 참여 관련 메트릭 이름들
        engagement_metrics = {"likes", "comments", "saved", "shares"}

        total_metrics = {
            "likes": 0.0,
            "comments": 0.0,
            "saved": 0.0,
            "shares": 0.0,
            "reach": 0.0,
            "impressions": 0.0,
            "engagement": 0.0,
        }

        individual_posts = []
        content_count = len(media_insights)

        for i, media in enumerate(media_insights):
            if not isinstance(media, dict):
                raise DataValidationError(
                    f"미디어 데이터가 딕셔너리 형태가 아닙니다: {type(media).__name__}"
                )

            post_metrics = {metric: 0.0 for metric in total_metrics.keys()}

            if "data" in media:
                for metric in media["data"]:
                    if not isinstance(metric, dict):
                        continue

                    metric_name = metric.get("name", "")

                    # 추적하는 메트릭만 처리
                    if metric_name not in total_metrics and metric_name != "saved":
                        continue

                    try:
                        metric_value = _extract_metric_value(metric)
                        if metric_name in total_metrics:
                            post_metrics[metric_name] = metric_value
                            total_metrics[metric_name] += metric_value
                    except DataValidationError:
                        # 특정 메트릭에서 데이터 오류가 발생해도 다른 메트릭은 계속 처리
                        continue

                # 개별 게시물의 참여도 계산
                post_engagement = sum(
                    post_metrics[metric]
                    for metric in engagement_metrics
                    if metric in post_metrics
                )
                post_metrics["engagement"] = post_engagement
                total_metrics["engagement"] += post_engagement

                # 개별 게시물 참여율 계산
                post_reach = post_metrics.get("reach", 0)
                post_engagement_rate = (
                    (post_engagement / post_reach) * 100 if post_reach > 0 else 0
                )

                individual_posts.append(
                    {
                        "index": i,
                        "metrics": post_metrics,
                        "engagement_rate": round(post_engagement_rate, 2),
                    }
                )

        # 전체 통계 계산
        total_engagement = total_metrics["engagement"]
        total_reach = total_metrics["reach"]
        total_impressions = total_metrics["impressions"]

        avg_engagement_rate = (
            (total_engagement / total_reach) * 100 if total_reach > 0 else 0
        )
        avg_impressions_per_post = (
            total_impressions / content_count if content_count > 0 else 0
        )
        avg_engagement_per_post = (
            total_engagement / content_count if content_count > 0 else 0
        )

        # 개별 게시물 참여율 분석
        engagement_rates = [post["engagement_rate"] for post in individual_posts]
        best_post_idx = (
            max(range(len(engagement_rates)), key=lambda i: engagement_rates[i])
            if engagement_rates
            else None
        )
        worst_post_idx = (
            min(range(len(engagement_rates)), key=lambda i: engagement_rates[i])
            if engagement_rates
            else None
        )

        result = {
            # 기본 합계 메트릭
            "total_engagement": total_engagement,
            "total_reach": total_reach,
            "total_impressions": total_impressions,
            "total_likes": total_metrics["likes"],
            "total_comments": total_metrics["comments"],
            "total_saves": total_metrics["saved"],
            "total_shares": total_metrics["shares"],
            # 평균 메트릭
            "content_count": content_count,
            "average_engagement_rate": round(avg_engagement_rate, 2),
            "average_impressions_per_post": round(avg_impressions_per_post, 2),
            "average_engagement_per_post": round(avg_engagement_per_post, 2),
            # 성과 분석
            "best_performing_post_index": best_post_idx,
            "worst_performing_post_index": worst_post_idx,
            "best_engagement_rate": round(engagement_rates[best_post_idx], 2)
            if best_post_idx is not None
            else 0,
            "worst_engagement_rate": round(engagement_rates[worst_post_idx], 2)
            if worst_post_idx is not None
            else 0,
            # 상세 데이터 (선택적)
            "individual_posts": individual_posts,
        }

        return result

    except Exception as e:
        if isinstance(e, (InvalidParameterError, DataValidationError)):
            raise
        raise DataProcessingError(
            f"참여 메트릭 계산 중 오류 발생: {str(e)}", "engagement_calculation"
        )


def _extract_metric_value(metric: Dict[str, Any]) -> int | float:
    """
    메트릭에서 값을 추출합니다.

    Args:
        metric (Dict[str, Any]): 메트릭 딕셔너리

    Returns:
        int | float: 추출된 값 (원본 타입 유지)

    Raises:
        DataValidationError: 메트릭 데이터 구조가 잘못되거나 값이 없는 경우
    """
    metric_name = metric.get("name", "unknown")
    metric_values = metric.get("values", [])

    if not metric_values:
        raise DataValidationError(f"메트릭 '{metric_name}'의 values가 비어있습니다")

    if not isinstance(metric_values[0], dict):
        raise DataValidationError(
            f"메트릭 '{metric_name}'의 values[0]이 딕셔너리가 아닙니다"
        )

    metric_value = metric_values[0].get("value")

    # 값이 없는 경우도 에러 발생
    if metric_value is None:
        raise DataValidationError(f"메트릭 '{metric_name}'의 value가 없습니다 (null)")

    # 숫자가 아닌 값 처리
    if not isinstance(metric_value, (int, float)):
        raise DataValidationError(
            f"메트릭 '{metric_name}'의 값이 숫자가 아닙니다: {type(metric_value).__name__}"
        )

    return metric_value


def calculate_follower_growth(account_insights: Dict[str, Any]) -> Dict[str, Any]:
    """
    팔로워 증가량을 계산합니다.

    Args:
        account_insights (Dict[str, Any]): 계정 인사이트 데이터

    Returns:
        Dict[str, Any]: 팔로워 성장 메트릭
    """
    follower_data = []

    if "data" in account_insights:
        for metric in account_insights["data"]:
            if metric.get("name") == "follower_count":
                follower_data = metric.get("values", [])
                break

    if len(follower_data) < 2:
        return {"follower_growth": 0, "growth_rate": 0}

    start_count = follower_data[0].get("value", 0)
    end_count = follower_data[-1].get("value", 0)

    follower_growth = end_count - start_count
    growth_rate = (follower_growth / start_count) * 100 if start_count > 0 else 0

    return {
        "start_follower_count": start_count,
        "end_follower_count": end_count,
        "follower_growth": follower_growth,
        "growth_rate": round(growth_rate, 2),
    }


def get_content_performance_by_type(
    media_list: List[Dict[str, Any]], media_insights: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    콘텐츠 타입별 성과를 분석합니다.

    Args:
        media_list (List[Dict[str, Any]]): 미디어 목록
        media_insights (List[Dict[str, Any]]): 미디어 인사이트 목록

    Returns:
        Dict[str, Any]: 콘텐츠 타입별 성과 데이터
    """
    performance_by_type = {}

    # 미디어 타입별로 그룹화
    for i, media in enumerate(media_list):
        media_type = media.get("media_type", "unknown")

        if media_type not in performance_by_type:
            performance_by_type[media_type] = {
                "count": 0,
                "total_engagement": 0,
                "total_reach": 0,
                "total_impressions": 0,
            }

        performance_by_type[media_type]["count"] += 1

        # 해당 미디어의 인사이트 찾기
        if i < len(media_insights) and "data" in media_insights[i]:
            for metric in media_insights[i]["data"]:
                metric_name = metric.get("name", "")
                metric_value = metric.get("values", [{}])[0].get("value", 0)

                if metric_name in ["likes", "comments", "saved", "shares"]:
                    performance_by_type[media_type]["total_engagement"] += metric_value
                elif metric_name == "reach":
                    performance_by_type[media_type]["total_reach"] += metric_value
                elif metric_name == "impressions":
                    performance_by_type[media_type]["total_impressions"] += metric_value

    # 평균 계산
    for media_type in performance_by_type:
        data = performance_by_type[media_type]
        count = data["count"]

        if count > 0:
            data["avg_engagement"] = round(data["total_engagement"] / count, 2)
            data["avg_reach"] = round(data["total_reach"] / count, 2)
            data["avg_impressions"] = round(data["total_impressions"] / count, 2)
            data["avg_engagement_rate"] = (
                round((data["total_engagement"] / data["total_reach"]) * 100, 2)
                if data["total_reach"] > 0
                else 0
            )

    return performance_by_type
