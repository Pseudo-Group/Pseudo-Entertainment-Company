from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.sns_analyzer.modules.nodes import InstagramDataCollectorNode
from agents.sns_analyzer.modules.state import InstagramAnalysisState


class InstagramAnalysisWorkflow(BaseWorkflow):
    """
    Instagram 성과 분석을 위한 Workflow 클래스

    이 클래스는 Instagram API를 통한 데이터 수집 및 월간 성과 분석을 위한 Workflow를 정의합니다.
    InstagramAnalysisState를 사용하여 Instagram 관련 데이터 상태를 관리합니다.
    """

    def __init__(self, state=InstagramAnalysisState):
        super().__init__()
        self.state = state

    def build(self):
        """
        Instagram 분석 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 Instagram 데이터 수집 및 분석을 위한 Workflow를 구축합니다.
        현재는 데이터 수집 노드만 포함하고 있으며, 추후 분석 및 보고서 생성 노드를 추가할 예정입니다.

        Workflow 흐름:
        1. Instagram 데이터 수집 (계정 인사이트, 미디어 목록, 개별 인사이트)
        2. [추후 추가] 데이터 분석 및 인사이트 생성
        3. [추후 추가] 월간 보고서 생성

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)

        # Instagram 데이터 수집 노드 추가
        builder.add_node("instagram_data_collector", InstagramDataCollectorNode())

        # 시작점에서 데이터 수집 노드로 연결
        builder.add_edge("__start__", "instagram_data_collector")

        # 데이터 수집 완료 후 종료 (추후 분석 노드 추가 예정)
        builder.add_edge("instagram_data_collector", "__end__")

        # 추후 추가될 조건부 에지 예시
        # builder.add_conditional_edges(
        #     "instagram_data_collector",
        #     # 데이터 수집 완료 후, 수집된 데이터의 품질이나 타입에 따라
        #     # 다음 분석 노드를 선택하는 라우터 함수
        #     determine_analysis_type,
        #     {
        #         "monthly_analysis": "monthly_report_generator",
        #         "content_analysis": "content_analyzer",
        #         "audience_analysis": "audience_analyzer"
        #     }
        # )

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow


# Instagram 분석 Workflow 인스턴스 생성
instagram_analysis_workflow = InstagramAnalysisWorkflow()
