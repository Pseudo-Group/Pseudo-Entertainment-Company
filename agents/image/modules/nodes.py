"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

import os
import base64
import uuid
from datetime import datetime
import json_repair
from typing import Dict, Any
from langchain_core.runnables import RunnableSerializable
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from google import genai
from google.genai import types
from PIL import Image
from io import BytesIO

from agents.text.modules.persona import PERSONA
from agents.base_node import BaseNode
from agents.image.modules.state import ImageState
import agents.image.modules.chains as chains
import agents.image.modules.prompts as prompts

from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")


# Step 1 콘셉트 분해
class ConceptDecompositionNode(BaseNode):
    """
    Music Agent의 곡 정보를 토대로 컨셉을 분해/도출하는 노드
    
    Args:
        information -> Dict
        (곡의 title, context, style 정보) 

    Returns:
        concepts -> Dict List
        (keyword, atmosphere, visual_metaphor,color_texture로 이루어진 컨셉들)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_concept_decomposition(ImageState)
        self.chain = chains.set_decomposition_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                # "music_context": state["music_context"],
                "title": state["information"]["title"],
                "context": state["information"]["context"],
                "style": state["information"]["style"],
                # "information": state["information"]
            }
        )
        result = json_repair.loads(response)
        return {"concepts": result}
    

# Step 1.5 콘셉트 결정
class ConceptDecisionNode(BaseNode):
    """
    분해된 컨셉들 중 적절한 컨셉을 선별하는 노드

    Args:
        concepts -> Dict list
        (keyword, atmosphere, visual_metaphor,color_texture로 이루어진 컨셉들)
        albumcover_style -> str
        (앨범커버 스타일을 설명하는 짧은 문자열)
    
    Returns:
        final_concept -> Dict
        (컨셉들 중 최종으로 결정된 하나의 컨셉)

    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_concept_decision()
        self.chain = chains.set_decision_chain(self.prompt)
        
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "album_cover_style": state["album_cover_style"],
                "concepts": state["concepts"],
                # "keyword": state["keyword"],
                # "atmosphere": state["atmosphere"],
                # "visual_metaphor": state["visual_metaphor"],
                # "color_texture": state["color_texture"]
            }
        )
        result = json_repair.loads(response)
        return {"final_concept": result}


# Step 2 스토리보드
class CreateStoryboardNode(BaseNode):
    """
    선별된 컨셉들을 토대로 스토리보드를 제작하는 노드
    Args:
        final_concept -> Dict

    Returns:
        storyboard -> Dict
        (앨범커버 컨셉과 자세한 요소를 담은 딕셔너리)
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_storyboard_prompt()
        self.chain = chains.set_storyboard_chain(self.prompt)

    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                # "concepts": state["concepts"],
                "keyword": state["final_concept"]["keyword"],
                "atmosphere": state["final_concept"]["atmosphere"],
                "visual_metaphor": state["final_concept"]["visual_metaphor"],
                "color_texture": state["final_concept"]["color_texture"]
            }
        )
        result = json_repair.loads(response)
        return {"storyboard": result}


# Step 3-A 레이아웃/구도
class LayoutNode(BaseNode):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_layout_prompt()
        self.chain = chains.set_layout_chain(self.prompt)

    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "main_theme": state["storyboard"]["main_theme"],
                "story_summary": state["storyboard"]["story_summary"],
                "mood_tags": state["storyboard"]["mood_tags"],
                "dominant_colors": state["storyboard"]["dominant_colors"],
                "texture_keywords": state["storyboard"]["texture_keywords"],
                "visual_motifs": state["storyboard"]["visual_motifs"],
                "includes_human": state["storyboard"]["includes_human"]
            }
        )
        result = json_repair.loads(response)
        return {"photo_layout": result}


# Step 3-B 배경 디자인
class BackgroundNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_background_prompt()
        self.chain = chains.set_background_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "main_theme": state["storyboard"]["main_theme"],
                "story_summary": state["storyboard"]["story_summary"],
                "mood_tags": state["storyboard"]["mood_tags"],
                "dominant_colors": state["storyboard"]["dominant_colors"],
                "texture_keywords": state["storyboard"]["texture_keywords"],
                "visual_motifs": state["storyboard"]["visual_motifs"],
                "includes_human": state["storyboard"]["includes_human"]
            }
        )
        result = json_repair.loads(response)
        return {"photo_background": result}


# Step 3-C 의상 컨셉
class StyleNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_style_prompt()
        self.chain = chains.set_style_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "main_theme": state["storyboard"]["main_theme"],
                "story_summary": state["storyboard"]["story_summary"],
                "mood_tags": state["storyboard"]["mood_tags"],
                "dominant_colors": state["storyboard"]["dominant_colors"],
                "texture_keywords": state["storyboard"]["texture_keywords"],
                "visual_motifs": state["storyboard"]["visual_motifs"],
            }
        )
        result = json_repair.loads(response)
        return {"model_style": result}


# Step 3-E 표정, 포징
class PoseNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_pose_prompt()
        self.chain = chains.set_pose_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "main_theme": state["storyboard"]["main_theme"],
                "story_summary": state["storyboard"]["story_summary"],
                "mood_tags": state["storyboard"]["mood_tags"],
                "dominant_colors": state["storyboard"]["dominant_colors"],
                "texture_keywords": state["storyboard"]["texture_keywords"],
                "visual_motifs": state["storyboard"]["visual_motifs"],
            }
        )
        result = json_repair.loads(response)
        return {"model_pose": result}


# Step 3-F 사진작가
class PhotographerNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_photographer_prompt()
        self.chain = chains.set_photographer_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "main_theme": state["storyboard"]["main_theme"],
                "story_summary": state["storyboard"]["story_summary"],
                "mood_tags": state["storyboard"]["mood_tags"],
                "dominant_colors": state["storyboard"]["dominant_colors"],
                "texture_keywords": state["storyboard"]["texture_keywords"],
                "visual_motifs": state["storyboard"]["visual_motifs"],
            }
        )
        result = json_repair.loads(response)
        return {"photographer_settings": result}


# Step 4 통합 프롬프팅
class DirectorNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.prompt = prompts.get_director_prompt()
        self.chain = chains.set_director_chain(self.prompt)
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain
        response = prompt_chain.invoke(
            {
                "photo_background": state["photo_background"],
                "photo_layout": state["photo_layout"],
                "model_style": state["model_style"],
                "model_pose": state["model_pose"],
                "photographer_settings": state["photographer_settings"]
            }
        )
        return {"integrated_prompt": response}


# Step 5 이미지 생성
class ImageGenerationNode(BaseNode):
    def __init__(self, **kwargs):
        super().__init__(**kwargs) 
        self.client = genai.Client()
        self.output_folder = "./generated_images"

    def _generate_unique_filename(self, extension="png"):
        """고유한 파일명 생성"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"generated_{timestamp}_{unique_id}.{extension}"

    def execute(self, state: ImageState) -> dict:       
        response = self.client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=state['integrated_prompt'],
        )
        
        # 폴더가 없으면 생성
        os.makedirs(self.output_folder, exist_ok=True)
        generated_image_path = None
        
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(part.text)
            elif part.inline_data is not None:
                image = Image.open(BytesIO(part.inline_data.data))
                
                # 고유한 파일명 생성
                filename = self._generate_unique_filename()
                generated_image_path = os.path.join(self.output_folder, filename)
                
                # 이미지 저장
                image.save(generated_image_path)
                print(f"이미지가 저장되었습니다: {generated_image_path}")
                break
                
            return {"generated_image_path": generated_image_path}


    


"""
Legacy
"""
class getStoryBoardNode(BaseNode):
    """
    다른 노드로부터 온 input을 받아서, 해석하는 노드 
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
        self.chain = set_context_chain()
        self.prompt = get_context_prompt()
    
    def execute(self, state: ImageState) -> dict:
        prompt_chain = self.chain

        response = prompt_chain.invoke(
            {
                "content_topic": state['content_topic'], 
                "content_type": state['content_type'],
                "context": state['context'] , 
                "genre" : state['genre'],
                "persona": PERSONA  
            }
        , generation_config = dict(response_modalities = ["TEXT"]))

        return {'response':response}



