"""
이미지 Workflow의 상태를 정의하는 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow에서 사용되는 상태 정보를 정의합니다.
LangGraph의 상태 관리를 위한 클래스를 포함합니다.
"""

from __future__ import annotations

from typing import TypedDict, Dict, List, Any, Optional
from PIL import ImageFile
from pathlib import Path
from langgraph.graph.message import add_messages


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
    album_cover_style: str

class StoryboardDict(TypedDict):
    main_theme: str
    story_summary: str
    mood_tags: List[str]
    dominant_colors: List[str]
    texture_keywords: List[str]
    visual_motifs: List[str]
    includes_human: bool

class LayoutDict(TypedDict):
    composition: str
    framing: str
    shot_type: str

class BackgroundDict(TypedDict):
    backdrop: str
    scene: str
    props: str
    color_texture: str

class ModelStyleDict(TypedDict):
    fitting: str
    silhouette: str
    top: str
    bottom: str
    layering: str
    accessories: str
    props: str
    makeup: str
    hair: str

class ModelPoseDict(TypedDict):
    pose: str
    gesture: str
    gaze: str

class PhotographerDict(TypedDict):
    lighting: str
    lens: str
    tone: str


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

    # Photographer Settings
    photographer_settings: PhotographerDict
    
    # ImageState 필드들
    content_topic: str
    content_type: str
    context_detail: str
    genre: str
    persona: str
    
    # Integrated Prompt
    integrated_prompt: str

    # Generated Image
    generated_image: str
