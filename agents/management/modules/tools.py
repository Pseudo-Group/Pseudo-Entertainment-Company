"""
도구(Tools) 모듈

이 모듈은 Management Workflow에서 사용할 수 있는 다양한 도구를 정의합니다.
도구는 LLM이 프로젝트 관리, 리소스 할당, 팀 관리 등을 지원하는 함수들입니다.

아래는 엔터테인먼트 프로젝트 관리에 적합한 도구의 예시입니다:
- 프로젝트 일정 관리 도구: 일정 생성, 수정, 추적
- 팀 구성원 할당 도구: 팀원 정보 검색 및 역할 할당
- 리소스 검색 도구: 가용 리소스 출력 및 할당 상태 확인
- 참조 자료 검색 도구: 엔터테인먼트 산업의 프로젝트 관리 사례 검색
- 협업 지원 도구: 팀원간 커뮤니케이션 및 협업 지원
- 인스타그램 컨텐츠 검증 도구: Perplexity API를 통한 실시간 웹 검색 기반 컨텐츠 검증
"""

import json
import logging
import os
import asyncio
from typing import Any, Dict

import httpx
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")


async def _verify_instagram_content_async(
    content_text: str, content_type: str = "text"
) -> Dict[str, Any]:
    """
    Perplexity API를 사용하여 인스타그램 컨텐츠의 적절성을 실시간 웹 검색으로 검증합니다.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"인스타그램 컨텐츠 검증 시작: {content_type}")
    logger.info(f"컨텐츠 길이: {len(content_text)} 문자")

    if not content_text or not content_text.strip():
        return {
            "error": "컨텐츠 텍스트가 비어 있습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증할 컨텐츠가 없습니다."],
            "warnings": [],
            "suggestions": ["컨텐츠를 입력해주세요."],
            "risk_level": "high",
            "content_type": content_type,
            "tags": [],
        }

    if not PERPLEXITY_API_KEY:
        return {
            "error": "PERPLEXITY_API_KEY가 설정되지 않았습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["API 키가 없어 검증을 수행할 수 없습니다."],
            "warnings": [],
            "suggestions": ["PERPLEXITY_API_KEY를 설정해주세요."],
            "risk_level": "high",
            "content_type": content_type,
            "tags": [],
        }

    try:
        # Perplexity API를 통한 인스타그램 정책 검색 및 컨텐츠 검증
        prompt = f"""
다음 인스타그램 컨텐츠를 검증해주세요:

컨텐츠 유형: {content_type}
컨텐츠 텍스트: {content_text}

실시간 웹 검색을 통해 다음을 확인해주세요:
1. 인스타그램 커뮤니티 가이드라인 및 정책
2. 유사한 컨텐츠의 위반 사례
3. 현재 인스타그램에서 금지하는 키워드나 주제
4. 최근 인스타그램 정책 변경사항
5. 해당 컨텐츠의 잠재적 위험 요소

검색 키워드 예시:
- "Instagram community guidelines 2024"
- "Instagram content policy violations"
- "Instagram banned content examples"
- "Instagram content moderation rules"

다음 JSON 형태로 결과를 반환해주세요:
{{
    "is_approved": true/false,
    "score": 0.0-1.0,
    "reasons": ["승인/거부 이유들 (웹 검색 결과 기반)"],
    "warnings": ["경고사항들"],
    "suggestions": ["개선 제안사항들"],
    "risk_level": "low/medium/high",
    "policy_references": ["참조한 정책들"],
    "similar_cases": ["유사한 사례들"],
    "tags": ["관련 태그들"]
}}
"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
            )

            if response.status_code != 200:
                error_details = response.text
                logger.error(f"Perplexity API 오류: {response.status_code} - {error_details}")
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Perplexity API 응답 로깅
            logger.info(f"Perplexity API 응답 상태: {response.status_code}")
            logger.info(f"Perplexity API 원본 응답: {content}")
            
            # JSON 파싱
            try:
                parsed_result = json.loads(content)
                logger.info(f"Perplexity API 파싱된 결과: {json.dumps(parsed_result, ensure_ascii=False, indent=2)}")
                final_result = {
                    "is_approved": parsed_result.get("is_approved", False),
                    "score": float(parsed_result.get("score", 0.0)),
                    "reasons": parsed_result.get("reasons", []),
                    "warnings": parsed_result.get("warnings", []),
                    "suggestions": parsed_result.get("suggestions", []),
                    "risk_level": parsed_result.get("risk_level", "medium"),
                    "content_type": content_type,
                    "policy_references": parsed_result.get("policy_references", []),
                    "similar_cases": parsed_result.get("similar_cases", []),
                    "tags": parsed_result.get("tags", []),
                }
                
                logger.info(f"최종 검증 결과: {json.dumps(final_result, ensure_ascii=False, indent=2)}")
                return final_result
            except json.JSONDecodeError:
                return {
                    "error": "Perplexity API 응답 파싱 실패",
                    "is_approved": False,
                    "score": 0.0,
                    "reasons": ["Perplexity API 응답이 올바른 JSON이 아닙니다."],
                    "warnings": [],
                    "suggestions": ["다시 시도해주세요."],
                    "risk_level": "medium",
                    "content_type": content_type,
                    "tags": [],
                }

    except httpx.ReadTimeout:
        logger.error("Perplexity API 응답 시간 초과")
        return {
            "error": "Perplexity API 응답 시간 초과",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["Perplexity API에서 응답이 지연되어 검증을 완료할 수 없습니다."],
            "warnings": ["네트워크 상태나 Perplexity API의 부하 문제일 수 있습니다."],
            "suggestions": ["잠시 후 다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": content_type,
            "tags": [],
        }
    except Exception as e:
        logger.error(f"검증 중 예외 발생: {type(e).__name__} - {e!r}")
        return {
            "error": f"검증 중 오류 발생: {type(e).__name__}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": content_type,
            "tags": [],
        }


async def _verify_instagram_mixed_content_async(
    image_url: str, text_content: str, image_description: str = ""
) -> Dict[str, Any]:
    """
    Perplexity API를 사용하여 인스타그램 이미지와 텍스트를 함께 검증합니다.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"인스타그램 혼합 컨텐츠 검증 시작: 이미지={image_url}, 텍스트={text_content}")
    logger.info(f"이미지 설명: {image_description}")

    if not image_url or not image_url.strip():
        return {
            "error": "이미지 URL이 비어 있습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증할 이미지가 없습니다."],
            "warnings": [],
            "suggestions": ["이미지 URL을 입력해주세요."],
            "risk_level": "high",
            "content_type": "mixed",
            "tags": [],
        }

    if not text_content or not text_content.strip():
        return {
            "error": "텍스트 컨텐츠가 비어 있습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증할 텍스트가 없습니다."],
            "warnings": [],
            "suggestions": ["텍스트 컨텐츠를 입력해주세요."],
            "risk_level": "high",
            "content_type": "mixed",
            "tags": [],
        }

    if not PERPLEXITY_API_KEY:
        return {
            "error": "PERPLEXITY_API_KEY가 설정되지 않았습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["API 키가 없어 검증을 수행할 수 없습니다."],
            "warnings": [],
            "suggestions": ["PERPLEXITY_API_KEY를 설정해주세요."],
            "risk_level": "high",
            "content_type": "mixed",
            "tags": [],
        }

    try:
        # Perplexity API를 통한 인스타그램 혼합 컨텐츠 정책 검색 및 검증
        prompt = f"""
다음 인스타그램 포스트(이미지 + 텍스트)를 검증해주세요:

이미지 URL: {image_url}
텍스트 컨텐츠: {text_content}
이미지 설명: {image_description}

실시간 웹 검색을 통해 다음을 확인해주세요:
1. 인스타그램 커뮤니티 가이드라인 및 혼합 컨텐츠 정책
2. 이미지와 텍스트의 조합이 정책에 위반되는지 확인
3. 현재 인스타그램에서 금지하는 이미지-텍스트 조합 유형
4. 최근 인스타그램 혼합 컨텐츠 정책 변경사항
5. 해당 포스트의 잠재적 위험 요소 (이미지와 텍스트 각각 및 조합)

검색 키워드 예시:
- "Instagram mixed content policy violations 2024"
- "Instagram image text combination guidelines"
- "Instagram community guidelines mixed media"
- "Instagram post moderation rules 2024"

다음 JSON 형태로 결과를 반환해주세요:
{{
    "is_approved": true/false,
    "score": 0.0-1.0,
    "reasons": ["승인/거부 이유들 (웹 검색 결과 기반)"],
    "warnings": ["경고사항들"],
    "suggestions": ["개선 제안사항들"],
    "risk_level": "low/medium/high",
    "policy_references": ["참조한 정책들"],
    "similar_cases": ["유사한 사례들"],
    "image_analysis": ["이미지 관련 분석"],
    "text_analysis": ["텍스트 관련 분석"],
    "combination_analysis": ["이미지-텍스트 조합 분석"],
    "tags": ["관련 태그들"]
}}
"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
            )

            if response.status_code != 200:
                error_details = response.text
                logger.error(f"Perplexity API 오류: {response.status_code} - {error_details}")
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Perplexity API 응답 로깅
            logger.info(f"Perplexity API 응답 상태: {response.status_code}")
            logger.info(f"Perplexity API 원본 응답: {content}")
            
            # JSON 파싱
            try:
                parsed_result = json.loads(content)
                logger.info(f"Perplexity API 파싱된 결과: {json.dumps(parsed_result, ensure_ascii=False, indent=2)}")
                final_result = {
                    "is_approved": parsed_result.get("is_approved", False),
                    "score": float(parsed_result.get("score", 0.0)),
                    "reasons": parsed_result.get("reasons", []),
                    "warnings": parsed_result.get("warnings", []),
                    "suggestions": parsed_result.get("suggestions", []),
                    "risk_level": parsed_result.get("risk_level", "medium"),
                    "content_type": "mixed",
                    "policy_references": parsed_result.get("policy_references", []),
                    "similar_cases": parsed_result.get("similar_cases", []),
                    "image_analysis": parsed_result.get("image_analysis", []),
                    "text_analysis": parsed_result.get("text_analysis", []),
                    "combination_analysis": parsed_result.get("combination_analysis", []),
                    "tags": parsed_result.get("tags", []),
                    "image_url": image_url,
                    "text_content": text_content,
                    "image_description": image_description,
                }
                
                logger.info(f"최종 혼합 컨텐츠 검증 결과: {json.dumps(final_result, ensure_ascii=False, indent=2)}")
                return final_result
            except json.JSONDecodeError:
                return {
                    "error": "Perplexity API 응답 파싱 실패",
                    "is_approved": False,
                    "score": 0.0,
                    "reasons": ["Perplexity API 응답이 올바른 JSON이 아닙니다."],
                    "warnings": [],
                    "suggestions": ["다시 시도해주세요."],
                    "risk_level": "medium",
                    "content_type": "mixed",
                    "tags": [],
                }

    except httpx.ReadTimeout:
        logger.error("Perplexity API 응답 시간 초과")
        return {
            "error": "Perplexity API 응답 시간 초과",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["Perplexity API에서 응답이 지연되어 검증을 완료할 수 없습니다."],
            "warnings": ["네트워크 상태나 Perplexity API의 부하 문제일 수 있습니다."],
            "suggestions": ["잠시 후 다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": "mixed",
            "tags": [],
        }
    except Exception as e:
        logger.error(f"혼합 컨텐츠 검증 중 예외 발생: {type(e).__name__} - {e!r}")
        return {
            "error": f"혼합 컨텐츠 검증 중 오류 발생: {type(e).__name__}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["혼합 컨텐츠 검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": "mixed",
            "tags": [],
        }


async def _verify_instagram_image_async(
    image_url: str, image_description: str = ""
) -> Dict[str, Any]:
    """
    Perplexity API를 사용하여 인스타그램 이미지의 적절성을 실시간 웹 검색으로 검증합니다.
    """
    logger = logging.getLogger(__name__)
    logger.info(f"인스타그램 이미지 검증 시작: {image_url}")
    logger.info(f"이미지 설명: {image_description}")

    if not image_url or not image_url.strip():
        return {
            "error": "이미지 URL이 비어 있습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증할 이미지가 없습니다."],
            "warnings": [],
            "suggestions": ["이미지 URL을 입력해주세요."],
            "risk_level": "high",
            "content_type": "image",
            "tags": [],
        }

    if not PERPLEXITY_API_KEY:
        return {
            "error": "PERPLEXITY_API_KEY가 설정되지 않았습니다.",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["API 키가 없어 검증을 수행할 수 없습니다."],
            "warnings": [],
            "suggestions": ["PERPLEXITY_API_KEY를 설정해주세요."],
            "risk_level": "high",
            "content_type": "image",
            "tags": [],
        }

    try:
        # Perplexity API를 통한 인스타그램 이미지 정책 검색 및 검증
        prompt = f"""
다음 인스타그램 이미지를 검증해주세요:

이미지 URL: {image_url}
이미지 설명: {image_description}

실시간 웹 검색을 통해 다음을 확인해주세요:
1. 인스타그램 커뮤니티 가이드라인 및 이미지 정책
2. 유사한 이미지의 위반 사례
3. 현재 인스타그램에서 금지하는 이미지 유형
4. 최근 인스타그램 이미지 정책 변경사항
5. 해당 이미지의 잠재적 위험 요소

검색 키워드 예시:
- "Instagram image policy violations 2024"
- "Instagram banned image content examples"
- "Instagram community guidelines images"
- "Instagram image moderation rules"

다음 JSON 형태로 결과를 반환해주세요:
{{
    "is_approved": true/false,
    "score": 0.0-1.0,
    "reasons": ["승인/거부 이유들 (웹 검색 결과 기반)"],
    "warnings": ["경고사항들"],
    "suggestions": ["개선 제안사항들"],
    "risk_level": "low/medium/high",
    "policy_references": ["참조한 정책들"],
    "similar_cases": ["유사한 사례들"],
    "tags": ["관련 태그들"]
}}
"""

        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {"role": "user", "content": prompt},
                    ],
                },
            )

            if response.status_code != 200:
                error_details = response.text
                logger.error(f"Perplexity API 오류: {response.status_code} - {error_details}")
                raise Exception(f"Perplexity API 오류: {response.status_code}")

            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Perplexity API 응답 로깅
            logger.info(f"Perplexity API 응답 상태: {response.status_code}")
            logger.info(f"Perplexity API 원본 응답: {content}")
            
            # JSON 파싱
            try:
                parsed_result = json.loads(content)
                logger.info(f"Perplexity API 파싱된 결과: {json.dumps(parsed_result, ensure_ascii=False, indent=2)}")
                final_result = {
                    "is_approved": parsed_result.get("is_approved", False),
                    "score": float(parsed_result.get("score", 0.0)),
                    "reasons": parsed_result.get("reasons", []),
                    "warnings": parsed_result.get("warnings", []),
                    "suggestions": parsed_result.get("suggestions", []),
                    "risk_level": parsed_result.get("risk_level", "medium"),
                    "content_type": "image",
                    "policy_references": parsed_result.get("policy_references", []),
                    "similar_cases": parsed_result.get("similar_cases", []),
                    "tags": parsed_result.get("tags", []),
                    "image_url": image_url,
                    "image_description": image_description,
                }
                
                logger.info(f"최종 이미지 검증 결과: {json.dumps(final_result, ensure_ascii=False, indent=2)}")
                return final_result
            except json.JSONDecodeError:
                return {
                    "error": "Perplexity API 응답 파싱 실패",
                    "is_approved": False,
                    "score": 0.0,
                    "reasons": ["Perplexity API 응답이 올바른 JSON이 아닙니다."],
                    "warnings": [],
                    "suggestions": ["다시 시도해주세요."],
                    "risk_level": "medium",
                    "content_type": "image",
                    "tags": [],
                }

    except httpx.ReadTimeout:
        logger.error("Perplexity API 응답 시간 초과")
        return {
            "error": "Perplexity API 응답 시간 초과",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["Perplexity API에서 응답이 지연되어 검증을 완료할 수 없습니다."],
            "warnings": ["네트워크 상태나 Perplexity API의 부하 문제일 수 있습니다."],
            "suggestions": ["잠시 후 다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": "image",
            "tags": [],
        }
    except Exception as e:
        logger.error(f"이미지 검증 중 예외 발생: {type(e).__name__} - {e!r}")
        return {
            "error": f"이미지 검증 중 오류 발생: {type(e).__name__}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["이미지 검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": "image",
            "tags": [],
        }


def verify_instagram_content_tool(
    image_url: str = "", text_content: str = ""
) -> Dict[str, Any]:
    """
    인스타그램 컨텐츠 검증 도구
    
    Perplexity API를 사용하여 인스타그램 컨텐츠의 적절성을 실시간 웹 검색으로 검증합니다.
    - image_url만 있으면: 이미지 검증
    - text_content만 있으면: 텍스트 검증  
    - 둘 다 있으면: 혼합 컨텐츠 검증
    """
    logger = logging.getLogger(__name__)
    logger.info(f"[도구] verify_instagram_content_tool 호출 - image_url: {image_url}, text_content: {text_content}")
    
    try:
        # 혼합 컨텐츠인지 확인
        if image_url and text_content:
            # 혼합 컨텐츠 검증
            result = asyncio.run(_verify_instagram_mixed_content_async(image_url, text_content, ""))
            return result
        elif image_url:
            # 이미지 검증
            result = asyncio.run(_verify_instagram_image_async(image_url, ""))
            return result
        elif text_content:
            # 텍스트 검증
            result = asyncio.run(_verify_instagram_content_async(text_content, "text"))
            return result
        else:
            # 둘 다 없으면 오류
            return {
                "error": "검증할 컨텐츠가 없습니다.",
                "is_approved": False,
                "score": 0.0,
                "reasons": ["이미지 URL 또는 텍스트 컨텐츠를 입력해주세요."],
                "warnings": [],
                "suggestions": ["image_url 또는 text_content를 입력해주세요."],
                "risk_level": "high",
                "content_type": "none",
                "tags": []
            }
    except Exception as e:
        logger.error(f"[도구] 예외 발생: {e}")
        return {
            "error": f"인스타그램 컨텐츠 검증 중 오류 발생: {str(e)}",
            "is_approved": False,
            "score": 0.0,
            "reasons": ["검증 중 오류가 발생했습니다."],
            "warnings": [],
            "suggestions": ["다시 시도해주세요."],
            "risk_level": "medium",
            "content_type": "error",
            "tags": []
        }
