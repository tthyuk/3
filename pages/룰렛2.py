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
if 'remaining_numbers' not in st.session_state:
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
            st.write(st.session_state.remaining_numbers)
        else:
            st.text("남은 번호가 없습니다.")
