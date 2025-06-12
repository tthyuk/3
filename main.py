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
        if not numbers:
            # 학생 수가 0일 경우 메시지 표시
            segment_html = "<div class='roulette-no-numbers'>학생 수를 입력하세요.</div>"
            # 룰렛 바퀴는 회전하지 않고, 메시지만 표시합니다.
            wheel_html = f"<div class='roulette-wheel' style='transform: rotate(0deg);'>{segment_html}</div>"
        else:
            total_segments = len(list(range(1, st.session_state.max_students + 1))) # 전체 초기 학생 수 (칸 수 고정)
            segment_angle = 360 / total_segments # 각 칸의 각도
            # 시각적 구분을 위한 색상 팔레트
            segment_colors = [
                "#FFD700", "#FF6347", "#6A5ACD", "#32CD32", "#8A2BE2",
                "#FF4500", "#1E90FF", "#DAA520", "#DC143C", "#00CED1",
                "#FF8C00", "#4B0082", "#7FFF00", "#BA55D3", "#F0E68C"
            ] # 다양한 색상 추가

            segments_html = []
            # 모든 가능한 번호(1부터 max_students까지)를 기준으로 세그먼트를 생성합니다.
            # 이렇게 해야 룰렛 칸 수가 고정되고, 뽑힌 번호는 비활성화되는 효과를 줄 수 있습니다.
            all_possible_numbers = list(range(1, st.session_state.max_students + 1))

            for i, num in enumerate(all_possible_numbers):
                # 각 세그먼트의 초기 회전 각도 (1번이 최상단에 오도록 조정)
                segment_rotation = i * segment_angle

                # 현재 뽑힌 번호인지 확인
                is_drawn = num in st.session_state.drawn_numbers

                # 색상 순환 (남아있는 번호만 활성 색상, 뽑힌 번호는 회색)
                color_index = i % len(segment_colors)
                segment_bg_color = segment_colors[color_index] if not is_drawn else "#D3D3D3" # 뽑힌 번호는 회색

                # 텍스트 색상 및 폰트 두께
                text_color = "black" if not is_drawn else "#696969" # 뽑힌 번호는 어두운 회색 텍스트
                font_weight = "normal"

                # 룰렛 중앙에서 번호까지의 거리 (radius of numbers)
                number_radius = 90 # 룰렛 중앙에서 숫자가 위치할 반지름

                # 번호가 세그먼트 중앙에 오도록 추가 회전 조정
                # 각 번호의 중심이 세그먼트의 중심에 오도록 번호 자체는 세그먼트 회전에 반대 방향으로 회전합니다.
                # (90도 보정은 룰렛의 상단이 0도라고 가정할 때 숫자를 똑바로 보이게 하기 위함)
                text_transform = f"rotate({-segment_rotation}deg)"


                segments_html.append(f"""
                <div class='roulette-segment' style='
                    background-color: {segment_bg_color};
                    transform: rotate({segment_rotation}deg) translate(0px, -{number_radius}px);
                    width: 50px; /* 세그먼트의 시각적 너비 */
                    height: 50px; /* 세그먼트의 시각적 높이 */
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    margin-left: -25px; /* width/2 */
                    margin-top: -25px; /* height/2 */
                    transform-origin: 25px {number_radius + 25}px; /* 세그먼트 중심에서 회전하도록 조정 */
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 1.2em;
                    color: {text_color};
                    font-weight: {font_weight};
                    border: 1px solid rgba(255,255,255,0.2);
                    box-sizing: border-box;
                    border-radius: 50%; /* 숫자 칸을 원형으로 */
                    z-index: 50; /* 룰렛 바퀴 위에 오도록 */
                '>
                    <span style="transform: {text_transform}; display: inline-block;">{num}</span>
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
            /* overflow: hidden; /* segments들이 부모를 벗어나지 않도록 */
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
            /* background-color: rgba(255,255,255,0.7); */
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
                total_segments = st.session_state.max_students # 전체 초기 번호 수
                segment_angle_val = 360 / total_segments if total_segments > 0 else 0

                # 뽑힌 번호의 인덱스 (1부터 시작하는 번호를 0-based 인덱스로)
                # 이 인덱스에 해당하는 번호가 상단 중앙에 오도록 회전해야 합니다.
                # (drawn_number - 1)은 0-based 인덱스
                # 룰렛은 시계 방향으로 회전한다고 가정하고, 포인터는 상단 고정
                # 목표 번호가 상단 중앙에 오려면, (drawn_number - 1) * segment_angle_val 만큼 더 회전해야 합니다.
                # 그러나 CSS transform: rotate는 시계 방향이 양수이므로,
                # 회전하는 룰렛을 멈추는 최종 각도는 (시작 각도 + 추가 회전수 * 360도 + 목표 번호의 위치에 맞게 회전)
                # 목표 번호의 위치: (drawn_number - 1) * segment_angle_val (0번 인덱스가 0도에서 시작한다고 가정)
                # 최종적으로 포인터에 맞추려면 그 번호의 정중앙이 포인터에 와야 합니다.
                # 룰렛은 시계 방향으로 회전하므로, 목표 번호가 0도 위치에 오도록 회전해야 함.
                # 즉, (drawn_number - 1) * segment_angle_val 만큼의 각도를 (360 - 그 각도)로 보정해야 함.
                # 예를 들어 1번이 (1-1)*각도 = 0도에, 2번이 (2-1)*각도 에 있으므로
                # 1번이 오려면 0도, 2번이 오려면 -segment_angle_val 만큼 추가 회전하면 됨 (상대적으로)
                # 실제로는 (total_segments - (drawn_number - 1)) * segment_angle_val 만큼 더 돌아서 0도에 오도록 합니다.
                # (drawn_number - 1)은 0-based 인덱스.
                # 목표 각도 = (start_rotation + (random_extra_spins * 360)) + (360 - ((drawn_number - 1) * segment_angle_val)) % 360

                # 최종 각도 계산 (포인터가 룰렛의 12시 방향에 고정되어 있고, 1번이 12시 방향에서 시작한다고 가정)
                # (drawn_number - 1)은 0부터 시작하는 인덱스
                # 각 세그먼트의 중앙은 (인덱 * segment_angle_val) + segment_angle_val / 2
                # 포인터는 0도(12시)를 가리키므로, (drawn_number - 1)번 인덱스에 해당하는 번호의 중심이 0도에 오도록 회전해야 함.
                # 룰렛은 시계 반대 방향으로 돌아야 숫자가 올라옴. (CSS transform: rotate는 시계 방향이 양수)
                # 따라서 목표 번호의 위치까지의 각도만큼 음수 회전 (시계 반대 방향)
                # 예를 들어 1번이 목표면 0도, 2번이 목표면 -segment_angle_val.
                # 즉, (drawn_number - 1) * segment_angle_val 만큼 시계 방향으로 돌려야 그 번호가 포인터에 멈춤.
                # 최종 각도 = 시작 각도 + (총 바퀴수 * 360) + (추첨된 번호의 위치까지의 추가 회전)
                target_segment_start_angle = (drawn_number - 1) * segment_angle_val
                # 룰렛이 포인터에 정확히 멈추려면, 해당 번호의 시작 지점이 포인터에 맞춰져야 합니다.
                # 룰렛은 시계 방향으로 계속 돌다가 멈추므로, 목표 번호의 위치에 맞춰야 합니다.
                # 0도(12시)가 시작점, 1번이 0도에 위치한다고 가정.
                # 뽑힌 번호 (예: 3번)가 0도에 오려면 룰렛 전체를 (3-1)*segment_angle_val 만큼 더 돌려야 합니다.
                # 최종 회전 각도는 (시작 각도 + 총 회전 바퀴수 * 360 + 목표 번호의 각도)
                final_rotation_target = target_segment_start_angle

                # 현재 회전 각도에서 목표 각도까지 추가 회전
                # start_rotation이 이전 최종 각도이므로, 최종 각도를 맞추기 위해 필요한 총 회전량
                # 목표까지 회전해야 할 각도 = (random_extra_spins * 360) + (final_rotation_target - (st.session_state.current_rotation % 360))
                # final_rotation = start_rotation + (random_extra_spins * 360) + (final_rotation_target - (start_rotation % 360))
                
                # 목표 각도에 정지시키기 위한 최종 회전량 (부드러운 정지를 위해 이전 각도를 고려)
                # 예를 들어, 현재 룰렛이 10도에 멈춰있고, 5번이 뽑혀서 150도에 멈춰야 한다면
                # (5바퀴 + 150-10) 만큼 더 돌아야 합니다.
                # target_angle_within_360 = final_rotation_target % 360
                # current_angle_within_360 = start_rotation % 360
                # angle_to_add = (target_angle_within_360 - current_angle_within_360 + 360) % 360
                # final_rotation = start_rotation + (random_extra_spins * 360) + angle_to_add

                # Simple calculation: Just spin to the target angle, making sure it spins at least one full circle
                final_rotation = start_rotation + (random_extra_spins * 360) + (final_rotation_target - (start_rotation % 360) + 360) % 360

                with st.spinner(f'룰렛이 힘차게 돌아가는 중... 잠시 기다려주세요!'):
                    for i in range(num_frames):
                        progress = (i + 1) / num_frames
                        # Cubic ease-out for a smooth deceleration
                        eased_progress = 1 - (1 - progress)**3
                        
                        # 현재 프레임의 회전 각도 계산
                        current_spin_rotation = start_rotation + (final_rotation - start_rotation) * eased_progress

                        # 애니메이션 중 중앙에 표시될 임시 번호 (빠르게 변하는 효과)
                        # 남아있는 번호 중에서 무작위로 선택하여 애니메이션에 사용합니다.
                        if st.session_state.available_numbers:
                            display_num = random.choice(st.session_state.available_numbers)
                        else:
                            display_num = "---" # 뽑을 번호가 없으면 --- 표시

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
