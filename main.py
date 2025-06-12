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
        st.session_state.max_students = 1 # 초기 학생 수를 1로 설정하여 min_value 오류 방지

    if 'drawn_numbers' not in st.session_state:
        st.session_state.drawn_numbers = [] # 이미 뽑힌 번호들을 저장할 리스트

    # available_numbers는 현재 남아있는 (아직 뽑히지 않은) 번호들의 리스트입니다.
    # 앱이 처음 로드되거나, max_students가 변경되었을 때,
    # 또는 available_numbers가 비어있지만 max_students가 초기화되지 않았을 때 재설정합니다.
    if 'available_numbers' not in st.session_state or \
       (len(st.session_state.available_numbers) == 0 and st.session_state.max_students > 0 and not st.session_state.drawn_numbers) or \
       (st.session_state.max_students != len(st.session_state.drawn_numbers) + len(st.session_state.available_numbers)):
        if not st.session_state.drawn_numbers: # 뽑힌 번호가 없는 초기 상태일 때만 완전히 재초기화
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))

    # 룰렛의 현재 회전 각도를 저장합니다.
    if 'current_rotation' not in st.session_state:
        st.session_state.current_rotation = 0 # 룰렛의 초기 회전 각도

    # 총 학생 수를 입력받는 숫자 입력 필드를 생성합니다.
    # StreamlitDuplicateElementId 오류 방지를 위해 'key'를 추가합니다.
    max_students_input = st.number_input(
        "총 학생 수를 입력하세요:",
        min_value=1,
        value=st.session_state.max_students,
        step=1,
        help="발표에 참여할 학생의 총 인원수를 입력하세요.",
        key='max_students_input_key' # 고유한 key를 부여하여 위젯 충돌 방지
    )

    # 입력된 학생 수가 이전과 다르면 룰렛을 초기화합니다.
    # (학생 수 변경 시 룰렛 전체 상태를 재설정)
    if max_students_input != st.session_state.max_students:
        st.session_state.max_students = max_students_input
        st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        st.session_state.drawn_numbers = []
        st.session_state.current_rotation = 0 # 초기화 시 회전 각도도 초기화
        st.success(f"✅ 룰렛이 **{st.session_state.max_students}명**의 학생으로 초기화되었습니다. 이제 '룰렛 돌리기' 버튼을 눌러주세요!")
        st.rerun() # 변경사항 즉시 반영을 위해 앱 다시 실행

    st.markdown("---") # 구분선 추가

    # 현재 남아있는 번호들을 표시합니다.
    st.info(f"**남아있는 번호:** {st.session_state.available_numbers if st.session_state.available_numbers else '없음'}")
    # 추첨된 번호들을 순서대로 표시합니다.
    st.success(f"**추첨된 순서:** {st.session_state.drawn_numbers if st.session_state.drawn_numbers else '아직 추첨된 번호가 없습니다.'}")

    st.markdown("---") # 구분선 추가

    # 룰렛 애니메이션 컨테이너를 위한 placeholder를 생성합니다.
    # 이 placeholder를 통해 룰렛의 전체 HTML/CSS를 동적으로 업데이트하여 애니메이션을 구현합니다.
    roulette_placeholder = st.empty()

    # 룰렛을 렌더링하는 함수를 정의합니다.
    # 이 함수는 룰렛의 HTML/CSS 구조와 각 칸의 번호, 그리고 룰렛의 회전 상태를 업데이트합니다.
    def render_roulette_visual(current_rotation, drawn_number_display=None):
        # 룰렛 컨테이너의 크기 (전체 룰렛 영역)
        container_size = 350 # px
        # 룰렛 바퀴의 반지름 (실제 회전하는 원형 부분)
        wheel_radius_css = 125 # px (width/2)

        # 룰렛 칸의 기본 스타일 정의 (크기, 정렬 등)
        segment_width = 70  # 각 칸의 너비
        segment_height = 35 # 각 칸의 높이
        # 번호가 룰렛 중앙으로부터 배치될 반지름 (wheel_radius_css - 여백)
        number_radial_distance = wheel_radius_css * 0.7 # 룰렛 반지름의 70% 지점에 배치

        # wheel_content_html 변수를 먼저 초기화하여 NameError를 방지합니다.
        wheel_content_html = "" 
        
        # 전체 학생 수를 기준으로 고정된 룰렛 칸 수를 생성합니다. (뽑히면 숨김 처리)
        total_fixed_segments = st.session_state.max_students
        
        if total_fixed_segments == 0:
            # 학생 수가 0일 경우 메시지 표시
            wheel_content_html = "<div class='roulette-no-numbers'>학생 수를 입력하세요.</div>"
        else:
            # 각 칸이 차지하는 각도 (360도를 전체 칸 수로 나눔)
            segment_angle_val_for_fixed = 360 / total_fixed_segments

            # 시각적 구분을 위한 색상 팔레트 (다양한 색상 추가)
            segment_colors = [
                "#FFD700", "#FF6347", "#6A5ACD", "#32CD32", "#8A2BE2",
                "#FF4500", "#1E90FF", "#DAA520", "#DC143C", "#00CED1",
                "#FF8C00", "#4B0082", "#7FFF00", "#BA55D3", "#F0E68C",
                "#ADD8E6", "#FFA07A", "#90EE90", "#DDA0DD", "#FFE4B5",
                "#87CEEB", "#FFDAB9", "#BDB76B", "#FA8072", "#AFEEEE",
                "#F4A460", "#EE82EE", "#00FA9A", "#FFC0CB", "#6495ED"
            ]

            segments_html = []
            # 각 룰렛 칸(세그먼트)을 생성하고 배치합니다.
            for i in range(total_fixed_segments):
                num = i + 1 # 1부터 시작하는 학생 번호
                # 각 세그먼트의 중심 각도를 계산합니다. (룰렛의 0도(오른쪽 3시)를 기준으로 시계방향)
                segment_center_angle = (i * segment_angle_val_for_fixed) + (segment_angle_val_for_fixed / 2)
                
                # 이미 뽑힌 번호인지 확인합니다.
                is_drawn = num in st.session_state.drawn_numbers
                # 뽑힌 번호는 숨김 처리합니다.
                display_style = "display: none;" if is_drawn else ""

                # 칸의 배경색을 팔레트에서 순환하여 적용합니다.
                segment_bg_color = segment_colors[i % len(segment_colors)]
                text_color = "black" # 칸 안의 숫자 색상

                # 세그먼트 안의 숫자가 룰렛 회전과 상관없이 항상 똑바로 보이도록 반대 회전 각도를 적용합니다.
                content_rotate_angle = -segment_center_angle

                segments_html.append(f"""
                <div class='roulette-segment' style='
                    background-color: {segment_bg_color};
                    /* 룰렛 중앙(50%, 50%)을 기준으로 배치 후 회전, 그리고 바깥으로 이동 */
                    transform: translate(-50%, -50%) rotate({segment_center_angle}deg) translateY(-{number_radial_distance}px);
                    {display_style} /* 뽑힌 번호 숨김 */
                '>
                    <span style="transform: rotate({content_rotate_angle}deg); display: inline-block;">{num}</span>
                </div>
                """)
            wheel_content_html = ''.join(segments_html)

        # 룰렛 바퀴 전체의 HTML을 구성합니다. wheel_content_html은 항상 정의됩니다.
        wheel_html = f"<div class='roulette-wheel' style='transform: rotate({current_rotation}deg);'>{ wheel_content_html }</div>"

        # 룰렛 중앙에 추첨된 번호 (애니메이션 중 또는 최종 결과)를 표시합니다.
        # 이 숫자는 룰렛 바퀴의 회전과 별개로 항상 중앙에 고정되어 표시됩니다.
        central_display_html = f"""
        <div class='roulette-number-display' style='
            font-size: {("5em" if drawn_number_display is not None else "4em")};
            color: {("#FF4500" if drawn_number_display is not None else "#333")};
        '>
            {drawn_number_display if drawn_number_display is not None else "---"}
        </div>
        """

        # 최종 HTML 마크다운 구성
        roulette_placeholder.markdown(f"""
        <style>
        /* 룰렛 전체를 감싸는 컨테이너 스타일 */
        .roulette-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            position: relative;
            width: {container_size}px;
            height: {container_size}px;
            margin: 30px auto;
            border-radius: 50%;
            background-color: #f0f2f6; /* 배경색 */
            box-shadow: inset 0 0 15px rgba(0,0,0,0.3); /* 안쪽 그림자 */
            overflow: hidden; /* 내부 요소가 컨테이너를 벗어나지 않도록 */
        }}

        /* 룰렛 바퀴 자체의 스타일 (실제 회전하는 부분) */
        .roulette-wheel {{
            width: {2 * wheel_radius_css}px;
            height: {2 * wheel_radius_css}px;
            border-radius: 50%;
            border: 15px solid #333; /* 바퀴 테두리 */
            box-shadow: 0 0 20px rgba(0,0,0,0.6); /* 바퀴 그림자 */
            position: relative;
            background-color: #eee; /* 기본 바퀴 배경 */
            /* 룰렛 바퀴 전체의 회전 애니메이션 적용 */
            transform: rotate({current_rotation}deg);
            /* transition: transform 0.1s linear; /* 부드러운 회전을 위해 (단, JS 애니메이션 시 주석처리) */
        }}

        /* 룰렛 상단의 포인터 스타일 */
        .roulette-pointer {{
            width: 0;
            height: 0;
            border-left: 25px solid transparent; /* 왼쪽 삼각형 변 */
            border-right: 25px solid transparent; /* 오른쪽 삼각형 변 */
            border-bottom: 40px solid #ff4b4b; /* 밑변 (빨간색 삼각형) */
            position: absolute;
            top: -20px; /* 룰렛 컨테이너 상단에 위치 */
            left: 50%;
            transform: translateX(-50%); /* 중앙 정렬 */
            z-index: 100; /* 포인터가 다른 요소 위에 오도록 */
        }}

        /* 각 룰렛 칸(세그먼트)의 스타일 */
        .roulette-segment {{
            position: absolute;
            top: 50%;
            left: 50%;
            width: {segment_width}px;
            height: {segment_height}px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 1.2em;
            font-weight: bold; /* 숫자 폰트 굵게 */
            color: black;
            border: 1px solid rgba(255,255,255,0.3); /* 칸 사이 경계선 */
            box-sizing: border-box; /* 패딩, 보더가 너비/높이에 포함되도록 */
            border-radius: 5px; /* 약간 둥근 모서리 */
            z-index: 50; /* 바퀴 위에 오도록 */
            /* transform-origin: center; /* 룰렛 중앙이 아닌 자신의 중심에서 회전 */
            /* 이 세그먼트의 transform은 개별 세그먼트의 위치 및 방향을 설정합니다.
               룰렛 바퀴의 transform에 의해 전체적으로 회전됩니다. */
        }}

        /* 룰렛 중앙에 추첨된 번호가 표시될 영역 스타일 */
        .roulette-number-display {{
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-weight: bold;
            z-index: 101; /* 중앙 숫자가 포인터 위에 오도록 */
            text-align: center;
            width: 100%;
            height: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
            border-radius: 50%;
        }}

        /* 학생 수가 0일 경우 룰렛 중앙에 표시될 메시지 스타일 */
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
            {wheel_html} <!-- 룰렛 바퀴와 그 안에 칸들이 포함 -->
            {central_display_html} <!-- 룰렛 중앙의 숫자 -->
        </div>
        """, unsafe_allow_html=True) # HTML 렌더링 허용

    # 앱 로드 시 또는 초기화 시 룰렛을 초기 상태로 렌더링합니다.
    # 초기 렌더링 시에는 현재 회전 각도를 사용하며, 아직 추첨된 번호는 없으므로 중앙 표시는 기본값입니다.
    render_roulette_visual(st.session_state.current_rotation)

    # '룰렛 돌리기' 버튼을 생성합니다.
    col1, col2 = st.columns(2) # 버튼을 나란히 배치하기 위해 두 개의 컬럼을 생성합니다.

    with col1:
        if st.button("룰렛 돌리기 🎰", help="남아있는 학생 중 한 명을 무작위로 추첨합니다."):
            if st.session_state.available_numbers: # 추첨 가능한 번호가 있을 경우에만 작동
                st.balloons() # 축하 풍선 효과를 미리 보여줍니다.

                # 최종 결과로 뽑힐 번호를 선택합니다.
                drawn_number = random.choice(st.session_state.available_numbers)
                
                # 룰렛 스핀 애니메이션 설정
                spin_duration = 4 # 룰렛이 회전하는 총 시간 (초)
                num_frames = 60 # 애니메이션 프레임 수 (부드러운 전환을 위해 충분히 크게)
                sleep_per_frame = spin_duration / num_frames # 각 프레임 당 지연 시간

                # 룰렛 회전 시작 각도 (현재 룰렛이 멈춰있는 각도)
                start_rotation = st.session_state.current_rotation
                # 무작위로 3~5바퀴 더 돌도록 설정하여 흥미를 유발합니다.
                random_extra_spins = random.randint(3, 5)

                # 최종 정지 각도 계산: 뽑힌 번호가 포인터(상단 중앙)에 정확히 오도록
                # 현재 available_numbers 리스트를 정렬하여 인덱스와 각도를 일치시킵니다.
                sorted_available_numbers_for_calc = sorted(st.session_state.available_numbers)
                # 뽑힌 번호가 현재 룰렛에 남아있는 번호들 중 몇 번째에 해당하는지 인덱스를 찾습니다.
                drawn_number_index_in_current_list = sorted_available_numbers_for_calc.index(drawn_number)

                # 현재 룰렛의 활성 세그먼트(칸) 수
                num_segments_for_calc = len(sorted_available_numbers_for_calc)
                # 각 세그먼트가 차지하는 각도
                segment_angle_val = 360 / num_segments_for_calc if num_segments_for_calc > 0 else 0

                # 뽑힌 번호의 세그먼트 중심이 룰렛의 0도(오른쪽 3시)를 기준으로 얼마나 떨어져 있는지 계산합니다.
                target_segment_center_angle = (drawn_number_index_in_current_list * segment_angle_val + (segment_angle_val / 2)) % 360
                
                # 룰렛의 포인터는 12시 방향에 고정되어 있습니다. CSS rotate는 시계 방향이 양수이므로,
                # 12시 방향은 270도에 해당합니다 (3시 방향이 0도일 때).
                target_point_angle = 270 

                # 룰렛을 회전시켜 target_segment_center_angle이 target_point_angle에 오도록 할 최종 상대적 회전 각도 (0-360 범위)
                relative_rotation_needed = (target_point_angle - target_segment_center_angle + 360) % 360

                # 최종적으로 룰렛이 멈출 총 회전 각도를 계산합니다.
                # 이는 시작 각도 + 무작위로 추가 회전할 바퀴 수 + 목표 위치로 정렬하기 위한 추가 각도입니다.
                # `start_rotation % 360`은 현재 룰렛의 0-360도 범위 내 각도를 나타냅니다.
                needed_rotation_for_alignment = (relative_rotation_needed - (start_rotation % 360) + 360) % 360
                final_rotation = start_rotation + (random_extra_spins * 360) + needed_rotation_for_alignment

                # 룰렛 회전 애니메이션 실행
                with st.spinner(f'룰렛이 힘차게 돌아가는 중... 잠시 기다려주세요!'):
                    for i in range(num_frames):
                        progress = (i + 1) / num_frames
                        # Cubic ease-out 함수를 사용하여 부드러운 감속 효과를 만듭니다.
                        eased_progress = 1 - (1 - progress)**3
                        
                        # 현재 프레임의 회전 각도를 계산합니다.
                        current_spin_rotation = start_rotation + (final_rotation - start_rotation) * eased_progress

                        # 애니메이션 중 중앙에 임시로 표시될 번호 (빠르게 변하는 효과)
                        if st.session_state.available_numbers:
                            display_num = random.choice(st.session_state.available_numbers)
                        else:
                            display_num = "---"

                        # 룰렛 시각화를 업데이트합니다. (회전 각도와 임시 번호 전달)
                        # 이 시점에는 아직 available_numbers에서 뽑힌 번호가 제거되지 않았습니다.
                        render_roulette_visual(current_spin_rotation, display_num)
                        time.sleep(sleep_per_frame)

                # 실제 번호 리스트에서 뽑힌 번호를 제거하고 기록합니다.
                st.session_state.available_numbers.remove(drawn_number)
                st.session_state.drawn_numbers.append(drawn_number)

                # 최종 당첨 번호를 룰렛 중앙에 표시하고, 룰렛을 최종 각도로 고정합니다.
                # available_numbers가 업데이트되었으므로, 이제 뽑힌 번호의 칸은 렌더링되지 않습니다.
                render_roulette_visual(final_rotation, drawn_number)
                st.session_state.current_rotation = final_rotation # 다음 룰렛을 위해 최종 각도 저장

                # 룰렛 아래에 최종 당첨 번호를 한 번 더 표시합니다.
                st.markdown(f"## 🎉 **{drawn_number}번 학생 당첨!**")
                time.sleep(1) # 당첨 번호가 잠시 보이도록
                st.rerun() # 변경사항 즉시 반영 (전체 상태 업데이트를 위해 앱을 다시 실행합니다.)
            else:
                # 더 이상 뽑을 번호가 없을 때 경고 메시지를 표시합니다.
                st.warning("더 이상 뽑을 학생이 없습니다. '룰렛 초기화' 버튼을 눌러 다시 시작하세요.")

    with col2:
        # '룰렛 초기화' 버튼을 생성합니다.
        if st.button("룰렛 초기화 🔄", help="모든 추첨 상태를 처음으로 되돌립니다."):
            st.session_state.max_students = 1 # 초기 학생 수로 되돌림
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
            st.session_state.drawn_numbers = []
            st.session_state.current_rotation = 0 # 초기화 시 회전 각도도 초기화
            st.info("룰렛이 초기화되었습니다.")
            # 초기화된 상태의 룰렛을 렌더링합니다.
            render_roulette_visual(st.session_state.current_rotation)
            st.rerun() # 앱을 다시 실행하여 초기 상태로 돌아갑니다.

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
