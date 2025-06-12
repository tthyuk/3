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

    # 룰렛의 현재 회전 각도를 저장합니다.
    if 'current_rotation' not in st.session_state:
        st.session_state.current_rotation = 0 # 초기 회전 각도

    # 총 학생 수를 입력받는 숫자 입력 필드를 생성합니다.
    # StreamlitDuplicateElementId 오류 방지를 위해 'key'를 추가합니다.
    max_students_input = st.number_input(
        "총 학생 수를 입력하세요:",
        min_value=1,
        value=st.session_state.max_students,
        step=1,
        help="발표에 참여할 학생의 총 인원수를 입력하세요.",
        key='max_students_input_key' # 고유한 key 추가
    )

    # 입력된 학생 수가 이전과 다르면 룰렛을 초기화합니다.
    if max_students_input != st.session_state.max_students:
        st.session_state.max_students = max_students_input
        st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        st.session_state.drawn_numbers = []
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
    def render_roulette_visual(current_available_numbers, current_rotation, drawn_number_display=None):
        # 룰렛 바퀴의 반지름 (CSS px 값)
        wheel_radius_css = 125 # .roulette-wheel width/2
        container_size = 350 # .roulette-container width/height

        if not current_available_numbers:
            segment_html = "<div class='roulette-no-numbers'>추첨할 번호가 없습니다. 학생 수를 입력하거나 룰렛을 초기화하세요.</div>"
            wheel_html = f"<div class='roulette-wheel' style='transform: rotate(0deg);'>{segment_html}</div>"
        else:
            num_active_segments = len(current_available_numbers)
            segment_angle = 360 / num_active_segments # 각 칸의 각도

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
            segment_width = 80
            segment_height = 40
            # 숫자가 위치할 반지름 (룰렛 중앙에서 세그먼트 중앙까지의 거리)
            # 룰렛 바퀴 반지름(125px)에서 세그먼트 높이의 절반 정도를 빼서 조정
            number_radial_distance = wheel_radius_css - (segment_height / 2) - 10 # 룰렛 테두리 안쪽으로 배치

            # 현재 추첨 가능한 번호들을 정렬하여 시각적 순서를 일관되게 유지합니다.
            sorted_available_numbers = sorted(current_available_numbers)

            for i, num in enumerate(sorted_available_numbers):
                # 각 세그먼트의 시작 각도 (0번 인덱스가 0도에 위치)
                # 이 각도는 룰렛 바퀴의 0도 (오른쪽 3시 방향)를 기준으로 합니다.
                segment_start_angle = i * segment_angle

                # CSS `transform: rotate()`는 시계 방향이 양수입니다.
                # `transform`을 이용한 포지셔닝:
                # 1. 룰렛 바퀴의 중앙(50%, 50%)으로 이동
                # 2. 본인의 중심을 기준으로 회전 (세그먼트 자체를 방사형으로 돌림)
                # 3. Y축(회전된 축) 방향으로 바깥으로 이동 (룰렛 중앙으로부터의 거리)
                # 이 `transform`은 `roulette-wheel` 내에서 상대적으로 적용됩니다.
                
                # 세그먼트 안의 숫자는 항상 똑바로 보이도록 세그먼트의 회전 각도에 반대되는 각도로 회전시킵니다.
                content_rotate_angle = -segment_start_angle

                color_index = i % len(segment_colors)
                segment_bg_color = segment_colors[color_index]
                text_color = "black"

                segments_html.append(f"""
                <div class='roulette-segment' style='
                    background-color: {segment_bg_color};
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    width: {segment_width}px;
                    height: {segment_height}px;
                    /* Translate to center, then rotate to position, then translate radially */
                    transform: translate(-50%, -50%) rotate({segment_start_angle}deg) translateY(-{number_radial_distance}px);
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 1.2em;
                    color: {text_color};
                    font-weight: normal;
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

        # 룰렛 중앙에 추첨된 번호 (애니메이션 중 또는 최종 결과) 표시
        central_display_html = f"""
        <div class='roulette-number-display' style='
            font-size: {("5em" if drawn_number_display is not None else "4em")};
            color: {("#FF4500" if drawn_number_display is not None else "#333")};
        '>
            {drawn_number_display if drawn_number_display is not None else "---"}
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
            width: {container_size}px; /* 룰렛 컨테이너 크기 */
            height: {container_size}px; /* 룰렛 컨테이너 크기 */
            margin: 30px auto;
            border-radius: 50%;
            background-color: #f0f2f6; /* 배경색 */
            box-shadow: inset 0 0 15px rgba(0,0,0,0.3); /* 그림자 강화 */
            overflow: hidden; /* 내부 요소가 넘치지 않도록 */
        }}

        .roulette-wheel {{
            width: {2 * wheel_radius_css}px; /* 룰렛 바퀴 크기 */
            height: {2 * wheel_radius_css}px; /* 룰렛 바퀴 크기 */
            border-radius: 50%;
            border: 15px solid #333; /* 테두리 두께 */
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
                # 현재 available_numbers 리스트 내에서 drawn_number의 인덱스를 찾습니다.
                # (룰렛 칸은 available_numbers에 따라 동적으로 생성되므로, 이 인덱스를 사용해야 합니다.)
                sorted_available_numbers = sorted(st.session_state.available_numbers)
                drawn_number_index_in_current_list = sorted_available_numbers.index(drawn_number)

                num_segments_for_calc = len(sorted_available_numbers)
                segment_angle_val = 360 / num_segments_for_calc if num_segments_for_calc > 0 else 0

                # 뽑힌 번호의 세그먼트 중심이 0도(상단 포인터)에 오도록 할 최종 각도 계산
                # 룰렛의 0도가 오른쪽(3시 방향)이므로, 포인터(12시 방향)는 -90도(또는 270도)에 해당합니다.
                # 세그먼트의 중심 각도: drawn_number_index_in_current_list * segment_angle_val + (segment_angle_val / 2)
                target_segment_center_angle = (drawn_number_index_in_current_list * segment_angle_val + (segment_angle_val / 2)) % 360
                
                # target_point_angle: 포인터가 위치한 각도 (12시 방향)
                target_point_angle = 270 # 270 degrees is 12 o'clock in CSS rotation (clockwise from 3 o'clock)

                # 룰렛을 회전시켜 target_segment_center_angle이 target_point_angle에 오도록 할 목표 회전 각도 (0-360 범위)
                # 필요한 상대적 회전량
                relative_rotation_needed = (target_point_angle - target_segment_center_angle + 360) % 360

                # 최종 총 회전 각도 계산
                # 현재 회전 각도에서 시작 + 무작위 추가 바퀴 + 목표 위치로의 정렬 회전
                # (start_rotation % 360)은 현재 룰렛의 0-360도 범위 내 각도입니다.
                # needed_rotation_for_alignment는 현재 위치에서 목표 위치까지 추가로 필요한 각도 (0-360)
                needed_rotation_for_alignment = (relative_rotation_needed - (start_rotation % 360) + 360) % 360

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
                        # 여기서는 available_numbers가 아직 업데이트되지 않았으므로 현재 세션 상태의 available_numbers를 사용합니다.
                        render_roulette_visual(st.session_state.available_numbers, current_spin_rotation, display_num)
                        time.sleep(sleep_per_frame)

                # 실제 번호 리스트에서 뽑힌 번호를 제거하고 기록합니다.
                st.session_state.available_numbers.remove(drawn_number)
                st.session_state.drawn_numbers.append(drawn_number)

                # 최종 당첨 번호를 룰렛 중앙에 표시하고 색상 및 크기를 고정합니다.
                # 여기서는 available_numbers가 업데이트된 후의 상태를 전달하여 룰렛이 새로운 칸 수로 렌더링되도록 합니다.
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
            st.session_state.current_rotation = 0 # 초기화 시 회전 각도 초기화
            st.info("룰렛이 초기화되었습니다.")
            # 초기화된 상태의 룰렛을 렌더링합니다.
            render_roulette_visual(st.session_state.available_numbers, st.session_state.current_rotation)
            st.rerun()

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
