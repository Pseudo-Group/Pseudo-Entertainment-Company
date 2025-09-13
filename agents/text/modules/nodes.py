"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.
"""

from agents.base_node import BaseNode
from agents.text.modules.chains import set_extraction_chain
from agents.text.modules.persona import PERSONA
from agents.text.modules.state import TextState


class PersonaExtractionNode(BaseNode):
    """
    콘텐츠 종류에 적합한 페르소나를 추출하는 노드
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)  # BaseNode 초기화
        # 체인은 실행 시점에 생성하여 테스트 시 환경 변수 의존성을 피합니다.
        self.chain = None  # type: ignore

    def execute(self, state: TextState) -> dict:
        """
        주어진 상태(state)에서 핵심 키워드와 페르소나를 추출하여, 이미지 생성 노드에 전달합니다.
        """
        # 체인을 지연 생성하여 OPENAI_API_KEY 없이도 인스턴스화 가능하도록 처리
        if self.chain is None:
            self.chain = set_extraction_chain()

        # 페르소나 추출 체인 실행
        extracted_persona = self.chain.invoke(
            {
                "content_topic": state["content_topic"],  # 콘텐츠 주제
                "content_type": state["content_type"],  # 콘텐츠 유형
                "persona_details": PERSONA,  # 페르소나 세부 정보
            }
        )

        state["persona_extracted"] = extracted_persona

        # 추출된 페르소나를 응답으로 반환
        return {"response": extracted_persona}
    

    
