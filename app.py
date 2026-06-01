import streamlit as st
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import base64

# 1. API 키 설정
api_key = st.sidebar.text_input("OpenAI API Key", type="password")

if api_key:
    client = OpenAI(api_key=api_key)

    st.title("👙 MD용 도매 상품 소구점 발굴기")
    st.caption("입력한 정보를 바탕으로 타겟과 소구점을 명확하게 뽑아냅니다.")
    
    st.divider()

    # 2. 사용자 입력 섹션
    wholesale_url = st.text_input("1. 도매 사이트 상품 상세페이지 URL")
    product_type = st.text_input("2. 제품 종류", placeholder="예: 캡나시, 골지 브라팬티 세트, 차가브라 등")
    material_info = st.text_area("3. 제품 소재 정보", placeholder="예: 하이텐션 소프트 스트레치, 나일론 80%, 스판 20% 등")
    extra_info = st.text_area("4. MD 실착 테스트 및 디테일 설명 (필수 ⭐)", placeholder="예: 패드가 빠지지 않음, 셔링으로 뱃살 커버 등 직접 발견한 디테일을 적어주세요.")
    uploaded_files = st.file_uploader("5. 직접 촬영한 디테일/테스트 사진 (다중 선택 가능)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    # [새로 추가된 선택사항 칸]
    competitor_reviews = st.text_area("6. 타사 베스트셀러 단점 / 1점 리뷰 (선택사항 💡)", placeholder="예: 세탁 한 번에 패드가 반으로 접혀서 빡침, 어깨끈이 너무 얇아서 살을 파고듦 등")

    # 이미지를 AI가 읽을 수 있도록 변환하는 함수
    def encode_image(uploaded_file):
        return base64.b64encode(uploaded_file.read()).decode('utf-8')

    # 간단한 웹 크롤링 기능
    def fetch_wholesale_text(url):
        if not url: return "URL 정보 없음"
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                return soup.get_text(strip=True)[:2000]
            else:
                return "URL 접근 실패 (로그인 필요 혹은 차단)"
        except Exception as e:
            return f"크롤링 오류: {str(e)}"

    # 3. 분석 시작 버튼
    if st.button("✨ 타겟 및 소구점 발굴하기"):
        # 6번 competitor_reviews는 조건에서 제외하여 빈칸이어도 통과됩니다!
        if not wholesale_url or not product_type or not extra_info or not uploaded_files:
            st.warning("URL, 제품 종류, 추가 설명, 디테일 사진은 필수 입력 항목입니다. MD님이 직접 찾은 디테일을 꼭 넣어주세요!")
        else:
            with st.spinner("정보를 종합하여 타겟과 소구점을 분석 중입니다..."):
                
                wholesale_text = fetch_wholesale_text(wholesale_url)
                
                # AI 지시문
                prompt_text = f"""
                당신은 10년 차 탑급 속옷/의류 브랜드 MD이자 메인 카피라이터입니다.
                아래 제공된 [입력 정보]와 [실물 사진]을 심층 분석하여, 당장 쇼핑몰 상세페이지 기획안에 쓸 수 있는 '아주 구체적이고 날카로운 소구점'을 도출해야 합니다.

                [🚨 절대 금지 사항 - 뻔한 표현 금지]
                - "편안함을 추구하는 여성", "스타일을 중시하는 여성", "활동적인 여성" 같은 포괄적이고 뜬구름 잡는 표현은 절대 쓰지 마세요.
                - 대신, 고객이 일상에서 겪는 '아주 구체적인 불편함(Pain Point)'이나 '특정 상황', '구체적인 체형 고민(키/몸무게/체형)'을 묘사하세요.
                - "경험이 있나요?" 같은 홈쇼핑식 질문형 어투는 절대 쓰지 말고, 확신에 찬 전문가의 평서문으로 작성할 것.

                [🚨 경쟁사 단점 저격 지침]
                - 만약 아래 [경쟁사 단점 정보]가 입력되었다면, 해당 단점 때문에 스트레스받았던 고객들을 집중 저격하세요. 타사 제품을 샀다가 실패한 고객들의 억울함을 달래주며, 우리 제품이 그 문제를 어떻게 완벽하게 해결(사이다 해결)하는지 메인 소구와 부소구에 적극 반영하여 매력적인 비교 카피를 짜내야 합니다. (경쟁사 단점 정보가 없거나 비어있다면, 무시하고 진행하세요.)

                [입력 정보]
                - 제품 종류: {product_type}
                - 제품 소재 정보: {material_info}
                - 추가 설명: {extra_info}
                - 경쟁사 단점 정보: {competitor_reviews if competitor_reviews else '제공 안 됨'}
                - 도매처 기본 텍스트: {wholesale_text}

                [출력 양식] - 반드시 아래 양식 그대로 작성할 것
                (각 항목은 단답형이 아니라, 카피라이팅 톤으로 길고 상세하게 작성할 것)
                
                ### 1. 일반적인 '{product_type}'의 특징
                - 주의사항: 이 항목에는 MD가 입력한 '추가 설명'이나 '경쟁사 단점 정보'를 절대 포함하지 마세요! 오직 시중에 판매되는 '일반적이고 평범한' {product_type}들이 가진 보편적인 내용만 객관적으로 적으세요.
                - 주요 타겟 (3가지): (일반적인 제품을 주로 찾는 다양한 고객군의 특징과 구체적인 상황을 묘사)
                  1. 
                  2. 
                  3. 
                - 제품의 장점 (5가지): (시중 제품들의 평범하고 일반적인 장점을 구체적으로 작성)
                  1. 
                  2. 
                  3. 
                  4. 
                  5. 
                - 제품의 단점 (5가지): (기존 시중 제품들이 가진 고질적인 불편함)
                  1. 
                  2. 
                  3. 
                  4. 
                  5. 

                ### 2. 이 제품만의 추천 소구점 (사진 및 입력 정보 기반)
                - 1번 추천 타겟: (가장 강력하게 구매를 원할, 구체적인 페인포인트를 가진 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 형태의 문장)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 설명)

                - 2번 추천 타겟: 
                - 메인 소구: 
                - 부소구: 

                - 3번 추천 타겟: 
                - 메인 소구: 
                - 부소구: 

                - 4번 추천 타겟: 
                - 메인 소구: 
                - 부소구: 

                - 5번 추천 타겟: 
                - 메인 소구: 
                - 부소구: 
                """

                messages = [
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": prompt_text}]
                    }
                ]
                
                for file in uploaded_files:
                    base64_image = encode_image(file)
                    messages[0]["content"].append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
                
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=2500
                    )
                    
                    st.success("🎉 분석 완료!")
                    st.divider()
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI 분석 중 오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에 OpenAI API Key를 입력하면 프로그램이 활성화됩니다.")