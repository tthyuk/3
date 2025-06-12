import streamlit as st
import random
import time
import math # 수학 연산을 위해 math 모듈 임포트

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
    
    # 룰렛의 현재 회전 각도를 저장합니다.
    if 'current_rotation' not in st.session_state:
        st.session_state.current_rotation = 0 # 초기 회전 각도

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
        st.session_state.current_rotation = 0 # 초기화 시 회전 각도 초기화
        st.success(f"✅ 룰렛이 **{st.session_state.max_students}명**의 학생으로 초기화되었습니다. 이제 '룰렛 돌리기' 버튼을 눌러주세요!")
        st.rerun()

    st.markdown("---") # 구분선 추가

    # 현재 남아있는 번호들을 표시합니다.
    st.info(f"**남아있는 번호:** {st.session_state.available_numbers if st.session_state.available_numbers else '없음'}")
    # 추첨된 번호들을 순서대로 표시합니다.
    st.success(f"**추첨된 순서:** {st.session_state.drawn_numbers if st.session_state.drawn_numbers else '아직 추첨된 번호가 없습니다.'}")

    st.markdown("---") # 구분선 추가

    # 룰렛 애니메이션 컨테이너를 위한 placeholder를 생성합니다.
    roulette_placeholder = st.empty()

    # 룰렛을 렌더링하는 함수를 정의합니다.
    # 이 함수는 룰렛의 HTML/CSS와 함께 현재 표시될 숫자를 포함하여 룰렛을 그립니다.
    def render_roulette_visual(numbers, current_rotation, highlighted_number=None):
        # 룰렛 바퀴의 반지름 (CSS px 값)
        wheel_radius_css = 125 # .roulette-wheel width/2
        
        if not numbers or st.session_state.max_students == 0:
            # 학생 수가 0일 경우 메시지 표시
            segment_html = "<div class='roulette-no-numbers'>학생 수를 입력하세요.</div>"
            # 룰렛 바퀴는 회전하지 않고, 메시지만 표시합니다.
            wheel_html = f"<div class='roulette-wheel' style='transform: rotate(0deg);'>{segment_html}</div>"
        else:
            total_segments = st.session_state.max_students # 전체 초기 학생 수 (칸 수 고정)
            segment_angle = 360 / total_segments # 각 칸의 각도
            
            # 시각적 구분을 위한 색상 팔레트
            segment_colors = [
                "#FFD700", "#FF6347", "#6A5ACD", "#32CD32", "#8A2BE2",
                "#FF4500", "#1E90FF", "#DAA520", "#DC143C", "#00CED1",
                "#FF8C00", "#4B0082", "#7FFF00", "#BA55D3", "#F0E68C",
                "#ADD8E6", "#FFA07A", "#90EE90", "#DDA0DD", "#FFE4B5",
                "#87CEEB", "#FFDAB9", "#BDB76B", "#FA8072", "#AFEEEE",
                "#F4A460", "#EE82EE", "#00FA9A", "#FFC0CB", "#6495ED"
            ] # 다양한 색상 추가 (최대 30개)

            segments_html = []
            # 모든 가능한 번호(1부터 max_students까지)를 기준으로 세그먼트를 생성합니다.
            all_possible_numbers = list(range(1, st.session_state.max_students + 1))

            # 세그먼트 (숫자 칸)의 크기 및 룰렛 중앙으로부터의 거리
            segment_width = 80  # 세그먼트의 시각적 너비 (px)
            segment_height = 40 # 세그먼트의 시각적 높이 (px)
            # 숫자가 위치할 반지름 (룰렛 중앙에서 세그먼트 중앙까지의 거리)
            # 룰렛 바퀴 반지름(125px)에서 세그먼트 높이의 절반 정도를 빼서 조정
            number_radial_distance = wheel_radius_css - (segment_height / 2) - 10 # 룰렛 테두리 안쪽으로 배치

            for i, num in enumerate(all_possible_numbers):
                # 각 세그먼트의 중심이 룰렛의 12시 방향(0도)에서 시작하여 시계 방향으로 회전하는 각도
                segment_center_angle = (i * segment_angle) # 0번 인덱스가 0도에 위치

                # CSS `transform: rotate()`는 시계 방향이 양수입니다.
                # `math.cos`와 `math.sin`을 사용할 때 0도는 X축 양의 방향(오른쪽)이므로,
                # 룰렛의 0도를 Y축 양의 방향(위쪽)으로 맞추기 위해 -90도를 보정합니다.
                angle_rad_for_pos = math.radians(segment_center_angle - 90)

                # 룰렛 중심(0,0)을 기준으로 세그먼트 중심의 X, Y 좌표 계산
                x_pos = number_radial_distance * math.cos(angle_rad_for_pos)
                y_pos = number_radial_distance * math.sin(angle_rad_for_pos)

                # 세그먼트의 top-left 좌표 (룰렛 바퀴의 top-left(0,0) 기준)
                # 룰렛 바퀴의 중심은 (wheel_radius_css, wheel_radius_css)
                segment_left = wheel_radius_css + x_pos - (segment_width / 2)
                segment_top = wheel_radius_css + y_pos - (segment_height / 2)

                is_drawn = num in st.session_state.drawn_numbers
                color_index = i % len(segment_colors)
                segment_bg_color = segment_colors[color_index] if not is_drawn else "#D3D3D3" # 뽑힌 번호는 회색 배경
                text_color = "black" if not is_drawn else "#696969" # 뽑힌 번호는 어두운 회색 텍스트
                font_weight = "normal" if not is_drawn else "normal"

                # 룰렛 바퀴의 회전(current_rotation)에 따라 세그먼트도 같이 회전하지만,
                # 세그먼트 안의 숫자는 항상 똑바로 보이도록 세그먼트의 회전 각도에 반대되는 각도로 회전시킵니다.
                content_rotate_angle = -segment_center_angle

                segments_html.append(f"""
                <div class='roulette-segment' style='
                    background-color: {segment_bg_color};
                    left: {segment_left}px;
                    top: {segment_top}px;
                    width: {segment_width}px;
                    height: {segment_height}px;
                    transform: rotate({segment_center_angle}deg); /* 세그먼트 자체를 방사형 위치에 회전 */
                    position: absolute;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 1.2em;
                    color: {text_color};
                    font-weight: {font_weight};
                    border: 1px solid rgba(255,255,255,0.2);
                    box-sizing: border-box;
                    border-radius: 5px; /* 약간 둥근 모서리 */
                    z-index: 50;
                '>
                    <span style="transform: rotate({content_rotate_angle}deg); display: inline-block;">{num}</span>
                </div>
                """)

            # 룰렛 바퀴는 전체 세그먼트들을 포함하며 회전합니다.
            wheel_html = f"<div class='roulette-wheel' style='transform: rotate({current_rotation}deg);'>{ ''.join(segments_html) }</div>"

        # 룰렛 중앙에 현재 표시될 숫자 (애니메이션 중 또는 최종 결과)
        central_display_html = f"""
        <div class='roulette-number-display' style='
            font-size: {("5em" if highlighted_number is not None else "4em")};
            color: {("#FF4500" if highlighted_number is not None else "#333")};
        '>
            {highlighted_number if highlighted_number is not None else st.session_state.roulette_display_number}
        </div>
        """

        # 최종 HTML 마크다운
        roulette_placeholder.markdown(f"""
        <style>
        .roulette-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            width: 350px; /* 룰렛 컨테이너 크기 더 키움 */
            height: 350px; /* 룰렛 컨테이너 크기 더 키움 */
            margin: 30px auto;
            border-radius: 50%;
            background-color: #f0f2f6; /* 배경색 */
            box-shadow: inset 0 0 15px rgba(0,0,0,0.3); /* 그림자 강화 */
            overflow: hidden; /* 내부 요소가 넘치지 않도록 */
        }}

        .roulette-wheel {{
            width: 250px; /* 룰렛 바퀴 크기 키움 */
            height: 250px; /* 룰렛 바퀴 크기 키움 */
            border-radius: 50%;
            border: 15px solid #333; /* 테두리 두께 키움 */
            box-shadow: 0 0 20px rgba(0,0,0,0.6); /* 그림자 강화 */
            position: relative;
            background-color: #eee; /* 기본 휠 배경 */
        }}

        .roulette-pointer {{
            width: 0;
            height: 0;
            border-left: 25px solid transparent;
            border-right: 25px solid transparent;
            border-bottom: 40px solid #ff4b4b; /* Streamlit의 빨간색과 유사 */
            position: absolute;
            top: -20px; /* 룰렛 위에 포인터 위치 조정 */
            left: 50%;
            transform: translateX(-50%);
            z-index: 100; /* 포인터가 최상단에 오도록 */
        }}

        /* 룰렛 중앙에 숫자를 표시하기 위한 스타일 */
        .roulette-number-display {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            z-index: 101; /* 중앙 숫자가 포인터 위에도 오도록 */
            text-align: center;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
        }}

        /* 숫자가 없는 경우 메시지 */
        .roulette-no-numbers {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            color: #555;
            font-size: 1.5em;
            text-align: center;
            padding: 20px;
        }}
        </style>

        <div class="roulette-container">
            <div class="roulette-pointer"></div>
            {wheel_html}
            {central_display_html}
        </div>
        """, unsafe_allow_html=True)

    # 앱 로드 시 또는 초기화 시 룰렛을 초기 상태로 렌더링합니다.
    # 초기 렌더링 시에는 현재 회전 각도를 사용합니다.
    render_roulette_visual(st.session_state.available_numbers, st.session_state.current_rotation)

    # '룰렛 돌리기' 버튼을 생성합니다.
    col1, col2 = st.columns(2) # 버튼을 나란히 배치하기 위해 두 개의 컬럼을 생성합니다.

    with col1:
        if st.button("룰렛 돌리기 🎰", help="남아있는 학생 중 한 명을 무작위로 추첨합니다."):
            if st.session_state.available_numbers:
                st.balloons() # 축하 풍선 효과를 미리 보여줍니다.

                # 최종 결과 처리
                drawn_number = random.choice(st.session_state.available_numbers)
                
                # 룰렛 스핀 애니메이션 (전체 룰렛 회전)
                spin_duration = 4 # 룰렛이 회전하는 시간 (초)
                num_frames = 60 # 애니메이션 프레임 수
                sleep_per_frame = spin_duration / num_frames # 각 프레임 당 지연 시간

                # 룰렛 회전 시작 각도
                start_rotation = st.session_state.current_rotation
                # 무작위로 3~5바퀴 더 돌리기
                random_extra_spins = random.randint(3, 5)

                # 최종 각도 계산: 뽑힌 번호가 포인터(상단 중앙)에 오도록
                total_segments_for_calc = st.session_state.max_students # 전체 초기 번호 수 (각도 계산용)
                segment_angle_val = 360 / total_segments_for_calc if total_segments_for_calc > 0 else 0

                # 뽑힌 번호의 중심이 0도(상단 포인터)에 오도록 할 최종 각도 계산
                # (drawn_number - 1)은 0부터 시작하는 인덱스
                # target_center_angle: 뽑힌 번호의 세그먼트 중심이 룰렛의 상단(0도)에서 시계 방향으로 얼마나 떨어져 있는지
                target_center_angle = ((drawn_number - 1) * segment_angle_val + (segment_angle_val / 2)) % 360
                
                # 룰렛을 회전시켜 target_center_angle이 0도에 오도록 할 목표 회전 각도 (0-360 범위)
                # CSS rotate는 시계 방향이 양수이므로, 0도에 위치시키려면 (360 - 현재 각도)만큼 더 회전해야 합니다.
                target_relative_rotation = (360 - target_center_angle) % 360

                # 최종 총 회전 각도 계산
                # 현재 회전 각도에서 시작 + 무작위 추가 바퀴 + 목표 위치로의 정렬 회전
                # `start_rotation % 360`은 현재 룰렛의 0-360도 범위 내 각도입니다.
                # `needed_rotation_for_alignment`는 현재 위치에서 목표 위치까지 추가로 필요한 각도 (0-360)
                needed_rotation_for_alignment = (target_relative_rotation - (start_rotation % 360) + 360) % 360

                final_rotation = start_rotation + (random_extra_spins * 360) + needed_rotation_for_alignment

                with st.spinner(f'룰렛이 힘차게 돌아가는 중... 잠시 기다려주세요!'):
                    for i in range(num_frames):
                        progress = (i + 1) / num_frames
                        # Cubic ease-out for a smooth deceleration (부드러운 감속을 위한 Cubic ease-out)
                        eased_progress = 1 - (1 - progress)**3
                        
                        # 현재 프레임의 회전 각도 계산
                        current_spin_rotation = start_rotation + (final_rotation - start_rotation) * eased_progress

                        # 애니메이션 중 중앙에 표시될 임시 번호 (빠르게 변하는 효과)
                        if st.session_state.available_numbers:
                            display_num = random.choice(st.session_state.available_numbers)
                        else:
                            display_num = "---" # 뽑을 번호가 없으면 --- 표시

                        # 룰렛 시각화 업데이트 (회전 각도와 임시 번호 전달)
                        render_roulette_visual(st.session_state.available_numbers, current_spin_rotation, display_num)
                        time.sleep(sleep_per_frame)

                # 최종 당첨 번호를 룰렛 중앙에 표시하고 색상 및 크기를 고정합니다.
                render_roulette_visual(st.session_state.available_numbers, final_rotation, drawn_number)
                st.session_state.current_rotation = final_rotation # 다음 룰렛을 위해 최종 각도 저장

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
            st.session_state.current_rotation = 0 # 초기화 시 회전 각도 초기화
            st.info("룰렛이 초기화되었습니다.")
            render_roulette_visual(st.session_state.available_numbers, st.session_state.current_rotation) # 초기 상태 룰렛 렌더링
            st.rerun()

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
