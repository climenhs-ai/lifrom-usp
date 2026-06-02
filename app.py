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

    # 2. 사용자 입력 섹션 (요청하신 항목들로 세분화)
    wholesale_url = st.text_input("1. 도매 사이트 상품 상세페이지 URL (텍스트 읽기용 _ 라엠코리아 사이트 주소 삽입")
    product_type = st.text_input("2. 제품 종류", placeholder="예: 캡나시, 골지 브라팬티 세트, 차가브라 등")
    material_info = st.text_area("3. 제품 소재 정보", placeholder="예: 하이텐션 소프트 스트레치, 나일론 80%, 스판 20% 등")
    extra_info = st.text_area("4. MD 실착 테스트 및 디테일 설명 (필수 ⭐)", placeholder="예: 패드가 빠지지 않음, 셔링으로 뱃살 커버 등 직접 발견한 디테일을 적어주세요.")
    uploaded_files = st.file_uploader("5. 착용/디테일 사진 (이미지 읽기용 _ 신상마켓 사이트 캡쳐 및 직접 촬영)", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
    
    # 💡 딱 하나 추가된 입력 칸: 타사 단점
    competitor_reviews = st.text_area("6. 타사 베스트셀러 단점 / 1점 리뷰 (선택사항 💡)", placeholder="예: 캡이 붕 떠서 옷 태가 안 살아요, 어깨끈이 너무 얇아서 살을 파고듦 등")

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
        if not wholesale_url or not product_type or not extra_info or not uploaded_files:
            st.warning("URL, 제품 종류, 추가 설명, 디테일 사진은 필수 입력 항목입니다. MD님이 직접 찾은 디테일을 꼭 넣어주세요!")
        else:
            with st.spinner("정보를 종합하여 타겟과 소구점을 분석 중입니다..."):
                
                wholesale_text = fetch_wholesale_text(wholesale_url)
                
                # AI 지시문 (MD님이 가장 만족하셨던 순정 코드 베이스)
                prompt_text = f'''
                당신은 10년 차 탑급 속옷/의류 브랜드 MD이자 메인 카피라이터입니다.
                아래 제공된 [입력 정보]와 [실물 사진]을 심층 분석하여, 당장 쇼핑몰 상세페이지 기획안에 쓸 수 있는 '아주 구체적이고 날카로운 소구점'을 도출해야 합니다.

                [🚨 절대 금지 사항 - 뻔한 표현 금지]
                - 사진 속에 피팅 모델이 있더라도 "사람을 인식할 수 없습니다" 같은 방어적인 사과나 안내 문구는 절대 출력하지 마세요. 바로 기획안 내용만 시작하세요.
                - "편안함을 추구하는 여성", "스타일을 중시하는 여성", "활동적인 여성" 같은 포괄적이고 뜬구름 잡는 표현은 절대 쓰지 마세요.
                - 대신, 고객이 일상에서 겪는 '아주 구체적인 불편함(Pain Point)'이나 '특정 상황', '직업', '구체적인 체형 고민(키/몸무게/체형)'을 묘사하세요. (예: "명치 압박 때문에 밥 먹고 소화불량을 겪는 여성", "세탁기 돌릴 때마다 패드가 돌아가서 빡치는 사람", "하루종일 앉아 있어야 하는 사무직 여성", "큰 가슴으로 맞는 브라를 찾기 힘들었던 88사이즈 여성")
                - "경험이 있나요?" 같은 홈쇼핑식 질문형 어투는 절대 쓰지 말고, 확신에 찬 전문가의 평서문으로 작성할 것.

                [✨ 마케팅 전문 용어(네이밍) 포장 스킬]
                - 제공된 팩트(소재, 특징)를 바탕으로, 고급스럽고 전문적인 마케팅 네이밍을 창작해 메인 소구에 적극 섞어 쓰세요. (예: "가슴이 붕 뜨지 않음" -> "들뜸 제로, 인체공학적 3D 커브드 설계")

                [🚨 경쟁사 단점 저격 지침]
                - [경쟁사 단점 정보]가 있다면, 해당 단점으로 고통받던 고객을 타겟으로 삼고 우리 제품이 어떻게 사이다처럼 해결해 주는지 비교 카피에 반영하세요.

                [입력 정보]
                - 제품 종류: {product_type}
                - 제품 소재 정보: {material_info}
                - 추가 설명: {extra_info}
                - 경쟁사 단점 정보: {competitor_reviews if competitor_reviews else '제공 안 됨'}
                - 도매처 기본 텍스트: {wholesale_text}

                [출력 양식] - 반드시 아래 양식 그대로 작성할 것
                (각 항목은 단답형이 아니라, 카피라이팅 톤으로 길고 상세하게 작성할 것)
                
                ### 1. 일반적인 '{product_type}'의 특징
                - 주의사항: 이 항목에는 MD가 입력한 '추가 설명'이나 '경쟁사 단점'을 참고하는 게 아닌, 오직 시중에 판매되는 '일반적이고 평범한' {product_type}들이 가진 보편적인 내용만 객관적으로 적으세요.
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
                - 제품의 단점 (5가지): (기존 시중 제품들이 가진 치명적인 불편함 - 추후 우리 제품이 해결해 줄 페인포인트 빌드업 용도)
                  1. 
                  2. 
                  3. 
                  4. 
                  5. 

	    ### 2. 이 제품만의 추천 소구점 (사진 및 입력 정보 기반)
                - 주의사항: 타겟을 묘사할 때 [절대 금지 사항]을 반드시 지키세요. 구체적인 직업/상황/체형/페인포인트를 콕 집어 적되, 🚨프롬프트에 예시로 적혀있는 "사무직", "소화불량", "88사이즈" 같은 타겟을 절대 그대로 앵무새처럼 베껴 쓰지 마세요! 반드시 MD가 입력한 [제품 정보]와 [타사 단점]을 분석하여, 이 제품에 딱 맞는 구체적 타겟 5가지를 직접 추론하고 창작해야 합니다.
                
                - 1번 추천 타겟: (가장 강력하게 구매를 원할, 구체적인 페인포인트를 가진 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 - 전문 네이밍 포장 스킬 적극 활용할 것)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 구체적인 설명)

                - 2번 추천 타겟: (1번과 다른 각도의 구체적인 고민을 가진 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 - 전문 네이밍 포장 스킬 적극 활용할 것)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 구체적인 설명)

                - 3번 추천 타겟: (구체적인 신체 스펙이나 특정 라이프스타일을 가진 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 - 전문 네이밍 포장 스킬 적극 활용할 것)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 구체적인 설명)

                - 4번 추천 타겟: (앞선 1~3번과 전혀 다른 각도의 체형 고민이나 구체적 상황을 가진 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 - 전문 네이밍 포장 스킬 적극 활용할 것)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 구체적인 설명)

                - 5번 추천 타겟: (아주 소수일 수 있지만, 공감하면 무조건 구매할 수밖에 없는 니치한 타겟)
                - 메인 소구: (고객의 시선을 확 끄는 카피라이팅 - 전문 네이밍 포장 스킬 적극 활용할 것)
                - 부소구: (소재나 디테일을 바탕으로 메인 소구를 논리적으로 뒷받침하는 구체적인 설명)
                '''

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
                        max_tokens=2000
                    )
                    
                    st.success("🎉 분석 완료!")
                    st.divider()
                    st.markdown(response.choices[0].message.content)
                    
                except Exception as e:
                    st.error(f"AI 분석 중 오류 발생: {e}")
else:
    st.info("왼쪽 사이드바에 OpenAI API Key를 입력하면 프로그램이 활성화됩니다.")