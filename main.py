import streamlit as st
import random
import time

# Streamlit 앱의 메인 함수를 정의합니다.
def main():
    # 애플리케이션의 제목을 설정합니다.
    st.title("학생 발표 순서 추첨 룰렛 🎡")

    # 세션 상태(session state)를 초기화합니다.
    if 'max_students' not in st.session_state:
        st.session_state.max_students = 1

    if 'drawn_numbers' not in st.session_state:
        st.session_state.drawn_numbers = []

    if 'available_numbers' not in st.session_state or \
       (len(st.session_state.available_numbers) == 0 and st.session_state.max_students > 0 and not st.session_state.drawn_numbers) or \
       (st.session_state.max_students != len(st.session_state.drawn_numbers) + len(st.session_state.available_numbers)):
        if not st.session_state.drawn_numbers:
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))


    # 총 학생 수를 입력받는 숫자 입력 필드를 생성합니다.
    max_students_input = st.number_input(
        "총 학생 수를 입력하세요:",
        min_value=1,
        value=st.session_state.max_students,
        step=1,
        help="발표에 참여할 학생의 총 인원수를 입력하세요."
    )

    if max_students_input != st.session_state.max_students:
        st.session_state.max_students = max_students_input
        st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        st.session_state.drawn_numbers = []
        st.success(f"✅ 룰렛이 **{st.session_state.max_students}명**의 학생으로 초기화되었습니다. 이제 '룰렛 돌리기' 버튼을 눌러주세요!")
        st.rerun()

    st.markdown("---") # 구분선 추가

    # 현재 남아있는 번호들을 표시합니다.
    st.info(f"**남아있는 번호:** {st.session_state.available_numbers if st.session_state.available_numbers else '없음'}")
    # 추첨된 번호들을 순서대로 표시합니다.
    st.success(f"**추첨된 순서:** {st.session_state.drawn_numbers if st.session_state.drawn_numbers else '아직 추첨된 번호가 없습니다.'}")

    st.markdown("---") # 구분선 추가

    # 룰렛 애니메이션을 위한 HTML/CSS를 삽입합니다.
    # 이 룰렛은 앱이 실행되는 동안 계속 회전합니다.
    st.markdown("""
    <style>
    .roulette-container {
        display: flex;
        justify-content: center;
        align-items: center;
        position: relative;
        width: 250px;
        height: 250px;
        margin: 30px auto; /* 중앙 정렬 및 여백 */
    }

    .roulette-wheel {
        width: 200px;
        height: 200px;
        border-radius: 50%;
        /* 룰렛 섹션을 위한 원뿔형 그라데이션 */
        background: conic-gradient(
            #FFD700 0% 16.66%, /* Gold */
            #FF6347 16.66% 33.32%, /* Tomato */
            #6A5ACD 33.32% 49.98%, /* SlateBlue */
            #32CD32 49.98% 66.64%, /* LimeGreen */
            #8A2BE2 66.64% 83.3%, /* BlueViolet */
            #FF4500 83.3% 100% /* OrangeRed */
        );
        border: 10px solid #333;
        box-shadow: 0 0 15px rgba(0,0,0,0.5);
        position: relative;
        animation: spin 10s linear infinite; /* 10초 동안 선형으로 무한히 회전 */
    }

    .roulette-pointer {
        width: 0;
        height: 0;
        border-left: 20px solid transparent;
        border-right: 20px solid transparent;
        border-bottom: 30px solid #ff4b4b; /* Streamlit의 빨간색과 유사 */
        position: absolute;
        top: -15px; /* 룰렛 위에 포인터 위치 */
        left: 50%;
        transform: translateX(-50%);
        z-index: 10;
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    </style>

    <div class="roulette-container">
        <div class="roulette-pointer"></div>
        <div class="roulette-wheel"></div>
    </div>
    """, unsafe_allow_html=True)

    # '룰렛 돌리기' 버튼을 생성합니다.
    col1, col2 = st.columns(2)

    with col1:
        if st.button("룰렛 돌리기 🎰", help="남아있는 학생 중 한 명을 무작위로 추첨합니다."):
            if st.session_state.available_numbers:
                # 룰렛이 돌아가는 시각적인 효과를 추가합니다. (스피너 사용)
                with st.spinner('룰렛이 힘차게 돌아가는 중... 잠시 기다려주세요!'):
                    time.sleep(2) # 2초 동안 스피너를 보여줍니다.

                # 최종 결과 처리
                drawn_number = random.choice(st.session_state.available_numbers)
                st.session_state.available_numbers.remove(drawn_number)
                st.session_state.drawn_numbers.append(drawn_number)

                st.balloons() # 축하 풍선 효과!
                st.markdown(f"## 🎉 **{drawn_number}번 학생 당첨!**")
                st.rerun() # 변경사항 즉시 반영
            else:
                st.warning("더 이상 뽑을 학생이 없습니다. '룰렛 초기화' 버튼을 눌러 다시 시작하세요.")

    with col2:
        # '룰렛 초기화' 버튼을 생성합니다.
        if st.button("룰렛 초기화 🔄", help="모든 추첨 상태를 처음으로 되돌립니다."):
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
            st.session_state.drawn_numbers = []
            st.info("룰렛이 초기화되었습니다.")
            st.rerun()

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
