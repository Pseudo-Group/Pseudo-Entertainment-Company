import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logging.getLogger().setLevel(logging.INFO)
from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.management.modules.nodes import InstagramContentVerificationNode
from agents.management.modules.state import ManagementState



class ManagementWorkflow(BaseWorkflow):
    """
    인스타그램 컨텐츠 검증을 위한 Workflow 클래스

    이 클래스는 인스타그램 컨텐츠 검증만을 수행하는 단순한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    Perplexity API를 통한 실시간 웹 검색 기반 인스타그램 컨텐츠 검증 기능을 포함합니다.
   // 텍스트만 검증
   {"text_content": "오늘 날씨가 정말 좋네요!"}
   
   // 이미지만 검증  
   {"image_url": "https://example.com/image.jpg"}
   
   // 혼합 컨텐츠 검증
   {
     "image_url": "https://example.com/image.jpg",
     "text_content": "오늘 날씨가 정말 좋네요!"
   }
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        관리 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 콘텐츠 관리를 위한 Workflow 그래프를 구축합니다.
        인스타그램 컨텐츠 검증만 수행하는 단순한 구조입니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        
        def entry_point_inspector(state):
            """
            그래프의 실제 진입점에서 state를 검사하기 위한 디버깅 함수.
            """
            print(f"--- DEBUG: ENTRY POINT STATE ---")
            print(f"State type: {type(state)}")
            print(f"State keys: {state.keys() if hasattr(state, 'keys') else 'No keys'}")
            print(f"State content: {state}")
            print(f"---------------------------------")
            
            # LangGraph Studio에서 입력이 'input' 키로 전달되는 경우를 처리
            if isinstance(state, dict) and 'input' in state:
                # input 키의 내용을 최상위로 복사
                input_data = state['input']
                if isinstance(input_data, dict):
                    state.update(input_data)
                    print(f"Updated state with input data: {state}")
            
            # content_text가 있으면 user_input으로도 설정
            if isinstance(state, dict) and 'content_text' in state:
                state['user_input'] = state['content_text']
                print(f"Set user_input from content_text: {state}")
            
            return state

        builder = StateGraph(self.state)

        # InstagramContentVerificationNode 인스턴스 생성 및 메서드 바인딩
        instagram_node = InstagramContentVerificationNode()
        builder.add_node("instagram_content_verification", instagram_node.execute)
        
        # 진입점 및 라우팅 설정 - 바로 검증 노드로 이동
        builder.set_entry_point("instagram_content_verification")
        builder.add_edge("instagram_content_verification", "__end__")
        
        workflow = builder.compile()
        workflow.name = self.name
        return workflow


# 관리 Workflow 인스턴스 생성
management_workflow = ManagementWorkflow(ManagementState)
