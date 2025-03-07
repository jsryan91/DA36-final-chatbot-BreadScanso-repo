from langchain_openai import ChatOpenAI
from langchain.chat_models import ChatAnthropic
from langchain_anthropic import ChatAnthropic
import os
from dotenv import load_dotenv

# .env 파일로부터 환경 변수 로드
load_dotenv()

class LangChainPipeline:
    def __init__(self):
        # Claude 모델 초기화 (비즈니스 어드바이저용)
        self.model_claude = ChatAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"), model="claude-3-opus-20240229", temperature=0.7)
        # openai 모델 초기화
        # self.model_openai = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"), model_name="gpt-3.5-turbo", temperature=0.7, max_tokens=2048)

    # 🐕🐕🐕🐕🐕
    def get_business_advice(self, question):
        from langchain.schema import HumanMessage

        # 비즈니스 맥락을 포함한 프롬프트 구성
        prompt = f"""
        당신은 베이커리 사업 전문가로, 브레드스캔소라는 베이커리 업체의 매출/판매 데이터를 기반으로 전략적인 조언을 제공합니다.

        ### 질문:
        {question}

        ### 상황:
        - 브레드스캔소는 베이커리 제품을 생산하는 업체입니다.
        - 제품군은 빵이 주가 되고, 케이크, 마카롱 등 디저트류도 포함됩니다.

        위 상황을 바탕으로 질문에 전략적이고 실질적인 비즈니스 조언을 제공해주세요.
        단순히 데이터를 요약하는 것보다 비즈니스 관점에서 인사이트와 실행 가능한 조언을 제공하는 데 중점을 두세요.

        베이커리 산업의 일반적인 트렌드와 모범 사례를 바탕으로 조언해주세요.
        """

        messages = [HumanMessage(content=prompt)]
        response = self.model_claude.invoke(messages)
        return response.content

   # 🐕🐕🐕🐕🐕
   # 벡터-리터리버 연결 후에 살릴 코드
   #  def create_business_advisor_pipeline(self):
   #      """매출 데이터 기반 비즈니스 분석 파이프라인"""
   #      # 데이터 검색용 리트리버 가져오기
   #      # 🐕 retriever =
   #      from langchain.schema import HumanMessage
   #      # 비즈니스 분석용 프롬프트 템플릿
   #      prompt = ChatPromptTemplate.from_template("""
   #      당신은 베이커리 사업 전문가로, 브레드스캔소라는 베이커리 업체의 매출/판매 데이터를 기반으로 전략적인 조언을 제공합니다.
   #
   #      ### 질문:
   #      {question}
   #
   #      ### 관련 매출/판매 데이터:
   #      {context}
   #
   #      ### 추가 비즈니스 맥락:
   #      - 브레드스캔소는 프리미엄 베이커리 제품을 생산하는 업체입니다.
   #      - 제품군에는 빵, 케이크, 쿠키, 페이스트리 등이 포함됩니다.
   #      - 주요 고객층은 20-40대 직장인과 가족 단위 고객입니다.
   #      - 현재 계절적 요인과 지역 특성을 고려한 마케팅 전략을 구상 중입니다.
   #
   #      위 데이터와 맥락을 바탕으로 질문에 전략적이고 실질적인 비즈니스 조언을 제공해주세요.
   #      단순히 데이터를 요약하는 것보다 비즈니스 관점에서 인사이트와 실행 가능한 조언을 제공하는 데 중점을 두세요.
   #
   #      실제 데이터가 부족한 경우에는 베이커리 산업의 일반적인 트렌드와 모범 사례를 바탕으로 조언해도 좋습니다.
   #      """)
   #
   #      llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"),
   #                       model_name="gpt-3.5-turbo",
   #                       temperature=0.7)
   #
   #      # 파이프라인 구성
   #      business_chain = (
   #              {"context": retriever, "question": lambda x: x}
   #              | prompt
   #              | llm
   #              | StrOutputParser()
   #      )
   #
   #      return business_chain
