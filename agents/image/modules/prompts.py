"""프롬프트 템플릿 팩토리 모듈

nodes.py에서 사용하는 각 단계별 Prompt를 반환합니다.
대부분의 노드는 JSON 문자열 출력을 기대하므로, 명시적으로 JSON만 출력하도록 지시합니다.
"""

from langchain_core.prompts import ChatPromptTemplate, PromptTemplate


# 1) Concept Decomposition
def get_concept_decomposition(_state_type=None) -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        당신은 음악 콘셉 분석가입니다. 아래 곡 정보를 분석하여 3~5개의 시각적 콘셉트를 도출하세요.
        - title: {title}
        - context: |{context}|
        - style: |{style}|

        각 콘셉트는 다음 항목을 포함해야 합니다:
        - keyword: 핵심 키워드 (짧은 명사/구)
        - atmosphere: 분위기/감정 묘사 (짧은 문장)
        - visual_metaphor: 시각적 은유/상징 (리스트 가능)
        - color_texture: 색상/질감 키워드 (리스트)

        반드시 JSON 배열만 출력하세요. 마크다운 없이.
        """
    )


# 1.5) Concept Decision
def get_concept_decision() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        당신은 아트 디렉터입니다. 아래 후보 콘셉트들 중 앨범커버 스타일에 가장 부합하는 하나를 선택해 주세요.
        - album_cover_style: {album_cover_style}
        - concepts: {concepts}

        선택된 하나의 콘셉트를 JSON 객체로만 출력하세요.
        """
    )


# 2) Storyboard
def get_storyboard_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        다음 최종 콘셉트를 기반으로 앨범커버 스토리보드 요소를 생성하세요.
        - keyword: {keyword}
        - atmosphere: {atmosphere}
        - visual_metaphor: {visual_metaphor}
        - color_texture: {color_texture}

        아래 JSON 객체만 출력하세요:
        {{
          "main_theme": "핵심 주제 한 줄",
          "story_summary": "자연스러운 문장 1문단",
          "mood_tags": ["활기", "그리움"],
          "dominant_colors": ["#FFA500", "#2B2B2B"],
          "texture_keywords": ["벨벳", "거친 표면"],
          "visual_motifs": ["네온사인", "달"],
          "includes_human": true
        }}
        마크다운 금지, JSON만 출력.
        """
    )


# 3-A) Layout
def get_layout_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        다음 스토리보드를 바탕으로 사진의 레이아웃/구도 계획을 JSON으로 작성하세요.
        - main_theme: {main_theme}
        - story_summary: {story_summary}
        - mood_tags: {mood_tags}
        - dominant_colors: {dominant_colors}
        - texture_keywords: {texture_keywords}
        - visual_motifs: {visual_motifs}
        - includes_human: {includes_human}

        아래 예시 형태의 JSON만 출력하세요:
        {{
          "framing": "medium shot, centered subject",
          "composition_rules": ["rule of thirds", "leading lines"],
          "camera_angle": "eye-level",
          "negative_space": "balanced"
        }}
        """
    )


# 3-B) Background
def get_background_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        스토리보드를 바탕으로 배경 요소를 JSON으로 설계하세요. 입력은 레이아웃과 동일합니다.

        {{
          "environment": "city rooftop at dusk",
          "lighting": "warm neon rim light",
          "props": ["billboard", "stairwell"],
          "color_palette": ["#FF7F50", "#1E90FF"]
        }}
        만 출력.
        """
    )


# 3-C) Style (Outfit)
def get_style_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        스토리보드를 바탕으로 인물의 의상/스타일을 JSON으로만 작성하세요.
        - main_theme: {main_theme}
        - story_summary: {story_summary}
        - mood_tags: {mood_tags}
        - dominant_colors: {dominant_colors}
        - texture_keywords: {texture_keywords}
        - visual_motifs: {visual_motifs}

        {{
          "clothing_items": ["leather jacket", "graphic tee"],
          "accessories": ["silver chain", "ring"],
          "color_palette": ["#000000", "#C0C0C0"],
          "textures": ["leather", "cotton"],
          "style_summary": "modern streetwear with metallic accents"
        }}
        만 출력하고, 변수명 그대로 JSON으로.
        """
    )


# 3-D) Hair
def get_hair_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        스토리보드를 바탕으로 인물의 헤어스타일을 JSON으로만 작성하세요.
        - main_theme: {main_theme}
        - story_summary: {story_summary}
        - mood_tags: {mood_tags}
        - dominant_colors: {dominant_colors}
        - texture_keywords: {texture_keywords}
        - visual_motifs: {visual_motifs}

        {{
          "hair_type": "wavy",
          "hair_length": "shoulder length",
          "hair_color": "deep brown",
          "hair_style": "soft layered",
          "accessories": ["hairpin"]
        }}
        만 출력.
        """
    )


# 3-E) Pose
def get_pose_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        스토리보드를 바탕으로 인물의 표정/포즈를 JSON으로만 작성하세요.
        - main_theme: {main_theme}
        - story_summary: {story_summary}
        - mood_tags: {mood_tags}
        - dominant_colors: {dominant_colors}
        - texture_keywords: {texture_keywords}
        - visual_motifs: {visual_motifs}

        {{
          "facial_expression": "confident smirk",
          "gaze": "towards camera",
          "hand_gestures": "one hand in pocket, other holding mic",
          "body_posture": "relaxed shoulders, slight lean",
          "movement": "subtle sway"
        }}
        만 출력.
        """
    )


# 3-F) Photographer settings
def get_photographer_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        촬영 세팅을 JSON으로만 제안하세요. 스토리보드와 레이아웃을 고려합니다.
        - main_theme: {main_theme}
        - story_summary: {story_summary}
        - mood_tags: {mood_tags}
        - dominant_colors: {dominant_colors}
        - texture_keywords: {texture_keywords}
        - visual_motifs: {visual_motifs}

        {{
          "camera": "Sony A7R IV",
          "lens": "50mm",
          "focal_length": "50mm",
          "aperture": "f/2.0",
          "iso": 200,
          "shutter_speed": "1/125",
          "lighting_setup": ["key light left", "rim light back-right"]
        }}
        만 출력.
        """
    )


# 4) Director integration (include hair)
def get_director_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_template(
        """
        통합 프롬프트를 영어 한 문단으로 작성하세요. 아래 요소를 모두 자연스럽게 반영합니다.
        - background: {photo_background}
        - layout: {photo_layout}
        - outfit/style: {model_style}
        - hair: {model_hair}
        - pose: {model_pose}
        - photographer settings: {photographer_settings}

        지시사항:
        - 배경/구도/피사체/의상/헤어/표정과 포즈/조명/카메라 설정 요소를 자연스럽게 통합
        - 브랜드명/인물명은 피하고, 묘사 중심
        - 불필요한 접두/접미 문구 금지, 최종 1문단 텍스트만 출력
        """
    )


# (선택) 기존 템플릿도 유지하여 재사용 가능
outfit_prompt_template = PromptTemplate.from_template(
    "You are a fashion styling expert. The user's request is: '{user_request}'.\n"
    "Please describe an outfit suitable for the season, location, and mood in detail.\n"
    "At the end of your response, include a section titled 'Image Generation Prompt:' and write one paragraph in English that describes only the clothing and accessories.\n"
    "Do not include background, facial expression, pose, or any scene-related details.\n"
    "Focus only on the fashion items — their style, color, texture, and how they are combined."
)

pose_prompt_template = PromptTemplate.from_template(
    "You are an expert in character expression and pose design.\n"
    "The following concept should be visually interpreted: '{user_request}'\n\n"
    "Your task is to write one concise, vivid English sentence that describes only the person's pose and facial expression.\n"
    "- Include facial emotion, gaze direction, hand gestures, body posture, and movement.\n"
    "- Do not mention clothing, background, or scene elements.\n"
    "- The sentence should be suitable for an image generation model.\n"
    "- Avoid generic expressions and ensure physical cues are clearly described."
)

storyboard_prompt_template = PromptTemplate.from_template(
    "당신은 뮤직 앨범 아트 디렉터입니다. 다음은 앨범 커버 제작을 위한 핵심 콘셉트입니다:\n\n"
    "{concepts}\n\n"
    "이 정보를 바탕으로, **앨범 커버에 담길 장면**을 다음 조건에 맞춰 한 문단으로 서술하세요:\n"
    "1. 구체적인 시각적 이미지로 묘사된 장면일 것 (예: 시간대, 장소, 조명, 인물의 동작 등)\n"
    "2. 감정의 흐름이 느껴지도록 연출할 것 (예: 그리움에서 활기로 전환되는 느낌)\n"
    "3. '조화', '상징' 같은 추상적 단어보다는 시각적으로 떠올릴 수 있는 문장을 쓸 것\n"
    "4. 한국어로 작성할 것\n"
    "5. 제목처럼 한 줄로 전체 주제를 요약한 `main_theme`를 함께 생성할 것\n"
    "출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:\n\n"
    "- main_theme: 전체를 관통하는 핵심 주제 (짧은 문장)\n"
    "- story_summary: 1문단 정도의 이야기적 흐름 (자연스러운 문장)\n"
    "- mood_tags: 대표 감정 또는 분위기 키워드 리스트\n"
    "- dominant_colors: 주요 색상 HEX 코드 리스트 (예: #FFA500)\n"
    "- texture_keywords: 시각적 질감 키워드 리스트 (예: 벨벳, 거친 표면 등)\n"
    "- visual_motifs: 공통된 시각적 오브젝트 또는 상징물 리스트\n\n"
    "- includes_human: 이미지에 인물이 등장하는지 여부 (true 또는 false)"
    "모든 출력은 한국어로 작성하고, 반드시 JSON 형식만 출력하세요.\n"
    "Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting."
)
