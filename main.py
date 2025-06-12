import streamlit as st
import random
import time

# Streamlit 앱의 메인 함수를 정의합니다.
def main():
    # 애플리케이션의 제목을 설정합니다.
    st.title("학생 발표 순서 추첨 룰렛 🎡")

    # 세션 상태(session state)를 초기화합니다.
    # st.session_state는 Streamlit 앱의 상태를 저장하고 관리하는 데 사용됩니다.
    # 앱이 리로드되거나 버튼이 클릭되어도 이 변수들의 값은 유지됩니다.
    if 'max_students' not in st.session_state:
        st.session_state.max_students = 1

    if 'drawn_numbers' not in st.session_state:
        st.session_state.drawn_numbers = []

    # available_numbers는 다른 변수들의 초기화 후, 그 값들에 따라 초기화될 수 있습니다.
    # 이는 앱이 처음 로드될 때와 max_students가 변경되었을 때 모두 적용됩니다.
    # available_numbers가 세션에 없거나, 현재 학생 수와 뽑힌/남은 학생 수의 합이 맞지 않을 때만 재초기화
    if 'available_numbers' not in st.session_state or \
       (len(st.session_state.available_numbers) == 0 and st.session_state.max_students > 0 and not st.session_state.drawn_numbers) or \
       (st.session_state.max_students != len(st.session_state.drawn_numbers) + len(st.session_state.available_numbers)):
        if not st.session_state.drawn_numbers: # 뽑힌 번호가 없으면 완전히 재초기화
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))

    # 룰렛의 초기 숫자 표시를 위한 세션 상태를 설정합니다.
    if 'roulette_display_number' not in st.session_state:
        st.session_state.roulette_display_number = "---" # 초기 빈 상태 표시

    # 총 학생 수를 입력받는 숫자 입력 필드를 생성합니다.
    max_students_input = st.number_input(
        "총 학생 수를 입력하세요:",
        min_value=1,
        value=st.session_state.max_students,
        step=1,
        help="발표에 참여할 학생의 총 인원수를 입력하세요."
    )

    # 입력된 학생 수가 이전과 다르면 룰렛을 초기화합니다.
    if max_students_input != st.session_state.max_students:
        st.session_state.max_students = max_students_input
        st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        st.session_state.drawn_numbers = []
        st.session_state.roulette_display_number = "---" # 학생 수 변경 시 룰렛 숫자 초기화
        st.success(f"✅ 룰렛이 **{st.session_state.max_students}명**의 학생으로 초기화되었습니다. 이제 '룰렛 돌리기' 버튼을 눌러주세요!")
        st.rerun()

    st.markdown("---") # 구분선 추가

    # 현재 남아있는 번호들을 표시합니다.
    st.info(f"**남아있는 번호:** {st.session_state.available_numbers if st.session_state.available_numbers else '없음'}")
    # 추첨된 번호들을 순서대로 표시합니다.
    st.success(f"**추첨된 순서:** {st.session_state.drawn_numbers if st.session_state.drawn_numbers else '아직 추첨된 번호가 없습니다.'}")

    st.markdown("---") # 구분선 추가

    # 룰렛 애니메이션 컨테이너를 위한 placeholder를 생성합니다.
    # 이 placeholder를 통해 룰렛의 전체 HTML/CSS를 동적으로 업데이트하여 숫자 애니메이션을 구현합니다.
    roulette_placeholder = st.empty()

    # 룰렛을 렌더링하는 함수를 정의합니다.
    # 이 함수는 룰렛의 HTML/CSS와 함께 현재 표시될 숫자를 포함하여 룰렛을 그립니다.
    def render_roulette_visual(current_number_display="---", number_color="#333", font_size="4em"):
        roulette_placeholder.markdown(f"""
        <style>
        .roulette-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            width: 250px;
            height: 250px;
            margin: 30px auto;
        }}

        .roulette-wheel {{
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
        }}

        .roulette-pointer {{
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
        }}

        @keyframes spin {{
            from {{
                transform: rotate(0deg);
            }}
            to {{
                transform: rotate(360deg);
            }}
        }}

        /* 룰렛 중앙에 숫자를 표시하기 위한 스타일 */
        .roulette-number-display {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-size: {font_size}; /* 동적으로 변경될 폰트 크기 */
            font-weight: bold;
            color: {number_color}; /* 동적으로 변경될 숫자 색상 */
            z-index: 11; /* 포인터보다 위에 오도록 */
            text-align: center;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }}
        </style>

        <div class="roulette-container">
            <div class="roulette-pointer"></div>
            <div class="roulette-wheel"></div>
            <div class="roulette-number-display">
                {current_number_display}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 앱 로드 시 또는 초기화 시 룰렛을 초기 상태로 렌더링합니다.
    render_roulette_visual(st.session_state.roulette_display_number)

    # '룰렛 돌리기' 버튼을 생성합니다.
    col1, col2 = st.columns(2) # 버튼을 나란히 배치하기 위해 두 개의 컬럼을 생성합니다.

    with col1:
        if st.button("룰렛 돌리기 🎰", help="남아있는 학생 중 한 명을 무작위로 추첨합니다."):
            if st.session_state.available_numbers:
                # 룰렛 애니메이션 시작: 축하 풍선 효과를 미리 보여줍니다.
                st.balloons()

                # 룰렛 스핀 애니메이션 (중앙 숫자 변경)
                spin_duration = 2 # 룰렛이 숫자를 바꾸며 도는 시간 (초)
                num_frames = 30 # 숫자 변경 횟수 (애니메이션 프레임 수)
                sleep_per_frame = spin_duration / num_frames # 각 프레임 당 지연 시간

                # 스피너를 보여주며 애니메이션 진행 중임을 알립니다.
                with st.spinner(f'룰렛이 힘차게 돌아가는 중... 잠시 기다려주세요!'):
                    for i in range(num_frames):
                        # 남아있는 번호 중에서 무작위로 숫자를 선택하여 애니메이션에 사용합니다.
                        display_num = random.choice(st.session_state.available_numbers)
                        # 숫자의 색상과 크기에 애니메이션 효과를 줍니다.
                        anim_color = f"hsl({(i * 10) % 360}, 70%, 50%)" # 색상 변화 효과
                        anim_font_size = f"{3 + (i / num_frames) * 2}em" # 점차 커지도록
                        # 룰렛의 HTML/CSS와 함께 현재 숫자를 렌더링하여 업데이트합니다.
                        render_roulette_visual(display_num, anim_color, anim_font_size)
                        time.sleep(sleep_per_frame)

                # 최종 결과 처리
                drawn_number = random.choice(st.session_state.available_numbers)
                st.session_state.available_numbers.remove(drawn_number)
                st.session_state.drawn_numbers.append(drawn_number)

                # 최종 당첨 번호를 룰렛 중앙에 표시하고 색상 및 크기를 고정합니다.
                final_font_size = "5em"
                final_color = "#FF4500" # 당첨 번호 색상 (주황색 계열)
                render_roulette_visual(drawn_number, final_color, final_font_size) # 최종 번호 렌더링

                # 룰렛 아래에 최종 당첨 번호를 한 번 더 표시합니다.
                st.markdown(f"## 🎉 **{drawn_number}번 학생 당첨!**")
                time.sleep(1) # 당첨 번호가 잠시 보이도록
                st.rerun() # 변경사항 즉시 반영 (전체 상태 업데이트를 위해 필요합니다.)
            else:
                # 더 이상 뽑을 번호가 없을 때 경고 메시지를 표시합니다.
                st.warning("더 이상 뽑을 학생이 없습니다. '룰렛 초기화' 버튼을 눌러 다시 시작하세요.")

    with col2:
        # '룰렛 초기화' 버튼을 생성합니다.
        if st.button("룰렛 초기화 🔄", help="모든 추첨 상태를 처음으로 되돌립니다."):
            st.session_state.max_students = 1 # 초기 학생 수로 되돌림
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
            st.session_state.drawn_numbers = []
            st.session_state.roulette_display_number = "---" # 초기화 시 룰렛 숫자도 초기화
            st.info("룰렛이 초기화되었습니다.")
            render_roulette_visual(st.session_state.roulette_display_number) # 초기 상태 룰렛 렌더링
            st.rerun()

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
