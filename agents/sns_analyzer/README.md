# SNS 분석기 (SNS Analyzer)

## 개요

이 모듈은 Act 1: Entertainment의 SNS 성과 분석을 담당하는 LangGraph Workflow입니다. Instagram API를 통한 데이터 수집 및 월간 성과 분석을 제공하여 인플루언서의 콘텐츠 성과를 종합적으로 분석합니다.

## 주요 노드

### InstagramDataCollectorNode
**목적**: Instagram API를 통한 데이터 수집 및 메트릭 계산
- **입력**: InstagramAnalysisState (instagram_user_id, access_token, analysis_period)
- **처리**: 
  - 계정 인사이트 수집 (월간/일간 reach, 팔로워 수, 프로필 조회수)
  - 미디어 목록 및 개별 인사이트 수집
  - 참여율, 팔로워 성장률, 콘텐츠 타입별 성과 계산
- **출력**: 수집된 데이터 요약 및 상태 업데이트
- **에러 처리**: 재시도 로직 및 상세한 에러 분류

## 구조

```
sns_analyzer/
├── modules/                # 모듈 구성 요소
│   ├── __init__.py        
│   ├── errors.py          # 커스텀 예외 클래스들
│   ├── nodes.py           # Workflow 노드 (InstagramDataCollectorNode)
│   ├── state.py           # 상태 정의 (InstagramAnalysisState)
│   └── tools.py           # Instagram API 호출 및 메트릭 계산 함수
├── pyproject.toml         # 프로젝트 의존성
├── README.md              # 이 문서
└── workflow.py            # Instagram 분석 Workflow 정의
```

## 사용 방법

SNS 분석 Workflow는 다음과 같이 사용할 수 있습니다:

```python
from agents.sns_analyzer.workflow import instagram_analysis_workflow

# 초기 상태 설정
initial_state = {
    "instagram_user_id": "your_user_id",
    "access_token": "your_access_token",
    "analysis_period": "2024-01",
    "request_type": "monthly_analysis",
    "response": []
}

# Workflow 실행
result = instagram_analysis_workflow.build().invoke(initial_state)
```

## 확장 방법

이 모듈은 확장성을 고려하여 설계되었습니다. 새로운 기능(백로그)을 추가하려면:

1. `modules/nodes.py`에 새로운 노드 클래스 추가
2. 필요에 따라 `modules/state.py`에 상태 관리 추가
3. 필요에 따라 `model.py`, `chain.py` 등의 해당 노드에서 사용되는 관련 모듈을 수정/추가하세요.
4. `workflow.py`에서 Workflow에 새 노드를 엣지로 연결

## 라이센스

이 모듈은 Proact0의 Act 1: Entertainment의 내부 프로젝트로, 그룹 정책에 따른 라이센스가 적용됩니다.