"""
이미지 관련 콘텐츠 생성을 위한 Workflow 모듈

이 모듈은 이미지 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
StateGraph를 사용하여 이미지 처리를 위한 워크플로우를 구축합니다.
"""
import sys
import os

# 프로젝트 루트 디렉토리를 sys.path에 추가
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from langgraph.graph import StateGraph

from agents.base_workflow import BaseWorkflow
from agents.image.modules.state import ImageState
from agents.image.modules.nodes import ConceptDecompositionNode, ConceptDecisionNode, CreateStoryboardNode, LayoutNode, BackgroundNode, StyleNode, PoseNode, PhotographerNode, DirectorNode, ImageGenerationNode


class ImageWorkflow(BaseWorkflow):
    """
    이미지 관련 콘텐츠 생성을 위한 Workflow 클래스

    이 클래스는 이미지 기반 콘텐츠 생성을 위한 Workflow를 정의합니다.
    BaseWorkflow를 상속받아 기본 구조를 구현하고, ImageState를 사용하여 상태를 관리합니다.
    """

    def __init__(self, state):
        super().__init__()
        self.state = state

    def build(self):
        """
        이미지 Workflow 그래프 구축 메서드
        """
        builder = StateGraph(self.state)
    
        # 노드 추가
        builder.add_node("concept_decomposition", ConceptDecompositionNode())
        builder.add_node("concept_decision", ConceptDecisionNode())
        builder.add_node("create_storyboard", CreateStoryboardNode())
        builder.add_node("set_background", BackgroundNode())
        builder.add_node("set_layout", LayoutNode())
        builder.add_node("set_style", StyleNode())
        builder.add_node("set_pose", PoseNode())
        builder.add_node("set_photographer", PhotographerNode())
        builder.add_node("prompter", DirectorNode())
        builder.add_node("image_generation", ImageGenerationNode())
        
    
        # 엔트리포인트 설정 및 엣지 연결
        builder.set_entry_point("concept_decomposition")  # 시작점 설정
        builder.add_edge("concept_decomposition", "concept_decision")
        builder.add_edge("concept_decision", "create_storyboard")
        builder.add_edge("create_storyboard", "set_background")
        builder.add_edge("set_background", "set_layout")
        builder.add_edge("set_layout", "set_style")
        builder.add_edge("set_style", "set_pose")
        builder.add_edge("set_pose", "set_photographer")
        builder.add_edge("set_photographer", "prompter")
        builder.add_edge("prompter", "image_generation")
        builder.add_edge("image_generation", "__end__")  # 종료점 연결
    
        workflow = builder.compile()
        workflow.name = self.name
    
        return workflow



initial_state = {
    "information": {
        "title": "Home sweet home",
        "context": """
        You say it's changed
        Show must go on, behave
        오랜만에 옛 노래해
        I'm feelin' like I never left
        (That's right) I never left
        But you ain't know, O.K then lights, camera
        Act like you know
        Don't play on me, no, we're
        Airbnb, you're homeless
        혼비백산-해진-미-장센 (Mise-en-scène)
        도레미파시도 (Now, you know it)
        두껍아 두껍아 came with the troops
        뜯고 맛보고 즐기고 big bang when I shoot
        King in the zoo, he gotta do what I do
        One of one, not of them (Mirror)
        Man in the views aimin' at you
        Yeah, I'm aiming at a man, and amen, achoo
        Bless you, all cleaned house, fu
        Golden days are still alive
        외롭다는 말하지 마
        내가 있는 곳, 네가 있을 곳
        The place that I belong
        Home sweet home
        Home sick home
        Well I said, I would be back
        And I'd never let you go
        Pick a petal off a flower
        Daze you love me nope?
        Well I said, I would be back
        And I'd never let you go
        Pick a petal off a flower
        Do you love me or (stop!)
        Winner, winner chicken killer, 삼계탕 dinner
        하나 둘 set down (one, two, step) 'fantastic'한 팀워크
        Not mini, 많이 'More'
        Rock, scissors, paper, toast
        This is how we do it, just do it, let's do it y'all
        Work, work 월화수목금토- 일
        They gon' wait til' I'm gone
        So I came, I saw, I won
        G just D-word is my bond
        나 무대로 올라, coup d'e shit
        단숨에 호흡곤란, hook catch this
        아 '무제' 도 몰라? bull as shit
        Whatever, now or never
        Golden days are still alive
        외롭다는 말하지 마
        네가 있을 곳에 내가 있는 걸
        The place that I belong
        Home sweet home
        Home sick home
        Well I said, I would be back
        And i'd never let you go
        Pick a petal off a flower
        Daze you love me nope?
        Well I said, I would be back
        And i'd never let you go
        Pick a petal off a flower
        Do you love me or (stop!)
        We alike dead or alive, your life? Still life
        It's so nice, I missed you a lot
        You're welcome back home, wherever you are
        We alike dead or alive, your life is still with me
        Livin' good life, day or nights
        The highlight, it's about time to 'rock-on'
        Home sweet home
        Home sick home
        Well, I said, I would be back
        And I'd never let you go
        Pick a petal off a flower
        Daze, you love me, nope?
        Well, I said, I would be back
        And I'd never let you go
        Pick a petal off a flower
        Do you love me or (Stop)
        """,
        "style": """
        'HOME SWEET HOME'은 곡 제목 그대로 "즐거운 나의 집"이라는 의미로, "즐거운 나의 집"인 팬들 곁으로 돌아왔다는 메시지를 전달하며 팬들과의 깊은 유대감을 상징적으로 표현했다. 팬들과 대중의 곁을 한순간도 떠난 적이 없다는 메시지를 담아, 무대 위에서 자유롭게 뛰놀며 즐기는 듯한 가사와 리듬을 통해 듣는 이들에게 즐거움을 선사한다.
        """
    },
    "album_cover_style": "바쁜 도시 생활에 지쳐 고향 집으로 돌아와 느끼는 편안함과 추억"
}


# 이미지 Workflow 인스턴스 생성
image_workflow = ImageWorkflow(ImageState)

work = image_workflow.build()
result = work.invoke(initial_state)

print(result)
