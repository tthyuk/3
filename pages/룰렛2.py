import streamlit as st
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
st.markdown("룰렛이 회전하여 화살표에 당첨 번호를 맞춥니다!")

# --- Session State 초기화 ---
if 'total_students' not in st.session_state: st.session_state.total_students = 0
if 'remaining_numbers' not in st.session_state: st.session_state.remaining_numbers = []
if 'drawn_numbers' not in st.session_state: st.session_state.drawn_numbers = []
if 'last_drawn' not in st.session_state: st.session_state.last_drawn = None
if 'is_drawing' not in st.session_state: st.session_state.is_drawing = False

# --- 룰렛 HTML/CSS 생성 함수 (회전 기능 추가) ---
def create_roulette_html(numbers, highlighted_number=None, final_pick=False, top_number=None):
    """
    룰렛 HTML/CSS를 생성합니다.
    top_number를 기준으로 룰렛을 회전시킵니다.
    """
    wheel_size = 350
    if not numbers: font_size = "20px"
    elif len(numbers) < 15: font_size = "20px"
    else: font_size = "14px"
    
    items_html = ""
    angle_step = 360 / len(numbers) if len(numbers) > 0 else 0

    # ★★★★★ 회전 로직의 핵심 ★★★★★
    # top_number가 리스트에서 몇 번째에 있는지 찾아 오프셋을 계산합니다.
    offset_index = 0
    if top_number and top_number in numbers:
        offset_index = numbers.index(top_number)

    for i, num in enumerate(numbers):
        # 각 번호의 각도를 오프셋만큼 보정하여 회전 효과를 줍니다.
        angle = math.radians((i - offset_index) * angle_step - 90)
        x = (wheel_size / 2 - 25) * math.cos(angle) + (wheel_size / 2 - 15)
        y = (wheel_size / 2 - 25) * math.sin(angle) + (wheel_size / 2 - 15)
        
        is_highlighted = (num == highlighted_number)
        bg_color = "orange" if is_highlighted and not final_pick else "limegreen" if is_highlighted and final_pick else "white"
        color = "white" if is_highlighted else "black"
        font_weight = "bold" if is_highlighted else "normal"
        border = "3px solid orange" if is_highlighted and not final_pick else "3px solid limegreen" if is_highlighted and final_pick else "1px solid #ccc"

        items_html += f'<div class="number" style="top: {y}px; left: {x}px; background-color: {bg_color}; color: {color}; font-weight: {font_weight}; border: {border}; font-size: {font_size};">{num}</div>'

    html = f"""
    <style>
        .roulette-container {{ display: flex; justify-content: center; align-items: center; height: {wheel_size + 20}px; }}
        .roulette-wheel {{ width: {wheel_size}px; height: {wheel_size}px; border: 10px solid #333; border-radius: 50%; position: relative; background: #f0f2f6; box-shadow: 0 0 20px rgba(0,0,0,0.2); transition: transform 0.2s ease-out; }}
        .pointer {{ width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid red; position: absolute; top: -30px; left: calc(50% - 15px); z-index: 10; }}
        .number {{ position: absolute; width: 30px; height: 30px; border-radius: 50%; display: flex; justify-content: center; align-items: center; }}
    </style>
    <div class="roulette-container"><div class="roulette-wheel"><div class="pointer"></div>{items_html}</div></div>
    """
    return html

# --- 사이드바 ---
with st.sidebar:
    st.header("⚙️ 추첨 설정")
    total_input = st.number_input("전체 인원을 입력하세요", min_value=1, value=st.session_state.total_students if st.session_state.total_students > 0 else 10, step=1)
    if st.button("설정 및 초기화"):
        st.session_state.total_students = total_input
        st.session_state.remaining_numbers = list(range(1, total_input + 1))
        st.session_state.drawn_numbers = []
        st.session_state.last_drawn = None
        st.session_state.is_drawing = False
        st.success(f"{total_input}명으로 설정 완료!")
        time.sleep(1)
        st.rerun()

# --- 메인 화면 ---
if not st.session_state.remaining_numbers and not st.session_state.drawn_numbers:
    st.info("사이드바에서 전체 인원을 설정하고 '설정 및 초기화' 버튼을 눌러주세요.")
else:
    roulette_placeholder = st.empty()
    
    if st.session_state.last_drawn and not st.session_state.is_drawing:
        display_numbers = st.session_state.remaining_numbers + [st.session_state.last_drawn]
        display_numbers.sort()
        # 최종 당첨 번호를 top_number로 전달하여 회전
        roulette_html = create_roulette_html(display_numbers, highlighted_number=st.session_state.last_drawn, final_pick=True, top_number=st.session_state.last_drawn)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
        st.markdown(f"<h2 style='text-align: center; color: green;'>🎉 {st.session_state.last_drawn}번 당첨! 🎉</h2>", unsafe_allow_html=True)
    else:
        # 초기 상태에서는 회전하지 않음
        display_numbers = sorted(st.session_state.remaining_numbers)
        roulette_html = create_roulette_html(display_numbers)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)

    st.markdown("---")
    
    if st.button("🚀 추첨하기!", type="primary", use_container_width=True, disabled=not st.session_state.remaining_numbers):
        if st.session_state.remaining_numbers:
            st.session_state.is_drawing = True
            
            animation_duration = 20
            sleep_time = 0.05
            display_numbers = sorted(st.session_state.remaining_numbers)
            
            for i in range(animation_duration):
                temp_pick = random.choice(display_numbers)
                # 애니메이션 중에도 temp_pick을 top_number로 전달하여 회전 효과
                roulette_html = create_roulette_html(display_numbers, highlighted_number=temp_pick, top_number=temp_pick)
                roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
                
                if i > animation_duration * 0.8: time.sleep(sleep_time * 3)
                elif i > animation_duration * 0.6: time.sleep(sleep_time * 2)
                else: time.sleep(sleep_time)
            
            pick = random.choice(display_numbers)
            st.session_state.last_drawn = pick
            st.session_state.remaining_numbers.remove(pick)
            st.session_state.drawn_numbers.append(pick)
            st.session_state.is_drawing = False
            st.rerun()
        else:
            st.warning("모든 번호를 추첨했습니다!")

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
