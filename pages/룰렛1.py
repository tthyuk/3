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

def create_roulette_chart(numbers, selected_number=None):
    """룰렛 차트 생성"""
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
        hovertemplate='<b>%{label}</b><extra></extra>'
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
            
            # 룰렛 차트 표시
            if st.session_state.selected_number:
                # 선택된 번호가 있을 때
                fig = create_roulette_chart(available_numbers, st.session_state.selected_number)
                st.plotly_chart(fig, use_container_width=True)
            else:
                # 일반 상태
                fig = create_roulette_chart(available_numbers)
                st.plotly_chart(fig, use_container_width=True)
            
            # 추첨 버튼
            if st.button("🎯 룰렛 돌리기!", type="primary", use_container_width=True):
                # 애니메이션 효과를 위한 임시 컨테이너
                with st.container():
                    animation_text = st.empty()
                    animation_chart = st.empty()
                    
                    # 애니메이션 텍스트 효과
                    animation_messages = [
                        "🎲 룰렛이 돌아가고 있습니다...",
                        "🌟 번호를 선택하고 있습니다...",
                        "⭐ 거의 다 됐습니다...",
                        "🎯 결과가 나왔습니다!"
                    ]
                    
                    for i, message in enumerate(animation_messages):
                        animation_text.info(message)
                        
                        # 각 단계마다 다른 번호들을 임시로 하이라이트
                        for j in range(2):
                            temp_number = random.choice(available_numbers)
                            temp_fig = create_roulette_chart(available_numbers, temp_number)
                            animation_chart.plotly_chart(temp_fig, use_container_width=True)
                            time.sleep(0.3)
                    
                    # 최종 선택
                    selected_number = draw_number(available_numbers)
                    
                    if selected_number:
                        # 세션 상태 업데이트
                        st.session_state.selected_number = selected_number
                        st.session_state.excluded_numbers.append(selected_number)
                        st.session_state.draw_history.append(selected_number)
                        
                        # 최종 결과 표시
                        final_fig = create_roulette_chart(available_numbers, selected_number)
                        animation_chart.plotly_chart(final_fig, use_container_width=True)
                        animation_text.empty()
                        
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
