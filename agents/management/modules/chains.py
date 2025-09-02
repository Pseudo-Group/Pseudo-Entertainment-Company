"""LangChain 체인을 설정하는 함수 모듈

LCEL(LangChain Expression Language)을 사용하여 체인을 구성합니다.
modules.prompts, modules.models, modules.tools를 활용하여 
인스타그램 컨텐츠 검증 체인을 생성합니다.

"""

from typing import Any, Dict
import json
import logging

from langchain.schema.runnable import RunnablePassthrough, RunnableSerializable
from langchain_core.output_parsers import StrOutputParser

from agents.management.modules.models import get_gemini_model
from agents.management.modules.prompts import get_content_verification_prompt

from agents.management.modules.tools import verify_instagram_content_tool

logger = logging.getLogger(__name__)





def create_result_analysis_chain():
    """
    검증 결과를 분석하고 요약하는 체인을 생성합니다.
    
    Returns:
        RunnableSerializable: 결과 분석 체인
    """
    prompt = get_content_verification_prompt()
    llm = get_gemini_model(temperature=0.3)
    
    chain = prompt | llm | StrOutputParser()
    
    def analyze_result(input_data: Dict[str, Any]) -> Dict[str, Any]:
        verification_result = input_data.get("verification_result", {})
        
        # 검증 결과를 문자열로 변환
        if isinstance(verification_result, dict):
            result_str = json.dumps(verification_result, ensure_ascii=False, indent=2)
        else:
            result_str = str(verification_result)
        
        # LLM으로 결과 분석
        analysis = chain.invoke({"verification_result": result_str})
        
        return {
            **input_data,
            "analysis": analysis
        }
    
    return analyze_result



def set_instagram_content_verification_chain(
    image_url: str = "", text_content: str = ""
) -> Dict[str, Any]:
    """
    인스타그램 컨텐츠 검증을 위한 체인을 생성합니다.

    Args:
        image_url: 검증할 이미지 URL
        text_content: 검증할 텍스트 컨텐츠

    Returns:
        Dict[str, Any]: 검증 결과
    """
    logger.info(f"[체인] set_instagram_content_verification_chain 호출 - image_url: {image_url}, text_content: {text_content}")
    
    # 1단계: 검증 도구 호출
    verification_result = verify_instagram_content_tool(image_url, text_content)
    
    # 2단계: 검증 결과 분석
    analysis_chain = create_result_analysis_chain()
    result = analysis_chain({
        "verification_result": verification_result,
        "image_url": image_url,
        "text_content": text_content
    })
    
    return {
        "verification_result": verification_result,
        "analysis": result.get("analysis", ""),
        "image_url": image_url,
        "text_content": text_content
    }


