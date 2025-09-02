"""
노드 클래스 모듈

해당 클래스 모듈은 각각 노드 클래스가 BaseNode를 상속받아 노드 클래스를 구현하는 모듈입니다.

아래는 예시입니다.
"""

import asyncio
from agents.base_node import BaseNode
from agents.management.modules.chains import set_instagram_content_verification_chain
from agents.management.modules.state import ManagementState
import logging

class InstagramContentVerificationNode(BaseNode):
    """
    인스타그램 컨텐츠 검증만 수행하는 단일 노드
    """
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chain = set_instagram_content_verification_chain

    def execute(self, state: ManagementState) -> dict:
        print("노드 실행", state)
        logger = logging.getLogger(__name__)
        logger.info(f"[노드] InstagramContentVerificationNode.execute 호출 - state: {state}")

        # 입력 평탄화: LangSmith/LangGraph가 다양한 형태로 전달하는 입력을 흡수
        input_data = {}
        # 1) '/runs' 계열: state['input'] 아래에 값이 들어옴
        if isinstance(state, dict) and isinstance(state.get("input"), dict):
            input_data = state.get("input", {})
        # 2) 값이 직접 최상위로 들어온 경우
        elif isinstance(state, dict):
            input_data = state
        # 3) 메시지 채널로 들어온 경우(Studio 등): 마지막 user 메시지 content를 시도 파싱 (문자열/딕셔너리/블록 리스트 모두)
        if (not input_data) and isinstance(state, dict) and isinstance(state.get("messages"), list) and state["messages"]:
            last_msg = state["messages"][-1]
            content = last_msg.get("content") if isinstance(last_msg, dict) else None
            if isinstance(content, str):
                try:
                    import json as _json
                    parsed = _json.loads(content)
                    if isinstance(parsed, dict):
                        input_data = parsed
                except Exception:
                    pass
            elif isinstance(content, dict):
                input_data = content
            elif isinstance(content, list):
                # 블록 리스트 처리: text/value에 JSON 문자열이 들어오는 경우 우선 파싱
                import json as _json
                for block in content:
                    if isinstance(block, dict):
                        text_val = block.get("text") or block.get("value")
                        if isinstance(text_val, str) and text_val.strip():
                            t = text_val.strip()
                            if t.startswith("{") and t.endswith("}"):
                                try:
                                    parsed = _json.loads(t)
                                    if isinstance(parsed, dict):
                                        input_data.update(parsed)
                                except Exception:
                                    pass
                # fallback: 블록 내에 직접 키가 있으면 흡수
                for block in content:
                    if isinstance(block, dict):
                        for k in ("image_url", "text_content"):
                            if k in block and isinstance(block[k], str):
                                input_data[k] = block[k]
        
        # 디버깅: input_data 내용 확인
        logger.info(f"[노드] input_data: {input_data}")
        logger.info(f"[노드] input_data keys: {input_data.keys() if isinstance(input_data, dict) else 'Not a dict'}")

        # 단순한 입력 처리: image_url과 text_content만 사용
        image_url = input_data.get("image_url", "")
        text_content = input_data.get("text_content", "")
        
        logger.info(f"[노드] image_url: '{image_url}', text_content: '{text_content}'")
        
        # self.chain이 함수이므로 직접 호출
        result = self.chain(image_url, text_content)
        # 체인 결과를 상태에 병합하고 그대로 반환
        if isinstance(result, dict):
            state.update(result)
            return result
        state["content_verification_result"] = result
        return {"content_verification_result": result}
