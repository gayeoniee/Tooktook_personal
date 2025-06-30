# 🐱‍💻 Tooktook (Personal Version)

> ✨ **본 프로젝트는 LG U+ WhyNot Camp 7기 팀 프로젝트에서 출발하였으며 개인 포트폴리오 용도로 구조와 내용을 재정비한 버전입니다.**

---

## 💬 프로젝트 개요

**Tooktook**은 상담사의 업무 효율성과 정확성을 높이기 위한 **AI 기반 실시간 상담 지원 시스템**입니다. 상담 중 발생하는 반복적이고 복잡한 문의 상황에서, 실시간 음성 인식(STT), 키워드 기반 응답 추천, 상담 요약 등 다양한 기능을 통해 상담사를 보조합니다.

<p align="center">
  <img src="./pic/툭툭이.png" alt="툭툭이" width="220"/>
  <img src="./pic/툭툭이2.png" alt="툭툭이2" width="220"/>
  <br/>
  <em style="font-size: 13px; color: gray;">* GPT 기반 이미지 생성 툴을 활용해 제작된 캐릭터입니다.</em>
</p>

---

## 📓 프로젝트 문서 모음

<details>
<summary>툭툭 기획서 PDF</summary>
<a href="툭툭 기획서 PPT.pdf" target="_blank">툭툭 프로젝트 기획서 보러가기</a>
</details>

<details>
<summary>시스템 구조 및 기술 선택 배경</summary>
<a href="툭툭 시스템 구조 및 기술 선택 배경.pdf" target="_blank">세부 내용 (PDF)</a>
</details>

<details>
<summary>프로토타입</summary>
<a href="https://sjun4040.github.io/prototype/" target="_blank">▶️ 프로토타입 바로가기</a>
</details>

---

## 💡 Tooktook은 어떤 문제를 해결하나요?

> “비습한 질문이 계속 발생하는데 답변 찾는 데 시간이 너무 오래 간다”  
> “상당이 밀리면 고객도 힘들고 나도 더 급해지는다”  
> “지금 상황에서 무엇을 먼저 보여야 할지 모르겠다”

툭툭은 이런 상당사의 문제를 해결합니다.

- 음성 입력을 텍스트로 변환
- 대화 내 주요 키워드 추출
- 관련 자료 및 메뉴얼 기반 응답 문장 추천
- 상당 진행 중 자동으로 요약점 정보 요약 및 저장

---

## 🔹 시스템 개요

| 항목 | 내용 |
|--------|-----------------------------|
| 프로젝트명 | Tooktook (툭툭) |
| 목적 | 상당사의 대응 효율성과 정확성 강화 |
| 해결 방식 | STT + 키워드 추출 + RAG 기반 문서 추천 + 자동 요약 |
| 사용자 | 상당사 (내부 시스템 사용자) |

---

### 📊 시스템 흐름도
<img src="./pic/시스템흐름도.png" alt="흐름도" width="800"/>

### 📁 시스템 아키텍처
<img src="./pic/시스템아키텍쳐.png" alt="아키텍쳐" width="700"/>

---

## ⚡️ 핵심 기능 요약

| ID   | 기능이름 | 설명 | 우선순위 |
|------|-------------|------------------|--------|
| F-01 | STT 변환     | 음성을 텍스트로 변환 | 중 |
| F-02 | 텍스트 출력  | 변환된 텍스트 보여주기 | 상 |
| F-03 | 키워드 추출  | 키워드 검색 | 상 |
| F-04 | 응답 추천    | AI를 이용하여 추천 문구 출력 | 상 |
| F-06 | 상담 요약    | 진행 중 요약점 자동 요약 | 중 |
| F-07 | 상담 저장    | 전체 상담 내용 및 요약 저장 | 상 |

---

## 🔎 사용 시나리오 요약

1. 상담사가 웹 시스템에 로그인 후 상담 시작
2. 전화 연결 → 실시간 텍스트 변환
3. 텍스트 내 키워드 자동 추출
4. 관련 응답 문서 또는 문장 추천 (RAG 기반)
5. 상담 종료 시 자동 요약 생성 및 저장

---

## 📊 WBS (Work Breakdown Structure)
<img src="./pic/WBS.png" alt="WBS" width="1000"/>

---

## 🛠️ 사용 기술 스택

### 💻 Languages

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![SQL](https://img.shields.io/badge/SQL-4479A1?style=flat&logo=mysql&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)

### 📚 Libraries & Frameworks

![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat&logo=pandas)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat)
![Seaborn](https://img.shields.io/badge/Seaborn-76B900?style=flat)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat&logo=scikit-learn)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=flat&logo=tensorflow&logoColor=white)
<br>
![LangChain](https://img.shields.io/badge/LangChain-000000?style=flat&logo=langchain&logoColor=white)
![SentenceTransformers](https://img.shields.io/badge/SentenceTransformers-6e5a90?style=flat&logo=sentencetransformers&logoColor=white)
![GeminiApi](https://img.shields.io/badge/GeminiApi-9f22c8?style=flat&logo=gemini&logoColor=white)
![GPTApi](https://img.shields.io/badge/GPTApi-29051f?style=flat&logo=gpt&logoColor=white)

### 📦 Database

![ChromaDB](https://img.shields.io/badge/ChromaDB-09cee1?style=flat&logo=chromadb&logoColor=black)
