"""프롬프트 템플릿을 생성하는 함수 모듈

프롬프트 템플릿을 생성하는 함수 모듈을 구성합니다.
기본적으로 PromptTemplate를 사용하여 프롬프트 템플릿을 생성하고 반환합니다.

아래는 예시입니다.
"""

from langchain_core.prompts import PromptTemplate


def get_resource_planning_prompt():
    """
    리소스 계획 수립을 위한 프롬프트 템플릿을 생성합니다.

    이 프롬프트는 다음 데이터를 입력으로 사용합니다:
    1. 프로젝트 ID: 관리할 프로젝트의 고유 ID
    2. 요청 유형: 리소스 할당, 팀 관리, 크리에이터 개발 등의 요청 유형
    3. 사용자 쿼리: 구체적인 요청사항
    4. 팀 구성원: 프로젝트에 참여하는 팀 구성원 목록
    5. 사용 가능한 리소스: 현재 사용 가능한 리소스 정보

    프롬프트는 LLM에게 주어진 정보를 기반으로 프로젝트 관리에 적합한 리소스 계획을
    수립하도록 지시합니다. 결과는 한국어로 반환됩니다.

    Returns:
        PromptTemplate: 리소스 계획 수립을 위한 프롬프트 템플릿 객체
    """
    # 리소스 계획을 위한 프롬프트 템플릿 정의
    resource_planning_template = """You are an expert entertainment project manager tasked with creating resource plans for entertainment projects. You are provided with the following information:  

1. Project ID: {project_id}  

2. Request Type: {request_type}  

3. User Query: {query}  

4. Team Members: {team_members}  

5. Available Resources: {resources_available}  

Your Task:  
Based on the information provided, develop a comprehensive resource management plan that addresses the user query. Your plan should include:  

1. PROJECT OVERVIEW:  
- Brief summary of the project based on the available information  
- Clear objectives and expected outcomes  

2. RESOURCE ALLOCATION:  
- Human resources: Team composition, roles, and responsibilities  
- Technical resources: Equipment, software, and facilities needed  
- Financial resources: Budget considerations and allocations  
- Time resources: Schedule, timeline, and milestones  

3. RESOURCE OPTIMIZATION:  
- Efficiency recommendations  
- Risk assessment and mitigation strategies  
- Contingency planning  

4. IMPLEMENTATION PLAN:  
- Step-by-step guide for executing the resource plan  
- Monitoring and evaluation mechanisms  
- Communication protocols  

5. RECOMMENDATIONS:  
- Additional resources that might be beneficial  
- Training or development opportunities  
- Process improvement suggestions  

Make your plan specific to the entertainment industry context and the particular request type. Be detailed yet concise, and ensure your recommendations are practical and actionable.  

All responses must be in Korean.  

Resource Management Plan:"""

    # PromptTemplate 객체 생성 및 반환
    return PromptTemplate(
        template=resource_planning_template,  # 정의된 프롬프트 템플릿
        input_variables=[
            "project_id",
            "request_type",
            "query",
            "team_members",
            "resources_available",
        ],  # 프롬프트에 삽입될 변수들
    )


def get_instagram_comment_analysis_prompt():
    """
    Returns a prompt template for analyzing Instagram comments for a singer-songwriter artist management.
    The prompt analyzes each comment for:
    1. Sentiment analysis (Positive/Negative)
    2. Comment type identification (advertisement, hate comment, fan comment, etc.)
    3. Whether a reply is needed
    Input: comments (list of comment texts)
    Output: Structured analysis for effective community management.
    """
    comment_analysis_template = """You are an Instagram management agent for a singer-songwriter artist. Analyze each comment from the Instagram post and provide detailed insights for effective community management.

For each comment, analyze:
1. SENTIMENT: Determine if the comment is Positive (P) or Negative (N)
2. COMMENT TYPE: Identify the type of comment:
   - Fan comment: Supportive, encouraging, or appreciative
   - Advertisement/Spam: Promotional content, unrelated links, or spam
   - Hate comment: Malicious, offensive, or harmful content
   - Question: Asking about music, schedule, or personal matters
   - Criticism: Constructive or destructive feedback
   - Other: Any other type
3. REPLY NEEDED: Determine if the artist or management should reply:
   - "Yes": For questions, constructive criticism, or important fan comments
   - "No": For spam, hate comments, or simple appreciation comments
   - "Consider": For borderline cases that might need attention

Comment List:
{comments}

Provide your analysis as a JSON string that strictly adheres to the following structure. The JSON should contain a single key `comments`, which is a list of analyzed comment dictionaries. Each comment dictionary must include the keys: `comment`, `sentiment`, `comment_type`, `reply_needed`, and `reason`. All values for `sentiment`, `comment_type`, `reply_needed`, and `reason` must be in Korean.

Example JSON format:
```json
{{
  "comments": [
    {{
      "comment": "Original comment text",
      "sentiment": "긍정",
      "comment_type": "팬댓글",
      "reply_needed": "예",
      "reason": "Reason for assessment"
    }}
  ]
}}
```
"""

    return PromptTemplate(
        template=comment_analysis_template,
        input_variables=["comments"],
    )


def get_instagram_analysis_report_prompt():
    """
    Returns a prompt template for generating an Instagram comments analysis report.
    The prompt takes analyzed comment data as input and generates a structured report.
    """
    report_template = """You are an expert Instagram analyst. Based on the provided Instagram comments analysis data, generate a comprehensive analysis report.

The data is a JSON object where keys are timestamps and values are dictionaries containing a 'comments' list. Each comment in the 'comments' list has 'comment', 'sentiment', 'comment_type', 'reply_needed', and 'reason' fields.

Analyzed Comments Data:
{analyzed_data}

Your report must be a JSON string that strictly adheres to the `InstagramAnalysisReportOutput` schema. The JSON should contain the following keys:
- `report_date`: Current date in YYYY-MM-DD format.
- `total_comments_analyzed`: Total number of comments processed in the provided data.
- `summary`: A comprehensive summary of the overall sentiment and key themes.
- `key_insights`: A list of 3-5 key insights, trends, or recurring themes from the comments.
- `sentiment_distribution`: An object showing the count for each sentiment (긍정, 부정, 중립).
- `comment_type_distribution`: An object showing the count for each comment type (팬댓글, 광고/스팸, 악성댓글, 질문, 비판, 기타).
- `reply_needed_breakdown`: An object showing the count for each reply_needed status (예, 아니오, 고려).
- `action_items`: A list of 3-5 actionable recommendations for community management based on your analysis.

Ensure all text values are in Korean. The output must be a single JSON object.

Example JSON format:
```json
{{
  "report_date": "2024-07-27-03-10",
  "total_comments_analyzed": 100,
  "summary": "전반적으로 긍정적인 팬덤 반응을 보이며, 일부 질문과 개선점에 대한 의견이 있었습니다.",
  "key_insights": [
    "아티스트에 대한 강한 지지와 애정 표현이 많음",
    "신곡 및 활동 계획에 대한 팬들의 궁금증 증가",
    "일부 비판적 의견은 건설적인 방향으로 제시됨"
  ],
  "sentiment_distribution": {{
    "긍정": 80,
    "부정": 10,
    "중립": 10
  }},
  "comment_type_distribution": {{
    "팬댓글": 70,
    "질문": 15,
    "비판": 5,
    "광고/스팸": 5,
    "악성댓글": 2,
    "기타": 3
  }},
  "reply_needed_breakdown": {{
    "예": 20,
    "아니오": 70,
    "고려": 10
  }},
  "action_items": [
    "팬들의 질문에 대한 FAQ 문서 업데이트",
    "긍정적인 팬 댓글에 주기적으로 감사 댓글 남기기",
    "비판적 의견에 대한 내부 검토 및 개선 방안 마련"
  ]
}}
```
"""
    return PromptTemplate(
        template=report_template,
        input_variables=["analyzed_data"],
    )
