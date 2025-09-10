"""Instagram API 및 데이터 처리를 위한 Custom Exception 모듈

Instagram API 호출, 데이터 처리, 분석 과정에서 발생할 수 있는
다양한 에러 상황을 체계적으로 분류하고 처리하기 위한 예외 클래스들을 정의합니다.

주요 예외 분류:
- API 관련 에러 (인증, 호출 제한, 네트워크 등)
- 데이터 처리 에러 (파싱, 검증, 계산 등)
- 설정 및 입력 에러 (잘못된 매개변수, 누락된 값 등)
"""

from typing import Optional, Dict, Any
import requests


class InstagramError(Exception):
    """
    Instagram 관련 작업에서 발생하는 모든 에러의 기본 클래스

    모든 Instagram 관련 예외는 이 클래스를 상속받아야 합니다.
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            message (str): 에러 메시지
            error_code (str, optional): 에러 코드 (API 응답의 에러 코드)
            retryable (bool): 재시도 가능 여부
            details (Dict[str, Any], optional): 추가 에러 상세 정보
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.retryable = retryable
        self.details = details or {}

    def __str__(self):
        error_info = [self.message]

        if self.error_code:
            error_info.append(f"코드: {self.error_code}")

        if self.retryable:
            error_info.append("(재시도 가능)")

        return " - ".join(error_info)


class InstagramAPIError(InstagramError):
    """
    Instagram API 호출과 관련된 에러의 기본 클래스
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        status_code: Optional[int] = None,
        retryable: bool = False,
        details: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            status_code (int, optional): HTTP 상태 코드
        """
        super().__init__(message, error_code, retryable, details)
        self.status_code = status_code


class AuthenticationError(InstagramAPIError):
    """
    인증 관련 에러 (잘못된 토큰, 만료된 토큰 등)
    """

    def __init__(self, message: str = "Instagram API 인증 실패"):
        super().__init__(
            message=message,
            error_code="AUTH_FAILED",
            retryable=False,  # 인증 에러는 일반적으로 재시도 불가능
        )


class RateLimitError(InstagramAPIError):
    """
    API 호출 제한 에러
    """

    def __init__(
        self, message: str = "API 호출 제한 초과", retry_after: Optional[int] = None
    ):
        """
        Args:
            retry_after (int, optional): 재시도까지 대기 시간(초)
        """
        super().__init__(
            message=message,
            error_code="RATE_LIMIT_EXCEEDED",
            retryable=True,
            details={"retry_after": retry_after},
        )
        self.retry_after = retry_after


class NetworkError(InstagramAPIError):
    """
    네트워크 연결 관련 에러
    """

    def __init__(self, message: str = "네트워크 연결 실패"):
        super().__init__(
            message=message,
            error_code="NETWORK_ERROR",
            retryable=True,  # 네트워크 에러는 재시도 가능
        )


class InvalidParameterError(InstagramError):
    """
    잘못된 매개변수나 입력값 에러
    """

    def __init__(self, parameter_name: str, value: Any, expected: str):
        """
        Args:
            parameter_name (str): 잘못된 매개변수 이름
            value (Any): 실제 전달된 값
            expected (str): 기대되는 값의 설명
        """
        message = f"잘못된 매개변수 '{parameter_name}': {value} (기대값: {expected})"

        super().__init__(
            message=message,
            error_code="INVALID_PARAMETER",
            retryable=False,
            details={
                "parameter_name": parameter_name,
                "actual_value": value,
                "expected": expected,
            },
        )


class DataValidationError(InstagramError):
    """
    데이터 검증 실패 에러
    """

    def __init__(self, message: str, field_name: Optional[str] = None):
        """
        Args:
            field_name (str, optional): 검증 실패한 필드명
        """
        super().__init__(
            message=message,
            error_code="DATA_VALIDATION_FAILED",
            retryable=False,
            details={"field_name": field_name} if field_name else {},
        )


class DataProcessingError(InstagramError):
    """
    데이터 처리 중 발생하는 에러 (계산, 변환 등)
    """

    def __init__(self, message: str, operation: Optional[str] = None):
        """
        Args:
            operation (str, optional): 실패한 처리 작업명
        """
        super().__init__(
            message=message,
            error_code="DATA_PROCESSING_FAILED",
            retryable=False,
            details={"operation": operation} if operation else {},
        )


class MediaNotFoundError(InstagramAPIError):
    """
    요청한 미디어를 찾을 수 없는 경우
    """

    def __init__(self, media_id: str):
        message = f"미디어를 찾을 수 없습니다: {media_id}"

        super().__init__(
            message=message,
            error_code="MEDIA_NOT_FOUND",
            status_code=404,
            retryable=False,
            details={"media_id": media_id},
        )


class PermissionError(InstagramAPIError):
    """
    권한 부족 에러 (특정 인사이트에 접근 권한이 없는 경우)
    """

    def __init__(self, resource: str):
        message = f"리소스에 대한 접근 권한이 없습니다: {resource}"

        super().__init__(
            message=message,
            error_code="PERMISSION_DENIED",
            status_code=403,
            retryable=False,
            details={"resource": resource},
        )


def handle_requests_exception(e: Exception, operation: str) -> InstagramAPIError:
    """
    requests 라이브러리의 예외를 Instagram 관련 예외로 변환합니다.

    Args:
        e (Exception): requests에서 발생한 예외
        operation (str): 실행 중이던 작업 설명

    Returns:
        InstagramAPIError: 변환된 Instagram 예외
    """
    if isinstance(e, requests.exceptions.ConnectionError):
        return NetworkError(f"네트워크 연결 실패: {operation}")

    elif isinstance(e, requests.exceptions.Timeout):
        return NetworkError(f"요청 시간 초과: {operation}")

    elif isinstance(e, requests.exceptions.HTTPError):
        status_code = e.response.status_code if e.response else None

        if status_code == 401:
            return AuthenticationError("API 인증 실패")
        elif status_code == 403:
            return PermissionError(operation)
        elif status_code == 404:
            return MediaNotFoundError("unknown")
        elif status_code == 429:
            return RateLimitError("API 호출 제한 초과")
        else:
            return InstagramAPIError(
                f"HTTP 에러 ({status_code}): {operation}",
                status_code=status_code,
                retryable=status_code is not None
                and status_code >= 500,  # 5xx 에러는 재시도 가능
            )

    else:
        return InstagramAPIError(
            f"알 수 없는 에러: {operation} - {str(e)}", retryable=True
        )


def is_retryable_error(error: Exception) -> bool:
    """
    주어진 에러가 재시도 가능한지 확인합니다.

    Args:
        error (Exception): 확인할 에러

    Returns:
        bool: 재시도 가능 여부
    """
    if isinstance(error, InstagramError):
        return error.retryable

    # Instagram 에러가 아닌 경우 기본적으로 재시도 불가능으로 처리
    return False


def get_retry_delay(error: Exception) -> Optional[int]:
    """
    에러에서 재시도 지연 시간을 추출합니다.

    Args:
        error (Exception): 에러 객체

    Returns:
        Optional[int]: 지연 시간(초), 없으면 None
    """
    if isinstance(error, RateLimitError) and error.retry_after:
        return error.retry_after

    return None
