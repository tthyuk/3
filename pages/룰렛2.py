import streamlit as st
import random
import time
import math

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="발표 순서 추첨기",
    page_icon="🎡"
)

# --- 앱 제목 및 부제 수정 ---
st.title("🎡 발표 순서 추첨 룰렛")
st.markdown("발표 순서를 공정하고 재미있게 추첨해 보세요!") # ★★★ 사용자 친화적 문구로 변경 ★★★

# --- Session State 초기화 ---
if 'total_students' not in st.session_state: st.session_state.total_students = 0
if 'remaining_numbers' not in st.session_state: st.session_state.remaining_numbers = []
if 'drawn_numbers' not in st.session_state: st.session_state.drawn_numbers = []
if 'last_drawn' not in st.session_state: st.session_state.last_drawn = None
if 'is_drawing' not in st.session_state: st.session_state.is_drawing = False

# --- 룰렛 HTML/CSS 생성 함수 (시각적 강조 추가) ---
def create_roulette_html(numbers, highlighted_number=None, final_pick=False, top_number=None):
    """최종 당첨 시 다른 번호들을 흐리게 처리하는 기능 추가"""
    
    WHEEL_SIZE, NUMBER_DIV_SIZE, PADDING_FROM_EDGE = 350, 32, 35
    font_size = "14px" if len(numbers) >= 18 else "16px"
    items_html, angle_step = "", 360 / len(numbers) if len(numbers) > 0 else 0
    path_radius, center_offset = (WHEEL_SIZE / 2) - PADDING_FROM_EDGE, (WHEEL_SIZE / 2) - (NUMBER_DIV_SIZE / 2)
    offset_index = numbers.index(top_number) if top_number and top_number in numbers else 0

    for i, num in enumerate(numbers):
        angle = math.radians((i - offset_index) * angle_step - 90)
        x, y = path_radius * math.cos(angle) + center_offset, path_radius * math.sin(angle) + center_offset
        
        is_highlighted = (num == highlighted_number)
        
        # ★★★ 당첨 시 다른 번호 흐리게 처리하는 로직 ★★★
        opacity = 1.0
        if final_pick and not is_highlighted:
            opacity = 0.3 # 당첨되지 않은 번호는 흐리게
        
        bg_color = "orange" if is_highlighted and not final_pick else "limegreen" if is_highlighted and final_pick else "white"
        color = "white" if is_highlighted else "black"
        font_weight = "bold" if is_highlighted else "normal"
        border = "3px solid orange" if is_highlighted and not final_pick else "3px solid limegreen" if is_highlighted and final_pick else "1px solid #ccc"

        items_html += f'<div class="number" style="width: {NUMBER_DIV_SIZE}px; height: {NUMBER_DIV_SIZE}px; top: {y}px; left: {x}px; background-color: {bg_color}; color: {color}; font-weight: {font_weight}; border: {border}; font-size: {font_size}; opacity: {opacity};">{num}</div>'

    html = f"""
    <style>
        .roulette-container {{ display: flex; justify-content: center; align-items: center; height: {WHEEL_SIZE + 20}px; }}
        .roulette-wheel {{ width: {WHEEL_SIZE}px; height: {WHEEL_SIZE}px; border: 10px solid #333; border-radius: 50%; position: relative; background: #f0f2f6; box-shadow: 0 0 20px rgba(0,0,0,0.2); }}
        .pointer {{ width: 0; height: 0; border-left: 15px solid transparent; border-right: 15px solid transparent; border-top: 30px solid red; position: absolute; top: -30px; left: calc(50% - 15px); z-index: 10; }}
        .number {{ position: absolute; border-radius: 50%; display: flex; justify-content: center; align-items: center; transition: opacity 0.5s; }}
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
        st.session_state.drawn_numbers, st.session_state.last_drawn, st.session_state.is_drawing = [], None, False
        st.success(f"{total_input}명으로 설정 완료!")
        time.sleep(1)
        st.rerun()

# --- 메인 화면 ---
if not st.session_state.remaining_numbers and not st.session_state.drawn_numbers:
    st.info("사이드바에서 전체 인원을 설정하고 '설정 및 초기화' 버튼을 눌러주세요.")
else:
    roulette_placeholder = st.empty()
    
    if st.session_state.last_drawn and not st.session_state.is_drawing:
        display_numbers = sorted(st.session_state.remaining_numbers + [st.session_state.last_drawn])
        roulette_html = create_roulette_html(display_numbers, highlighted_number=st.session_state.last_drawn, final_pick=True, top_number=st.session_state.last_drawn)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
        # ★★★ 당첨 메시지 스타일 업그레이드 ★★★
        st.markdown(f"<h1 style='text-align: center; color: green;'>🎉 {st.session_state.last_drawn}번 당첨! 🎉</h1>", unsafe_allow_html=True)
    else:
        display_numbers = sorted(st.session_state.remaining_numbers)
        roulette_html = create_roulette_html(display_numbers)
        roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)

    st.markdown("---")
    
    if st.button("🚀 추첨하기!", type="primary", use_container_width=True, disabled=not st.session_state.remaining_numbers):
        if st.session_state.remaining_numbers:
            st.session_state.is_drawing = True
            animation_duration, sleep_time = 20, 0.05
            display_numbers = sorted(st.session_state.remaining_numbers)
            
            for i in range(animation_duration):
                temp_pick = random.choice(display_numbers)
                roulette_html = create_roulette_html(display_numbers, highlighted_number=temp_pick, top_number=temp_pick)
                roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
                if i > animation_duration*0.8: time.sleep(sleep_time*3)
                elif i > animation_duration*0.6: time.sleep(sleep_time*2)
                else: time.sleep(sleep_time)
            
            pick = random.choice(display_numbers)
            st.session_state.last_drawn, st.session_state.is_drawing = pick, False
            st.session_state.remaining_numbers.remove(pick)
            st.session_state.drawn_numbers.append(pick)
            st.rerun()
        else: st.warning("모든 번호를 추첨했습니다!")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🎯 추첨된 순서")
        if st.session_state.drawn_numbers:
            for i, number in enumerate(st.session_state.drawn_numbers): st.markdown(f"**{i+1}번째**: {number}번")
        else: st.text("아직 추첨된 번호가 없습니다.")
    
    with col2:
        st.subheader("⏳ 남은 번호")
        if st.session_state.remaining_numbers:
            st.session_state.remaining_numbers.sort()
            for number in st.session_state.remaining_numbers: st.markdown(f"  - {number}번")
        else: st.text("남은 번호가 없습니다.")
