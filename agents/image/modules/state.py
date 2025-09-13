"""
이미지 Workflow의 상태를 정의하는 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
base_workflow 스타일의 정적 TypedDict 구조를 따르며, 병렬 합류를 위한 보조 필드(머리 스타일, 머지 카운터)를 추가로 포함합니다.
"""

from __future__ import annotations

from typing import TypedDict, Dict, List, Any, Optional


"""
각 노드에서 사용하는 딕셔너리 자료형
"""


class SongInfoDict(TypedDict):
    title: str
    context: str
    style: str


class ConceptDict(TypedDict):
    keyword: List[str]
    atmosphere: List[str]
    visual_metaphor: List[str]
    color_texture: List[Dict[str, str]]
    album_cover_style: Optional[str]


class StoryboardDict(TypedDict):
    main_theme: str
    story_summary: str
    mood_tags: List[str]
    dominant_colors: List[str]
    texture_keywords: List[str]
    visual_motifs: List[str]
    includes_human: bool


class LayoutDict(TypedDict):
    framing: str
    composition_rules: List[str]
    camera_angle: str
    negative_space: str


class BackgroundDict(TypedDict):
    environment: str
    lighting: str
    props: List[str]
    color_palette: List[str]


class ModelStyleDict(TypedDict):
    clothing_items: List[str]
    accessories: List[str]
    color_palette: List[str]
    textures: List[str]
    style_summary: str


class ModelPoseDict(TypedDict):
    facial_expression: str
    gaze: str
    hand_gestures: str
    body_posture: str
    movement: str


class ModelHairDict(TypedDict):
    hair_type: str
    hair_length: str
    hair_color: str
    hair_style: str
    accessories: List[str]


class PhotographerDict(TypedDict):
    camera: str
    lens: str
    focal_length: str
    aperture: str
    iso: int
    shutter_speed: str
    lighting_setup: List[str]


"""
Agent State
"""


class ImageState(TypedDict):
    # MusicState 필드들
    information: SongInfoDict

    # Concept Decision
    album_cover_style: str
    concepts: List[ConceptDict]
    final_concept: ConceptDict

    # Storyboard
    storyboard: StoryboardDict

    # Layout & Background
    photo_layout: LayoutDict
    photo_background: BackgroundDict

    # Model Settings
    model_style: ModelStyleDict
    model_pose: ModelPoseDict
    # 추가: 헤어 세팅(병렬 분기용)
    model_hair: ModelHairDict

    # Photographer Settings
    photographer_settings: PhotographerDict

    # ImageState 기타 필드들 (레거시 호환 및 설명용)
    content_topic: Optional[str]
    content_type: Optional[str]
    context_detail: Optional[str]
    genre: Optional[str]
    persona: Optional[str]

    # Integrated Prompt
    integrated_prompt: str

    # Generated Image
    generated_image: Optional[str]

    # 병렬 합류를 위한 카운터
    merge_ready_count: int
