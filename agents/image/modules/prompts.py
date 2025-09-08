"""프롬프트 템플릿을 생성하는 함수 모듈

프롬프트 템플릿을 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate을 사용하여 프롬프트 템플릿을 생성하고 반환합니다.
"""

from langchain_core.prompts import PromptTemplate
from agents.image.modules.state import ImageState


# Step 1 콘셉트 분해
def get_concept_decomposition(state: ImageState) -> str:
    """
    컨셉 분해를 실행하는 프롬프트
    """

    template = """
    ### Goal
    신곡의 앨범 커버를 기획하기 위해 다음 가사‧메시지‧노래 스타일을 대상으로 ‘콘셉트 분해’작업을 진행하라.

    ### 곡 제목
    {title}

    ### 가사
    {context}

    ### 곡 설명
    {style}

    ### 요구사항
    1. 키워드(가사과 스타일), 감정 및 분위기 매핑
    2. 감정별 시각적 메타포/오브젝트 제안(예: 네온사인, 골드 컨페티)
    3. 어울리는 색상과 질감 아이디어(HEX 코드 포함)

    ### 작성 규칙
    - 컨셉은 최소 6개 이상(핵심 키워드 다양화)
    - 키워드는 컨셉 당 하나씩
    - 메타포는 추상(예: “따뜻함”)이 아닌 구체 오브젝트로 표현  
    - 장황한 설명 없이 출력
    - 결과를 아래 예시와 같이 JSON List 형식으로 처리

    ### Few-shot example
    {{{{
      "keyword": ["자유"],
      "atmosphere": ["편안함, 해방감"],
      "visual_metaphor": ["깃털"],
      "color_texture": [{{"#E6E6FA, 쉬폰"}}]
    }}}},
    """

    return PromptTemplate(
        template=template,
        input_variables=["title", "context", "style"],
    )


# Step 1.5 콘셉트 결정
def get_concept_decision():
    """
    분해된 콘셉트를 선택하기 위한 프롬프트 템플릿을 생성합니다.
    """

    template = """# Role
    당신은 신곡의 앨범 커버를 기획하기 위해 구성된 컨셉들 중 제공되는 앨범 커버 스타일에 가장 적합한 것을 선택해야합니다.
    
    # 앨범 커버 스타일
    {album_cover_style}
    
    # 컨셉 후보 목록
    {concepts}

    아래 기준을 토대로 **컨셉 후보** 중 가장 적절한 컨셉을 **한 가지**만 선택하세요.

    - 앨범 커버 스타일과의 일치성
    - 컨셉의 독창성
    - 컨셉의 시각적 매력
    - 컨셉의 실행 가능성
    - 컨셉의 대중성
    - 컨셉의 트렌드 반영
    - 컨셉의 감정적 연결

    Output must be valid JSON object only.
    Do NOT include ``` or any Markdown formatting.
    Instead of including brief description of your decision, print the original concepts only.
    """
    return PromptTemplate(
        template=template,
        input_variables=["album_cover_style", "concepts"]
    )


# Step 2 스토리보드
def get_storyboard_prompt():
    """
    앨범 커버 제작을 위한 스토리보드 프롬프트 템플릿을 생성합니다.
    """
    
    template = """# Role
    당신은 뮤직 앨범 아트 디렉터입니다. 다음은 앨범 커버 제작을 위한 핵심 콘셉트입니다:

    # Concept
    ### 키워드
    {keyword}
    ### 분위기
    {atmosphere}
    ### 시각적 이미지
    {visual_metaphor}
    ### 색감
    {color_texture}

    이 정보를 바탕으로, **앨범 커버에 담길 장면**을 다음 조건에 맞춰 한 문단으로 서술하세요:
    1. 구체적인 시각적 이미지로 묘사된 장면일 것 (예: 시간대, 장소, 조명, 인물의 동작 등)
    2. 감정의 흐름이 느껴지도록 연출할 것 (예: 그리움에서 활기로 전환되는 느낌)
    3. '조화', '상징' 같은 추상적 단어보다는 시각적으로 떠올릴 수 있는 문장을 쓸 것
    4. 한국어로 작성할 것
    5. 제목처럼 한 줄로 전체 주제를 요약한 `main_theme`를 함께 생성할 것

    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    - main_theme: 전체를 관통하는 핵심 주제 (짧은 문장)
    - story_summary: 1문단 정도의 이야기적 흐름 (자연스러운 문장)
    - mood_tags: 대표 감정 또는 분위기 키워드 리스트
    - dominant_colors: 주요 색상 HEX 코드 리스트 (예: #FFA500)
    - texture_keywords: 시각적 질감 키워드 리스트 (예: 벨벳, 거친 표면 등)
    - visual_motifs: 공통된 시각적 오브젝트 또는 상징물 리스트
    - includes_human: 이미지에 인물이 등장하는지 여부 (true 또는 false)

    모든 출력은 한국어로 작성하고, 반드시 JSON 형식만 출력하세요.
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["keyword", "atmosphere", "visual_metaphor", "color_texture"],
    )


# Step 3-A 레이아웃/구도
def get_layout_prompt():
    """
    앨범커버의 배경 구도
    """
    template = """# Role
    당신은 뮤직 앨범 아트의 레이아웃과 구도를 담당하는 디렉터입니다. 다음은 앨범 아트의 스토리보드 입니다.

    # storyboard
    ### 메인 테마
    {main_theme}
    ### 스토리 요약
    {story_summary}
    ### 분위기
    {mood_tags}
    ### 대표색상
    {dominant_colors}
    ### 질감
    {texture_keywords}
    ### 시각 요소
    {visual_motifs}
    ### 인물 등장 여부
    {includes_human}
    
    
    이 스토리보드를 바탕으로, **앨범 커버의 담길 장면**을 아래 항목들에 맞게 작성해주세요.
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    - composition: 레프트 하이 앵글, 아이레벨 등 앨범 커버 촬영 시 카메라가 찍어야하는 구도
    - framing: 카메라 프레임 안에 포함할 객체들
    - shot_type: 클로즈업, 미디엄샷 등 앨범 커버 촬영 샷의 유형
    
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["main_theme", "story_summary", "mood_tags", "dominant_colors", "texture_keywords", "visual_motifs", "includes_human"]
    )


# Step 3-B 배경 디자인
def get_background_prompt():
    """
    앨범커버의 배경 디자인
    """
    template = """# Role
    당신은 뮤직 앨범 아트의 배경 디자인을 담당하는 디렉터입니다. 다음은 앨범 아트의 스토리보드 입니다.

    # storyboard
    ### 메인 테마
    {main_theme}
    ### 스토리 요약
    {story_summary}
    ### 분위기
    {mood_tags}
    ### 대표색상
    {dominant_colors}
    ### 질감
    {texture_keywords}
    ### 시각 요소
    {visual_motifs}
    ### 인물 등장 여부
    {includes_human}
    
    이 스토리보드를 바탕으로, **앨범 커버의 담길 장면**을 아래 항목들에 맞게 작성해주세요.
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    - backdrop: 앨범 커버 촬영 장소
    - scene: 앨범 커버의 상황
    - props: 앨범 커버에 등장할 소품
    - color_texture: 앨범 커버의 전체적인 색감
    
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["main_theme", "story_summary", "mood_tags", "dominant_colors", "texture_keywords", "visual_motifs", "includes_human"]
    )


# Step 3-C 의상 컨셉
def get_style_prompt():
    """
    앨범 커버 모델 의상
    """
    template = """# Role
    당신은 싱어송라이터의 스타일리스트입니다. 다음은 아티스트의 앨범 아트의 스토리보드입니다.

    # storyboard
    ### 메인 테마
    {main_theme}
    ### 스토리 요약
    {story_summary}
    ### 분위기
    {mood_tags}
    ### 대표색상
    {dominant_colors}
    ### 질감
    {texture_keywords}
    ### 시각 요소
    {visual_motifs}

    이 스토리보드를 바탕으로, **아티스트의 스타일**을 아래 **스타일요소**에 맞게 감독해주세요. 모든 스타일 요소는 색감, 재질 등 세부 사항을 포함해야 합니다.
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    ### 스타일 요소
    - fitting: 모델이 입을 의상의 핏(slim fit, regular fit, loose fit 등)
    - silhouette: 의상이 연출하는 전체적인 윤곽선(A-line, H-line, X-line 등)
    - top: 모델이 입을 상의
    - bottom: 모델이 입을 하의
    - layering: 모델이 top, bottom 위에 입을 옷가지(자켓, 셔츠, 조끼 등). 없을 경우 'None'
    - accessories: 모델이 착용할 악세서리(귀고리, 목걸이, 팔찌 등)
    - props: 모델이 들거나 착용할 소품(가방 등). 없을 경우 'None'
    - makeup: 모델의 세부적인 메이크업(피부, 색조, 눈, 립 등)
    - hair: 모델의 헤어스타일(머리 기장, 웨이브, 앞머리, 묶음 등)
    
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["main_theme", "story_summary", "mood_tags", "dominant_colors", "texture_keywords", "visual_motifs"]
    )


# Step 3-E 표정, 포징
def get_pose_prompt():
    """
    앨범 커버 모델의 표정과 포즈
    """
    template = """# Role
    당신은 아티스트 앨범 아트 촬영 디렉터입니다. 다음은 아티스트의 앨범 아트의 스토리보드입니다.

    # storyboard
    ### 메인 테마
    {main_theme}
    ### 스토리 요약
    {story_summary}
    ### 분위기
    {mood_tags}
    ### 대표색상
    {dominant_colors}
    ### 질감
    {texture_keywords}
    ### 시각 요소
    {visual_motifs}

    이 스토리보드를 바탕으로, **아티스트의 포즈**를 아래 항목에 맞게 감독해주세요.
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    - pose: 모델이 취할 포즈(standing, sitting, laying 등)
    - gesture: 모델이 취할 세부적인 몸짓(손동작, 고개 등)
    - gaze: 모델의 시선 방향 및 시선 표현
    
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["main_theme", "story_summary", "mood_tags", "dominant_colors", "texture_keywords", "visual_motifs"]
    )


# Step 3-F 사진작가
def get_photographer_prompt():
    """
    앨범 커버 촬영 감독의 카메라 및 현장 세팅
    """
    template = """# Role
    당신은 아티스트 앨범 아트 촬영 디렉터입니다. 다음은 아티스트의 앨범 아트의 스토리보드입니다.

    # storyboard
    ### 메인 테마
    {main_theme}
    ### 스토리 요약
    {story_summary}
    ### 분위기
    {mood_tags}
    ### 대표색상
    {dominant_colors}
    ### 질감
    {texture_keywords}
    ### 시각 요소
    {visual_motifs}

    이 스토리보드를 바탕으로, **아티스트의 포즈**를 아래 항목에 맞게 감독해주세요.
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다:

    - lighting: 촬영에 사용할 조명 설정(key light, back light, fill light 등)
    - lens: 촬영에 사용할 렌즈 설정(prime, wide, zoom 등)
    - tone: 앨범커버의 전체적인 톤(조도, 색감, 분위기 등)
    
    Output must be a valid JSON object only. Do NOT include ``` or any Markdown formatting.
    """

    return PromptTemplate(
        template=template,
        input_variables=["main_theme", "story_summary", "mood_tags", "dominant_colors", "texture_keywords", "visual_motifs"]
    )


def get_director_prompt():
    template = """# Role
    너는 Text to Image 모델 프롬프팅에 뛰어난 Prompt Engineer이다.
    아래 사항들을 종합하여, 아티스트의 앨범 커버 제작에 사용할 자연스럽고 완성된 문장 형태의 Prompt를 작성하라.
    
    # 요소
    ### 배경
    {photo_background}

    ### 촬영 구도
    {photo_layout}

    ### 모델 스타일링
    {model_style}

    ### 모델 포즈
    {model_pose}

    ### 촬영작가 세팅
    {photographer_settings}
    """

    return PromptTemplate(
        template=template,
        input_variables=["photo_background", "photo_layout", "model_style", "model_pose", "photographer_settings"]
    )





"""
Legacy
"""
def get_text_response_prompt(state: ImageState) -> str:
    """
    텍스트 응답 생성을 위한 프롬프트 템플릿을 반환합니다.
    """

    return """
    목적: {content_type}
    
    다음 텍스트에 대한 이미지를 생성하고 있습니다:
    {content_topic}
    
    이 텍스트의 시각적 요소와 감성을 분석하고, 어떤 이미지가 생성될 것인지 설명해주세요.
    다음 요소들을 포함해서 설명해주세요:
    1. 주요 시각적 요소
    2. 색감과 톤
    3. 분위기와 감성
    4. 구도와 강조점
    """

def get_image_generation_prompt()->PromptTemplate:
    """
    이미지 생성을 위한 프롬프트 템플릿을 생성합니다.

    프롬프트는 LLM에게 사용자 쿼리에 맞는 이미지 생성 방법과
    이미지 특성을 설명하도록 지시합니다. 생성된 이미지 설명은 한국어로 반환됩니다.
    
    Returns:
        PromptTemplate: 이미지 생성을 위한 프롬프트 템플릿 객체
    """
    # 이미지 생성을 위한 프롬프트 템플릿 정의
    image_generation_template = """당신은 상업용 이미지 배경 디자이너 입니다.
    제가 드리는 페르소나와 내용에 따라서 배경 이미지 설명을 생성해 주세요.
    이미지에는 텍스트, 인물이 절대 들어가서는 안됩니다.
    
    input: 
    이미지의 구성은 다음과 같습니다:
    이미지 유형 : {content_type}
    이미지 주제 : {content_topic}
    이미지 내용 : {context_detail}
    output: 
    이미지를 설명하는 요소는 다음과 같습니다. JSON 형식으로, 한국어로 뽑아주세요. 
    1. 배경 요소  
       - 배경의 전반적인 설명  
       -  배경 전반적인 색감 
       -  배경의 촬영 구도 
    2. 배경을 구성하는 요소들에 대한 설명 
        - 구성 요소  
        - 해당 구성 요소의 사진에서의 배치 
  
    """

    # PromptTemplate 객체 생성 및 반환
    return PromptTemplate(
        template=image_generation_template,  # 정의된 프롬프트 템플릿
        input_variables=["content_type", "persona", "content_topic","context_detail"],  # 프롬프트에 삽입될 변수들
    )


def get_context_prompt()->PromptTemplate:
    """
    input으로 받은 json 객체를 해석할 수 있도록 하는 프롬프트 템플릿을 생성합니다.

    프롬프트는 input으로 받은 객체를 자신만의 언어로 다시 해석하도록 하는 내용을 담고 있습니다. 
    생성된 내용은 한국어로 반환됩니다.
    
    Returns:
        PromptTemplate: 이미지 생성을 위한 프롬프트 템플릿 객체
    """
    
    context_generation_template = """
    당신은 상업용 사진 감독 입니다. 제가 드리는 컨셉 키워드 들을 가지고 페르소나를 반영해서 어떤 컨셉으로 사진을 촬영할지 지정해 주세요.
    제가 드리는 키워드는 이렇습니다 : {context}
    그리고 페르소나는 이렇습니다: {persona} 
    장르는 이렇습니다: {genre}
    페르소나를 반영할 때 음악에 관련된 부분은 반영하지 않습니다.
    이 정보를 바탕으로 사진에 담길 정보들을 다음 조건에 맞춰 한 문단으로 서술하세요:
    출력은 아래 JSON 형식을 따르며, 각 항목은 다음과 같은 의미를 가집니다. 
    - main_theme: 전체를 관통하는 핵심 주제 (짧은 문장)\n"
    "- story_summary: 1문단 정도의 이야기적 흐름 (자연스러운 문장)\n"
    "- mood_tags: 대표 감정 또는 분위기 키워드 리스트\n"
    "- dominant_colors: 주요 색상 HEX 코드 리스트 (예: #FFA500)\n"
    "- texture_keywords: 시각적 질감 키워드 리스트 (예: 벨벳, 거친 표면 등)\n"
    "- visual_motifs: 공통된 시각적 오브젝트 또는 상징물 리스트\n\n"
    "- includes_human: 이미지에 인물이 등장하는지 여부 (true 또는 false)"
    "모든 출력은 한국어로 작성하고, 반드시 JSON 형식만 출력하세요.\n
    """

    return PromptTemplate(
        template = context_generation_template,
        input_variables = ["context", "persona"]
    )
