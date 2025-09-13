import json
from typing import Dict, List, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from prompt import prompt
import base64

from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

from agents.text.modules.persona import PERSONA
from agents.image.modules.state import ImageState

from agents.image.modules.nodes import ImageGenerationNode, getStoryBoardNode
from agents.text.modules.nodes import PersonaExtractionNode

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

template = ChatPromptTemplate.from_template(prompt)

def get_input() -> list:

    with open('./data.json', 'r', encoding = 'utf-8') as f:
        json_data = json.load(f)
    
    data = json_data

    return data 

def storyboard_node(state:dict) -> dict:
    story_node = getStoryBoardNode(name = "input_node")
    interpreted_text = story_node.execute(state)

    return {"content_topic": "앨범 커버", 
        "content_type": "앨범 제작",
        "context":state['context'],
        "context_describe": interpreted_text['response'] ,
        "persona": state['persona']}

def persona_extraction_node(state: dict) -> dict:
    persona_node = PersonaExtractionNode(name="persona_extraction")
    extracted_persona = persona_node.execute(state)
    
    return {
        "content_topic": state["content_topic"],
        "content_type": state["content_type"],
        "context": state['context'],
        "genre":state['genre'],
        "persona":extracted_persona
    }



def image_generation_node(state: dict) -> dict:
    image_node = ImageGenerationNode(name="image_generation")
    result = image_node.execute(state)
    return result

def build_graph():
    builder = StateGraph(dict)  # ImageState 대신 dict 사용
    builder.add_node("PersonaExtraction", RunnableLambda(persona_extraction_node))
    builder.add_node("StoryBoardExtraction", RunnableLambda(storyboard_node))
    builder.add_node("ImageGeneration", RunnableLambda(image_generation_node))
    
    
    builder.set_entry_point("PersonaExtraction")
    builder.add_edge("PersonaExtraction", "StoryBoardExtraction")
    builder.add_edge("StoryBoardExtraction", "ImageGeneration")
    builder.add_edge("ImageGeneration", END)  # set_finish_point 대신 END 사용

    return builder.compile()

if __name__ == "__main__":
    graph = build_graph()
    inputData = get_input()
    initial_state = {
        "content_topic": "앨범 커버", 
        "content_type": "앨범 제작",
        "genre": "힙합", 
        "context": inputData ,
        "persona": PERSONA
    }
    result = graph.invoke(initial_state)
    print(result)



