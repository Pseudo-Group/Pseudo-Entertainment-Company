from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.management.modules.nodes import (
    InstagramMediaFetchNode,
    InstagramCommentsFetchNode,
    NoChangeNode,
    InstagramCommentsAnalysisNode,
    InstagramAnalysisReportNode,
)
from agents.management.modules.state import ManagementState
from langchain.utils.env import get_from_env


class ManagementWorkflow(BaseWorkflow):
    """
    인스타그램 API 모니터링을 위한 Workflow 클래스

    이 클래스는 인스타그램 포스트의 댓글 수 변화를 모니터링하는 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ManagementState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        인스타그램 모니터링 Workflow 그래프 구축 메서드

        StateGraph를 사용하여 인스타그램 API 모니터링을 위한 Workflow 그래프를 구축합니다.
        조건부 에지를 사용하여 댓글 수 변경 여부에 따라 다른 경로를 실행합니다.

        Returns:
            CompiledStateGraph: 컴파일된 상태 그래프 객체
        """
        builder = StateGraph(self.state)

        # 노드 추가
        builder.add_node("media_fetch", InstagramMediaFetchNode())
        builder.add_node("comments_fetch", InstagramCommentsFetchNode())
        builder.add_node("analysis", InstagramCommentsAnalysisNode())
        builder.add_node("no_change", NoChangeNode())
        builder.add_node("generate_report", InstagramAnalysisReportNode())

        # 시작 노드에서 미디어 가져오기 노드로 연결
        builder.add_edge("__start__", "media_fetch")

        # 조건부 에지: 댓글 수 변경 여부에 따라 분기
        builder.add_conditional_edges(
            "media_fetch",
            self._should_fetch_comments,
            {
                "fetch_comments": "comments_fetch",
                "no_change": "no_change",
                "api_error": "__end__",  # API 오류 시 종료
            },
        )

        # 댓글 가져오기 노드에서 분석 노드로, 분석 노드에서 종료
        builder.add_edge("comments_fetch", "analysis")
        builder.add_edge(
            "analysis", "generate_report"
        )  # Connect analysis to report node
        builder.add_edge("generate_report", "__end__")  # Connect report node to end

        workflow = builder.compile()  # 그래프 컴파일
        workflow.name = self.name  # Workflow 이름 설정

        return workflow

    def _should_fetch_comments(self, state: ManagementState) -> str:
        """
        댓글을 가져올지 결정하는 라우터 함수

        Args:
            state: 현재 상태

        Returns:
            str: 다음 노드 이름 ("fetch_comments", "no_change", 또는 "api_error")
        """
        print("🔄 [Router] 다음 노드 결정 중...")

        # API 오류 체크
        if "API 요청에 실패했습니다" in str(state.get("response", [])):
            print("🔄 [Router] API 오류 감지 → api_error 경로 선택")
            return "api_error"

        # For testing purposes, force fetch_comments
        # return "fetch_comments"

        has_changes = state.get("has_changes", False)

        if has_changes:
            print("🔄 [Router] 댓글 수 변경 감지 → fetch_comments 경로 선택")
            return "fetch_comments"
        else:
            print("🔄 [Router] 댓글 수 변경 없음 → no_change 경로 선택")
            return "no_change"


# def test_instagram_workflow():
#     USER_ID = "17841451140542851"

#     global run_count
#     run_count += 1
#     print(f"\n===== {run_count}번째 실행 =====")
#     """
#     인스타그램 워크플로우를 테스트합니다.
#     """
#     # 인스타그램 API 인증 정보 (실제 값으로 교체 필요)
#     access_token = ACCESS_TOKEN  # 실제 액세스 토큰으로 교체
#     user_id = USER_ID  # 실제 사용자 ID로 교체

#     # 초기 상태 설정
#     initial_state = {
#         "access_token": access_token,
#         "user_id": user_id,
#         "comment_file_path": "./data/instagram_data.json",
#         "comment_analysis_file_path": "./data/instagram_data_analysis.json",
#         "json_data": None,  # JSON 파일에 저장할 데이터
#         "response": []
#     }

#     try:
#         # 워크플로우 실행
#         print("인스타그램 워크플로우를 시작합니다...")

#         # 워크플로우 빌드
#         workflow = management_workflow.build()

#         # 워크플로우 실행
#         result = workflow.invoke(initial_state)

#         # 결과 출력
#         print("\n=== 워크플로우 실행 결과 ===")
#         for message in result.get("response", []):
#             if hasattr(message, 'content'):
#                 print(f"응답: {message.content}")
#             else:
#                 print(f"응답: {message}")

#         # 상태 정보 출력
#         print(f"\n=== 상태 정보 ===")
#         print(f"미디어 데이터 개수: {len(result.get('media_data', []))}")
#         print(f"첫 번째 미디어 ID: {result.get('first_media_id')}")
#         print(f"현재 댓글 수: {result.get('current_comments_count')}")
#         print(f"이전 댓글 수: {result.get('previous_comments_count')}")
#         print(f"변경 여부: {result.get('has_changes')}")

#         if result.get('comments_data'):
#             print(f"댓글 데이터 개수: {len(result.get('comments_data', []))}")

#         # API 오류 체크
#         response_text = str(result.get("response", []))
#         if "API 요청에 실패했습니다" in response_text or "Invalid OAuth access token" in response_text:
#             print(f"\n⚠️  API 오류가 발생했습니다. 토큰을 확인해주세요.")
#             print(f"   - 토큰이 만료되었을 수 있습니다.")
#             print(f"   - 토큰이 올바른지 확인해주세요.")
#             print(f"   - 인스타그램 API 권한을 확인해주세요.")

#     except Exception as e:
#         print(f"워크플로우 실행 중 오류 발생: {str(e)}")


# def run_scheduler():
#     # 10분마다 워크플로우 실행
#     schedule.every(1).minutes.do(test_instagram_workflow)
#     # 또는 매 1시간마다: schedule.every().hour.do(test_instagram_workflow)

#     print("스케줄러가 시작되었습니다. (Ctrl+C로 종료)")
#     while True:
#         schedule.run_pending()
#         time.sleep(1)

management_workflow = ManagementWorkflow(ManagementState)

if __name__ == "__main__":
    # run_count = 0
    # # run_scheduler()
    # test_instagram_workflow()
    workflow = management_workflow.build()

    ACCESS_TOKEN = get_from_env("instagram_api_key", "INSTAGRAM_API_KEY")
    API_KEY = get_from_env("google_api_key", "GOOGLE_API_KEY")
    USER_ID = "17841451140542851"

    initial_state = {
        "access_token": ACCESS_TOKEN,
        "user_id": USER_ID,
        "api_key": API_KEY,
        "comment_file_path": "./data/instagram_data.json",
        "comment_analysis_file_path": "./data/instagram_data_analysis.json",
        "analysis_report_file_path": "./data/analysis_report.json",
        "json_data": None,
        "response": [],
    }
    result = workflow.invoke(initial_state)
    print(result)
