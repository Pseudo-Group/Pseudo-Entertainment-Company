"""모델 설정 함수 모듈

기본적으로 사용할 모델 인스턴스를 설정하고 생성하고 반환시킵니다.
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()


def get_gemini_llm(temperature=0.5):
    """
    LangChain에서 사용할 Gemini 모델을 초기화하여 번환합니다.
    환경변수에서 GOOGLE_API_KEY를 가져와 사용하기 때문에, .env 파일에 유효한 API 키가 설정되어 있어야 합니다.

    Args:
        temperature: 모델의 창의성 정도를 조절하는 파라미터 (기본값:0.5)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key
    )

def get_gemini_vlm(temperature=0.5):
    """
    LangChain에서 사용할 Gemini 모델을 초기화하여 번환합니다.
    환경변수에서 GOOGLE_API_KEY를 가져와 사용하기 때문에, .env 파일에 유효한 API 키가 설정되어 있어야 합니다.

    Args:
        temperature: 모델의 창의성 정도를 조절하는 파라미터 (기본값:0.5)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables. Please set it in .env file.")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-image-preview",
        google_api_key=api_key
    )