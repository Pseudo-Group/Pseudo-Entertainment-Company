# test code

"""
음악 Workflow 테스트 모듈

이 모듈은 MusicWorkflow 클래스의 기능을 테스트합니다.
"""

import pytest
from unittest.mock import Mock

from agents.music.workflow import MusicWorkflow
from agents.music.modules.state import MusicState
from modules.models import ChatGPT


@pytest.fixture
def mock_chatgpt():
    """ChatGPT 모의 객체 생성"""
    mock = Mock(spec=ChatGPT)
    mock.generate.return_value = "테스트 음악 가사"
    return mock


@pytest.fixture
def music_workflow(mock_chatgpt):
    """MusicWorkflow 인스턴스 생성"""
    return MusicWorkflow(MusicState, mock_chatgpt)


def test_music_workflow_initialization(music_workflow, mock_chatgpt):
    """MusicWorkflow 초기화 테스트"""
    assert music_workflow.name == "MusicWorkflow"
    assert music_workflow.state == MusicState
    assert music_workflow.model == mock_chatgpt


def test_music_workflow_build(music_workflow):
    """Workflow 그래프 구축 테스트"""
    graph = music_workflow.build()
    
    # 그래프가 성공적으로 생성되었는지 확인
    assert graph is not None
    assert graph.name == "MusicWorkflow"
    
    # 노드가 올바르게 추가되었는지 확인
    assert "generate_music" in graph.nodes


def test_music_workflow_execution(music_workflow, mock_chatgpt):
    """Workflow 실행 테스트"""
    # 테스트용 입력 상태
    initial_state = {
        "query": "여름 바다를 주제로 한 가사",
        "response": []
    }
    
    # Workflow 실행
    graph = music_workflow.build()
    result = graph.invoke(initial_state)
    
    # 결과 검증
    assert result is not None
    assert "response" in result
    assert "query" in result
    assert result["query"] == initial_state["query"]
    
    # ChatGPT가 호출되었는지 확인
    mock_chatgpt.generate.assert_called_once()


def test_music_workflow_error_handling(music_workflow, mock_chatgpt):
    """에러 처리 테스트"""
    # ChatGPT 에러 시뮬레이션
    mock_chatgpt.generate.side_effect = Exception("API Error")
    
    initial_state = {
        "query": "에러 테스트",
        "response": []
    }
    
    # Workflow 실행 및 에러 처리 검증
    graph = music_workflow.build()
    with pytest.raises(Exception) as exc_info:
        graph.invoke(initial_state)
    
    assert "API Error" in str(exc_info.value)


def test_music_workflow_empty_query(music_workflow):
    """빈 쿼리 처리 테스트"""
    initial_state = {
        "query": "",
        "response": []
    }
    
    graph = music_workflow.build()
    result = graph.invoke(initial_state)
    
    assert result is not None
    assert result["query"] == ""


@pytest.mark.parametrize("test_input,expected", [
    ("여름 바다", "여름 바다"),
    ("겨울 눈", "겨울 눈"),
    ("가을 단풍", "가을 단풍"),
])
def test_music_workflow_different_queries(music_workflow, mock_chatgpt, test_input, expected):
    """다양한 쿼리에 대한 테스트"""
    initial_state = {
        "query": test_input,
        "response": []
    }
    
    graph = music_workflow.build()
    result = graph.invoke(initial_state)
    
    assert result["query"] == expected
    mock_chatgpt.generate.assert_called()