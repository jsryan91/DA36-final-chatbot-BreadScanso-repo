# DA36기 최종프로젝트 AI(chatbot) repo
## [RAG 기반 LLM] 베이커리 매출 분석 시스템

### 📂 관련 레포지토리
- **WEB repo** | https://github.com/pladata-encore/DA36-final-web-BreadScanso-repo
- **AI repo - 이미지 인식** | https://github.com/pladata-encore/DA36-final-ai-BreadScanso-repo
- **AI repo - chatbot** | https://github.com/pladata-encore/DA36-final-chatbot-BreadScanso-repo

---

## 📌 프로젝트 개요
- **목표:**  
  자연어로 입력된 질문을 AI가 분석하여 SQL 쿼리를 생성하고, MySQL에서 데이터를 조회해 매출 분석을 제공하는 챗봇 시스템 제공  

- **주요 기능:**  
  - **OpenAI API**를 활용한 질문 이해 및 SQL 변환  
  - **MySQL**을 통한 베이커리 매출 데이터 조회 및 분석  
  - **AI**를 활용한 자연어 응답 생성  
  - **단계별 질문 카테고리화**  
    1. 데이터베이스 조회 여부 판단 → SQL 쿼리 생성 필요 여부 결정  
    2. SQL 쿼리 생성 시 → 분석 필요 여부에 따라 단순 조회 또는 심층 분석 모드 선택
   
  ![category](https://github.com/user-attachments/assets/b9b6af00-5796-454c-afc6-3627d8b27326)

---

## 📸 데모
1️⃣ **대화 맥락 기반**  
![hi](https://github.com/user-attachments/assets/f37f409f-bbb7-4e2e-803b-7d2a25e5eb12)

2️⃣ **단순 조회/집계**  
![sales](https://github.com/user-attachments/assets/4406d86c-95e1-47c2-9996-77d30afbc8a2)

3️⃣ **심층 분석**  
![item](https://github.com/user-attachments/assets/d6e89b8f-fa33-4a2c-bfd2-e191c2eb319b)

---

## 🌊 시스템 흐름도
![flow](https://github.com/user-attachments/assets/e19121f0-cf22-47da-8f98-67b298022ab3)

---

## 🛠 기술 스택
- **언어:** Python  
- **프레임워크 & 라이브러리:**  
  - Flask: API 서버 구축  
  - SQLAlchemy: MySQL 연동  
  - OpenAI API: 자연어 처리 및 응답 생성  
- **데이터베이스:** MySQL  
- **클라우드:** AWS (EC2, EB, S3)  
- **배포도구:** Docker  

---

## 💡 회고 및 개선점
### 🧠 배운 점
- OpenAI API를 활용한 자연어-쿼리 변환 가능성 탐색  
- SQLAlchemy를 이용한 효율적인 데이터베이스 연동  

### 🤓 문제점 및 해결 방법
- 단순한 인사에도 SQL 쿼리를 생성하여 부적절한 답변 제공  
  → SQL 쿼리가 필요한 질문인지 **분류하는 단계** 추가

### 🤷🏻‍♂️ 추가 개선 가능성
- **모델 변경 및 튜닝**  
  - SQL Query 생성 특화 모델 **DB-GPT** 사용  
  - 다양한 **LLM API 테스트**  
  - 프롬프팅 개선 → 예시 제공, 제약 추가, 질문 정제 단계 도입  

- **사용성 확장**  
  - 챗봇의 말투 & 대답 스타일 선택지 제공  
  - 사용자 피드백 반영 👍🏻👎🏻  
  - 소비자 상담용 챗봇 추가  

---

## 👥 참여자 및 기여 활동
- 강한결  
- 전민하  
- 조은비  
