import streamlit as st
import random
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import time
import math

# 페이지 설정
st.set_page_config(
    page_title="학생 발표 순서 추첨 룰렛",
    page_icon="🎲",
    layout="wide"
)

# 세션 상태 초기화
if 'excluded_numbers' not in st.session_state:
    st.session_state.excluded_numbers = []
if 'draw_history' not in st.session_state:
    st.session_state.draw_history = []
if 'total_numbers' not in st.session_state:
    st.session_state.total_numbers = 0
if 'selected_number' not in st.session_state:
    st.session_state.selected_number = None

def create_roulette_chart(numbers, selected_number=None, rotation_angle=0):
    """룰렛 차트 생성 (회전 각도 포함)"""
    if not numbers:
        return None
    
    # 색상 생성
    colors = px.colors.qualitative.Set3
    
    # 선택된 번호가 있을 때 하이라이트
    chart_colors = []
    for i, num in enumerate(numbers):
        if selected_number and num == selected_number:
            chart_colors.append('#FF6B6B')  # 빨간색으로 하이라이트
        else:
            chart_colors.append(colors[i % len(colors)])
    
    fig = go.Figure(data=[go.Pie(
        labels=[f"번호 {num}" for num in numbers],
        values=[1] * len(numbers),
        hole=0.4,
        marker=dict(colors=chart_colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='label',
        textfont_size=12,
        hovertemplate='<b>%{label}</b><extra></extra>',
        rotation=rotation_angle  # 회전 각도 적용
    )])
    
    fig.update_layout(
        title=dict(
            text="🎲 발표 순서 추첨 룰렛",
            x=0.5,
            font=dict(size=20)
        ),
        showlegend=False,
        height=500,
        margin=dict(t=100, b=50, l=50, r=50)
    )
    
    return fig

def draw_number(available_numbers):
    """번호 추첨 함수"""
    if not available_numbers:
        return None
    
    # 최종 선택
    selected = random.choice(available_numbers)
    return selected

# 메인 UI
st.title("🎲 학생 발표 순서 추첨 룰렛")
st.markdown("---")

# 사이드바 설정
with st.sidebar:
    st.header("⚙️ 설정")
    
    # 학생 수 입력
    total_students = st.number_input(
        "전체 학생 수를 입력하세요:",
        min_value=1,
        max_value=100,
        value=30,
        step=1
    )
    
    # 설정 적용 버튼
    if st.button("설정 적용", type="primary"):
        st.session_state.total_numbers = total_students
        st.session_state.excluded_numbers = []
        st.session_state.draw_history = []
        st.session_state.selected_number = None
        st.success(f"총 {total_students}명으로 설정되었습니다!")
        st.rerun()
    
    st.markdown("---")
    
    # 초기화 버튼
    if st.button("🔄 전체 초기화", type="secondary"):
        st.session_state.excluded_numbers = []
        st.session_state.draw_history = []
        st.session_state.selected_number = None
        st.success("초기화되었습니다!")
        st.rerun()

# 메인 컨텐츠
col1, col2 = st.columns([2, 1])

with col1:
    if st.session_state.total_numbers > 0:
        # 현재 사용 가능한 번호들
        available_numbers = [i for i in range(1, st.session_state.total_numbers + 1) 
                           if i not in st.session_state.excluded_numbers]
        
        if available_numbers:
            st.subheader(f"현재 추첨 가능한 번호: {len(available_numbers)}개")
            
            # 룰렛 차트 표시용 컨테이너
            chart_container = st.container()
            
            with chart_container:
                # 룰렛 차트 표시
                if st.session_state.selected_number:
                    # 선택된 번호가 있을 때
                    fig = create_roulette_chart(available_numbers, st.session_state.selected_number)
                    st.plotly_chart(fig, use_container_width=True, key="static_chart")
                else:
                    # 일반 상태
                    fig = create_roulette_chart(available_numbers)
                    st.plotly_chart(fig, use_container_width=True, key="static_chart")
            
            # 추첨 버튼
            if st.button("🎯 룰렛 돌리기!", type="primary", use_container_width=True):
                # 기존 차트 숨기기
                chart_container.empty()
                
                # 애니메이션용 새 컨테이너
                animation_container = st.container()
                
                with animation_container:
                    st.info("🎲 룰렛이 돌아가고 있습니다...")
                    
                    # 룰렛 회전 애니메이션
                    chart_placeholder = st.empty()
                    
                    # 회전 애니메이션 (점진적으로 느려지는 효과)
                    rotation_speeds = [30, 25, 20, 15, 12, 10, 8, 6, 4, 3, 2, 1]
                    current_angle = 0
                    
                    for speed in rotation_speeds:
                        for _ in range(5):  # 각 속도마다 5번 회전
                            current_angle += speed
                            if current_angle >= 360:
                                current_angle -= 360
                            
                            # 현재 각도에서 가장 가까운 번호 계산
                            segment_angle = 360 / len(available_numbers)
                            highlighted_index = int((360 - current_angle) / segment_angle) % len(available_numbers)
                            temp_highlighted = available_numbers[highlighted_index]
                            
                            temp_fig = create_roulette_chart(available_numbers, temp_highlighted, current_angle)
                            chart_placeholder.plotly_chart(temp_fig, use_container_width=True)
                            time.sleep(0.1)
                    
                    # 최종 선택 (추가 몇 번 더 천천히 돌기)
                    for _ in range(8):
                        current_angle += 1
                        if current_angle >= 360:
                            current_angle -= 360
                        
                        segment_angle = 360 / len(available_numbers)
                        highlighted_index = int((360 - current_angle) / segment_angle) % len(available_numbers)
                        temp_highlighted = available_numbers[highlighted_index]
                        
                        temp_fig = create_roulette_chart(available_numbers, temp_highlighted, current_angle)
                        chart_placeholder.plotly_chart(temp_fig, use_container_width=True)
                        time.sleep(0.2)
                    
                    # 최종 선택된 번호 결정
                    final_angle = current_angle
                    segment_angle = 360 / len(available_numbers)
                    selected_index = int((360 - final_angle) / segment_angle) % len(available_numbers)
                    selected_number = available_numbers[selected_index]
                    
                    # 세션 상태 업데이트
                    st.session_state.selected_number = selected_number
                    st.session_state.excluded_numbers.append(selected_number)
                    st.session_state.draw_history.append(selected_number)
                    
                    # 최종 결과 표시
                    final_fig = create_roulette_chart(available_numbers, selected_number, final_angle)
                    chart_placeholder.plotly_chart(final_fig, use_container_width=True)
                    
                    # 결과 메시지
                    st.success(f"🎉 선택된 번호: **{selected_number}번**")
                    st.balloons()
                    
                    # 잠시 후 페이지 새로고침
                    time.sleep(2)
                    st.rerun()
        else:
            st.info("🎊 모든 학생이 발표를 완료했습니다!")
            st.success("수고하셨습니다!")
    else:
        st.info("👈 사이드바에서 전체 학생 수를 설정해주세요.")

with col2:
    st.subheader("📊 추첨 현황")
    
    if st.session_state.total_numbers > 0:
        # 진행률 표시
        progress = len(st.session_state.excluded_numbers) / st.session_state.total_numbers
        st.progress(progress)
        st.write(f"진행률: {len(st.session_state.excluded_numbers)}/{st.session_state.total_numbers} ({progress*100:.1f}%)")
        
        # 추첨 기록
        if st.session_state.draw_history:
            st.subheader("🏆 발표 순서")
            for i, number in enumerate(st.session_state.draw_history, 1):
                if i == len(st.session_state.draw_history) and st.session_state.selected_number:
                    st.write(f"**{i}순: {number}번** ⭐")
                else:
                    st.write(f"{i}순: {number}번")
        
        # 남은 번호 표시
        remaining = [i for i in range(1, st.session_state.total_numbers + 1) 
                    if i not in st.session_state.excluded_numbers]
        
        if remaining:
            st.subheader("⏰ 남은 번호")
            remaining_str = ", ".join(map(str, remaining))
            st.write(remaining_str)
    
    # 통계 정보
    if st.session_state.draw_history:
        st.subheader("📈 통계")
        df = pd.DataFrame({
            '순서': range(1, len(st.session_state.draw_history) + 1),
            '번호': st.session_state.draw_history
        })
        st.dataframe(df, use_container_width=True)

# 하단 정보
st.markdown("---")
st.markdown("""
### 사용법
1. **사이드바**에서 전체 학생 수를 입력하고 '설정 적용' 버튼을 클릭하세요.
2. **'룰렛 돌리기!'** 버튼을 클릭하여 번호를 추첨하세요.
3. 선택된 번호는 자동으로 제외되며, 발표 순서가 기록됩니다.
4. 모든 학생의 발표가 끝나면 '전체 초기화' 버튼으로 새로 시작할 수 있습니다.
""")

st.markdown("""
<div style='text-align: center; color: #666; margin-top: 2rem;'>
    Made with ❤️ using Streamlit
</div>
""", unsafe_allow_html=True)
