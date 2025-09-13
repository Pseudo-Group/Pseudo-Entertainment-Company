"""LangChain 체인을 설정하는 함수 모듈 (Gemini 기반, base_workflow 스타일)

LCEL을 사용해 입력에서 필요한 키만 프롬프트에 매핑하고,
Gemini LLM과 연결한 Runnable 체인을 반환합니다.
"""

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableSerializable

from agents.image.modules.models import get_gemini_llm, get_gemini_vlm


# Step 1 콘셉트 분해
def set_decomposition_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            title=lambda x: x["title"],
            context=lambda x: x["context"],
            style=lambda x: x["style"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 1.5 콘셉트 결정
def set_decision_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            album_cover_style=lambda x: x["album_cover_style"],
            concepts=lambda x: x["concepts"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 2 스토리보드
def set_storyboard_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            keyword=lambda x: x["keyword"],
            atmosphere=lambda x: x["atmosphere"],
            visual_metaphor=lambda x: x["visual_metaphor"],
            color_texture=lambda x: x["color_texture"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-A 레이아웃/구도
def set_layout_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
            includes_human=lambda x: x["includes_human"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-B 배경 디자인
def set_background_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
            includes_human=lambda x: x["includes_human"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-C 의상 컨셉
def set_style_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-D 헤어 스타일
def set_hair_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-E 표정/포즈
def set_pose_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 3-F 사진작가 설정
def set_photographer_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            main_theme=lambda x: x["main_theme"],
            story_summary=lambda x: x["story_summary"],
            mood_tags=lambda x: x["mood_tags"],
            dominant_colors=lambda x: x["dominant_colors"],
            texture_keywords=lambda x: x["texture_keywords"],
            visual_motifs=lambda x: x["visual_motifs"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# Step 4 통합 프롬프팅
def set_director_chain(prompt, model=get_gemini_llm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            photo_background=lambda x: x["photo_background"],
            photo_layout=lambda x: x["photo_layout"],
            model_style=lambda x: x["model_style"],
            model_pose=lambda x: x.get("model_pose", {}),
            model_hair=lambda x: x.get("model_hair", {}),
            photographer_settings=lambda x: x["photographer_settings"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )


# (선택) 이미지 생성 체인 예시 - 현재는 사용 안 함
def set_image_generation_chain(prompt, model=get_gemini_vlm) -> RunnableSerializable:
    llm = model()
    return (
        RunnablePassthrough.assign(
            integrated_prompt=lambda x: x["integrated_prompt"],
        )
        | prompt
        | llm
        | StrOutputParser()
    )
