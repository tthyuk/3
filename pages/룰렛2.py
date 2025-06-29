import streamlit as st
import random
import time
import math

# --- 페이지 기본 설정 ---
st.set_page_config(
    page_title="발표 순서 추첨기",
    page_icon="🎨",
    layout="wide"
)

# --- 앱 제목 ---
st.title("🎨 컬러 룰렛으로 순서 추첨하기")
st.markdown("알록달록한 룰렛으로 발표 순서를 재미있게 정해보세요!")
st.write("---")

# --- Session State 초기화 ---
if 'total_students' not in st.session_state: st.session_state.total_students = 0
if 'remaining_numbers' not in st.session_state: st.session_state.remaining_numbers = []
if 'drawn_numbers' not in st.session_state: st.session_state.drawn_numbers = []
if 'last_drawn' not in st.session_state: st.session_state.last_drawn = None
if 'is_drawing' not in st.session_state: st.session_state.is_drawing = False

# --- 컬러 룰렛 HTML/CSS 생성 함수 (완전 수정) ---
def create_roulette_html(numbers, top_number=None):
    """화살표, 숫자 위치를 완벽하게 수정한 최종 룰렛을 생성합니다."""
    
    WHEEL_SIZE = 380
    CENTER_CIRCLE_RATIO = 0.35 # 안쪽 흰 원의 비율
    
    colors = ["#caffbf", "#fdffb6", "#ffd6a5", "#ffadad", "#bdb2ff", "#a0c4ff", "#9bf6ff"]
    
    gradient_parts, label_parts = [], []
    num_items = len(numbers)
    angle_step = 360 / num_items if num_items > 0 else 0

    rotation_angle = 0
    if top_number and top_number in numbers:
        idx = numbers.index(top_number)
        rotation_angle = - (idx * angle_step + angle_step / 2) - 90

    for i, num in enumerate(numbers):
        color = colors[i % len(colors)]
        start_angle, end_angle = i * angle_step, (i + 1) * angle_step
        gradient_parts.append(f"{color} {start_angle}deg {end_angle}deg")
        
        # ★★★★★ 숫자 위치를 정확히 중앙으로 계산하는 로직 ★★★★★
        outer_radius = WHEEL_SIZE / 2
        inner_radius = (WHEEL_SIZE * CENTER_CIRCLE_RATIO) / 2
        path_radius = (outer_radius + inner_radius) / 2 # 색상 칸의 중간 반지름
        
        label_angle_deg = start_angle + angle_step / 2
        label_angle_rad = math.radians(label_angle_deg)
        x = path_radius * math.cos(label_angle_rad) + (WHEEL_SIZE / 2)
        y = path_radius * math.sin(label_angle_rad) + (WHEEL_SIZE / 2)
        
        is_highlighted = (num == top_number)
        font_weight = "bold" if is_highlighted else "normal"
        font_size = "1.5em" if is_highlighted else "1.3em"
        counter_rotation = -rotation_angle
        transform_style = f"translate(-50%, -50%) rotate({counter_rotation}deg)"
        
        label_parts.append(f'<div class="label" style="top: {y}px; left: {x}px; font-weight: {font_weight}; font-size:{font_size}; transform: {transform_style};">{num}</div>')
    
    gradient_str, labels_str = ", ".join(gradient_parts), "".join(label_parts)
        
    html = f"""
    <style>
        .roulette-container {{ display: flex; justify-content: center; align-items: center; height: {WHEEL_SIZE + 40}px; position: relative; }}
        .roulette-wheel {{ 
            width: {WHEEL_SIZE}px; height: {WHEEL_SIZE}px;
            border-radius: 50%; background: conic-gradient({gradient_str});
            transition: transform 0.2s ease-out; transform: rotate({rotation_angle}deg);
            box-shadow: 0 0 20px rgba(0,0,0,0.2); position: relative;
        }}
        .wheel-center {{ 
            width: {CENTER_CIRCLE_RATIO * 100}%; height: {CENTER_CIRCLE_RATIO * 100}%; 
            background: white; border-radius: 50%; position: absolute;
            top: 50%; left: 50%; transform: translate(-50%, -50%);
            border: 5px solid #fff; box-shadow: inset 0 0 10px rgba(0,0,0,0.1);
        }}
        /* ★★★★★ 화살표 방향 및 위치 수정 ★★★★★ */
        .pointer {{ 
            width: 0; height: 0; 
            border-left: 15px solid transparent; border-right: 15px solid transparent;
            border-top: 30px solid red; /* 위쪽 테두리로 아래를 향하는 삼각형 생성 */
            position: absolute; top: -30px; left: calc(50% - 15px); z-index: 10;
        }}
        .label {{ position: absolute; color: #333; text-shadow: 0 0 3px white; transition: font-size 0.2s, font-weight 0.2s; }}
    </style>
    <div class="roulette-container">
        <div class="pointer"></div>
        <div class="roulette-wheel">
            <div class="wheel-center"></div>
            {labels_str}
        </div>
    </div>
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

# --- 메인 레이아웃 분할 ---
main_col, result_col = st.columns([2, 1])

# --- 왼쪽 메인 화면 (룰렛) ---
with main_col:
    if not st.session_state.remaining_numbers and not st.session_state.drawn_numbers:
        st.info("먼저 사이드바에서 전체 인원을 설정하고 '설정 및 초기화' 버튼을 눌러주세요.")
    else:
        roulette_placeholder = st.empty()
        
        if st.session_state.last_drawn and not st.session_state.is_drawing:
            display_numbers = sorted(st.session_state.remaining_numbers + [st.session_state.last_drawn])
            roulette_html = create_roulette_html(display_numbers, top_number=st.session_state.last_drawn)
            roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
            st.markdown(f"<h1 style='text-align: center; color: green;'>🎉 {st.session_state.last_drawn}번 당첨! 🎉</h1>", unsafe_allow_html=True)
        else:
            display_numbers = sorted(st.session_state.remaining_numbers)
            roulette_html = create_roulette_html(display_numbers, top_number=display_numbers[0] if display_numbers else None)
            roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)

        st.markdown("---")
        
        if st.button("🚀 추첨하기!", type="primary", use_container_width=True, disabled=not st.session_state.remaining_numbers):
            if st.session_state.remaining_numbers:
                st.session_state.is_drawing = True
                animation_duration, sleep_time = 25, 0.05
                display_numbers = sorted(st.session_state.remaining_numbers)
                
                for i in range(animation_duration):
                    temp_pick = random.choice(display_numbers)
                    roulette_html = create_roulette_html(display_numbers, top_number=temp_pick)
                    roulette_placeholder.markdown(roulette_html, unsafe_allow_html=True)
                    if i > animation_duration*0.85: time.sleep(sleep_time*3)
                    elif i > animation_duration*0.6: time.sleep(sleep_time*2)
                    else: time.sleep(sleep_time)
                
                pick = random.choice(display_numbers)
                st.session_state.last_drawn, st.session_state.is_drawing = pick, False
                st.session_state.remaining_numbers.remove(pick)
                st.session_state.drawn_numbers.append(pick)
                st.rerun()
            else: st.warning("모든 번호를 추첨했습니다!")

# --- 오른쪽 결과 표시 화면 ---
with result_col:
    st.subheader("🎯 추첨된 순서")
    if st.session_state.drawn_numbers:
        with st.container(height=200):
            for i, number in enumerate(st.session_state.drawn_numbers): st.markdown(f"**{i+1}번째**: {number}번")
    else: st.text("아직 추첨된 번호가 없습니다.")

    st.write("---")
    
    st.subheader("⏳ 남은 번호")
    if st.session_state.remaining_numbers:
        with st.container(height=250):
            st.session_state.remaining_numbers.sort()
            for number in st.session_state.remaining_numbers: st.markdown(f"  - {number}번")
    else: st.text("남은 번호가 없습니다.")
