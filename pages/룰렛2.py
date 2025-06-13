import streamlit as st
import random
import time

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="발표 순서 추첨기",
    page_icon="🎲"
)

# --- 앱 제목 ---
st.title("🎲 발표 순서 추첨 룰렛")
st.markdown("---")

# --- Session State 초기화 ---
# 앱이 재실행되어도 유지되어야 하는 값들을 저장합니다.
if 'total_students' not in st.session_state:
    st.session_state.total_students = 0
if 'remaining_numbers' not in st.session_state:import streamlit as st
import random
import time
import math

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="발표 순서 추첨기",
    page_icon="🎡"
)

# --- 앱 제목 ---
st.title("🎡 발표 순서 추첨 룰렛")
st.markdown("룰렛 애니메이션이 추가된 버전입니다!")

# --- Session State 초기화 ---
if 'total_students' not in st.session_state:
    st.session_state.total_students = 0
if 'remaining_numbers' not in st.session_state:
    st.session_state.remaining_numbers = []
if 'drawn_numbers' not in st.session_state:
    st.session_state.drawn_numbers = []
if 'last_drawn' not in st.session_state:
    st.session_state.last_drawn = None
if 'is_drawing' not in st.session_state:
    st.session_state.is_drawing = False

# --- 룰렛 HTML/CSS 생성 함수 ---
def create_roulette_html(numbers, highlighted_number=None, final_pick=False):
    """동적으로 룰렛 모양의 HTML과 CSS를 생성합니다."""
    # 룰렛의 크기 설정
    wheel_size = 350
    # 번호가 많아지면 폰트 크기를 줄임
    font_size = "20px" if len(numbers) < 15 else "14px"
    
    items_html = ""
    angle_step = 360 / len(numbers)

    for i, num in enumerate(numbers):
        angle = math.radians(i * angle_step - 90) # -90은 12시 방향에서 시작하기 위함
        x = (wheel_size / 2 - 25) * math.cos(angle) + (wheel_size / 2 - 15)
        y = (wheel_size / 2 - 25) * math.sin(angle) + (wheel_size / 2 - 15)
        
        is_highlighted = (num == highlighted_number)
        
        # 하이라이트 스타일
        bg_color = "orange" if is_highlighted and not final_pick else "limegreen" if is_highlighted and final_pick else "white"
        color = "white" if is_highlighted else "black"
        font_weight = "bold" if is_highlighted else "normal"
        border = "2px solid orange" if is_highlighted and not final_pick else "2px solid limegreen" if is_highlighted and final_pick else "1px solid #ccc"

        items_html += f"""
        <div class="number" style="top: {y}px; left: {x}px; background-color: {bg_color}; color: {color}; font-weight: {font_weight}; border: {border}; font-size: {font_size};">
            {num}
        </div>
        """

    # 전체 HTML 구조
    html = f"""
    <style>
        .roulette-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: {wheel_size + 20}px;
        }}
        .roulette-wheel {{
            width: {wheel_size}px;
            height: {wheel_size}px;
            border: 10px solid #333;
            border-radius: 50%;
            position: relative;
            background: #f0f2f6;
            box-shadow: 0 0 20px rgba(0,0,0,0.2);
        }}
        .pointer {{
            width: 0;
            height: 0;
            border-left: 15px solid transparent;
            border-right: 15px solid transparent;
            border-top: 30px solid red;
            position: absolute;
            top: -30px;
            left: calc(50% - 15px);
            z-index: 10;
        }}
        .number {{
            position: absolute;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            justify-content: center;
            align-items: center;
            transition: all 0.1s;
        }}
    </style>
    <div class="roulette-container">
        <div class="roulette-wheel">
            <div class="pointer"></div>
            {items_html}
        </div>
    </div>
    """
    return html

# --- 사이드바: 설정 영역 ---
with st.sidebar:
    st.header("⚙️ 추첨 설정")
    total_input = st.number_input(
        "전체 인원을 입력하세요", min_value=1, 
        value=st.session_state.total_students if st.session_state.total_students > 0 else 10, step=1
    )

    if st.button("설정 및 초기화"):
        st.session_state.total_students = total_input
        st.session_state.remaining_numbers = list(range(1, total_input + 1))
        st.session_state.drawn_numbers = []
        st.session_state.last_drawn = None
        st.session_state.is_drawing = False
        st.success(f"{total_input}명으로 설정이 완료되었습니다!")
        time.sleep(1)
        st.rerun()

# --- 메인 화면 ---
if not st.session_state.remaining_numbers and not st.session_state.drawn_numbers:
    st.info("먼저 사이드바에서 전체 인원을 설정하고 '설정 및 초기화' 버튼을 눌러주세요.")
else:
    # 룰렛을 표시할 공간
    roulette_placeholder = st.empty()
    
    # 마지막으로 뽑힌 번호 또는 기본 룰렛 표시
    if st.session_state.last_drawn and not st.session_state.is_drawing:
        roulette_html = create_roulette_html(st.session_state.remaining_numbers + [st.session_state.last_drawn], highlighted_number=st.session_state.last_drawn, final_pick=True)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: green;'>🎉 {st.session_state.last_drawn}번 당첨! 🎉</h2>", unsafe_allow_html=True)
    else:
        roulette_html = create_roulette_html(st.session_state.remaining_numbers)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)

    st.markdown("---")
    
    # 추첨 버튼
    if st.button("🚀 추첨하기!", type="primary", use_container_width=True, disabled=not st.session_state.remaining_numbers):
        if st.session_state.remaining_numbers:
            st.session_state.is_drawing = True
            
            # 애니메이션 효과
            animation_duration = 20 # 20번 깜빡임
            sleep_time = 0.05 # 깜빡이는 속도
            for i in range(animation_duration):
                temp_pick = random.choice(st.session_state.remaining_numbers)
                roulette_html = create_roulette_html(st.session_state.remaining_numbers, highlighted_number=temp_pick)
                roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
                # 마지막으로 갈수록 느려지게
                if i > animation_duration * 0.8:
                    time.sleep(sleep_time * 3)
                elif i > animation_duration * 0.6:
                    time.sleep(sleep_time * 2)
                else:
                    time.sleep(sleep_time)
            
            # 최종 추첨
            pick = random.choice(st.session_state.remaining_numbers)
            st.session_state.last_drawn = pick
            st.session_state.remaining_numbers.remove(pick)
            st.session_state.drawn_numbers.append(pick)
            st.session_state.is_drawing = False

            # 결과 표시 후 새로고침하여 최종 상태를 보여줌
            st.rerun()
        else:
            st.warning("모든 번호를 추첨했습니다!")

    # --- 결과 표시 영역 ---
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 추첨된 순서")
        if st.session_state.drawn_numbers:
            for i, number in enumerate(st.session_state.drawn_numbers):
                st.markdown(f"**{i+1}번째**: {number}번")
        else:
            st.text("아직 추첨된 번호가 없습니다.")
    
    with col2:
        st.subheader("⏳ 남은 번호")
        if st.session_state.remaining_numbers:
            st.session_state.remaining_numbers.sort()
            for number in st.session_state.remaining_numbers:
                st.markdown(f"  - {number}번")
        else:
            st.text("남은 번호가 없습니다.")
    st.session_state.remaining_numbers = []
if 'drawn_numbers' not in st.session_state:
    st.session_state.drawn_numbers = []
if 'last_drawn' not in st.session_state:
    st.session_state.last_drawn = None


# --- 사이드바: 설정 영역 ---
with st.sidebar:
    st.header("⚙️ 추첨 설정")
    
    # 전체 학생 수 입력
    total_input = st.number_input(
        "전체 인원을 입력하세요", 
        min_value=1, 
        value=st.session_state.total_students if st.session_state.total_students > 0 else 10, # 이전 값 유지 또는 기본값 10
        step=1
    )

    # 설정 및 초기화 버튼
    if st.button("설정 및 초기화"):
        st.session_state.total_students = total_input
        st.session_state.remaining_numbers = list(range(1, total_input + 1))
        st.session_state.drawn_numbers = []
        st.session_state.last_drawn = None
        st.success(f"{total_input}명으로 설정이 완료되었습니다! 추첨을 시작하세요.")
        time.sleep(1) # 메시지 확인 시간
        st.rerun() # 설정 후 화면을 새로고침하여 반영

# --- 메인 화면: 추첨 영역 ---
if not st.session_state.remaining_numbers and not st.session_state.drawn_numbers:
    st.info("먼저 사이드바에서 전체 인원을 설정하고 '설정 및 초기화' 버튼을 눌러주세요.")
else:
    # 추첨 버튼
    if st.button("🚀 추첨하기!", type="primary", use_container_width=True):
        if st.session_state.remaining_numbers:
            # 룰렛 애니메이션 효과 (선택 사항)
            placeholder = st.empty()
            for _ in range(10):
                temp_pick = random.choice(st.session_state.remaining_numbers)
                placeholder.markdown(f"<h1 style='text-align: center; color: orange;'>{temp_pick}</h1>", unsafe_allow_html=True)
                time.sleep(0.1)

            # 최종 추첨
            pick = random.choice(st.session_state.remaining_numbers)
            st.session_state.last_drawn = pick
            
            # 상태 업데이트
            st.session_state.remaining_numbers.remove(pick)
            st.session_state.drawn_numbers.append(pick)
            
            placeholder.markdown(f"<h1 style='text-align: center; color: green;'>🎉 {pick}번! 🎉</h1>", unsafe_allow_html=True)

        else:
            st.warning("모든 번호를 추첨했습니다!")
    
    # 마지막으로 추첨된 번호 표시 (버튼 누르지 않았을 때)
    elif st.session_state.last_drawn:
        st.markdown(f"<h1 style='text-align: center; color: green;'>🎉 {st.session_state.last_drawn}번! 🎉</h1>", unsafe_allow_html=True)

    st.markdown("---")

    # --- 결과 표시 영역 ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🎯 추첨된 순서")
        if st.session_state.drawn_numbers:
            # 순서와 함께 번호를 보기 좋게 표시
            for i, number in enumerate(st.session_state.drawn_numbers):
                st.markdown(f"**{i+1}번째**: {number}번")
        else:
            st.text("아직 추첨된 번호가 없습니다.")
    
    with col2:
        st.subheader("⏳ 남은 번호")
        if st.session_state.remaining_numbers:
            # 남은 번호를 정렬하여 보기 좋게 표시
            st.session_state.remaining_numbers.sort()
            # for 반복문을 사용하여 각 번호를 markdown으로 출력 (★수정된 부분★)
            for number in st.session_state.remaining_numbers:
                st.markdown(f"  - {number}번") # 들여쓰기와 함께 리스트 형태로 표시
        else:
            st.text("남은 번호가 없습니다.")
