import streamlit as st
import random
import time # time 모듈을 추가하여 지연 시간을 줍니다.

# Streamlit 앱의 메인 함수를 정의합니다.
def main():
    # 애플리케이션의 제목을 설정합니다.
    st.title("학생 발표 순서 추첨 룰렛 🎡")

    # 세션 상태(session state)를 초기화합니다.
    # st.session_state는 Streamlit 앱의 상태를 저장하고 관리하는 데 사용됩니다.
    # 앱이 리로드되거나 버튼이 클릭되어도 이 변수들의 값은 유지됩니다.

    # 세션 상태 변수들을 의존성 없이 먼저 초기화합니다.
    if 'max_students' not in st.session_state:
        st.session_state.max_students = 1 # 변경: 초기값을 0에서 1로 변경하여 min_value 오류 방지

    if 'drawn_numbers' not in st.session_state:
        st.session_state.drawn_numbers = []

    # available_numbers는 다른 변수들의 초기화 후, 그 값들에 따라 초기화될 수 있습니다.
    # 이는 앱이 처음 로드될 때와 max_students가 변경되었을 때 모두 적용됩니다.
    # available_numbers가 세션에 없거나, 현재 학생 수와 뽑힌/남은 학생 수의 합이 맞지 않을 때만 재초기화
    # len(st.session_state.available_numbers) == 0 and st.session_state.max_students > 0
    # 이 조건은 available_numbers가 비어있고, max_students가 유효한 경우를 의미합니다.
    # st.session_state.max_students != len(st.session_state.drawn_numbers) + len(st.session_state.available_numbers)
    # 이 조건은 현재 설정된 총 학생 수와 실제 뽑혔거나 남아있는 학생 수의 합이 일치하지 않을 때 재초기화합니다.
    if 'available_numbers' not in st.session_state or \
       (len(st.session_state.available_numbers) == 0 and st.session_state.max_students > 0) or \
       (st.session_state.max_students != len(st.session_state.drawn_numbers) + len(st.session_state.available_numbers)):
        # 뽑힌 번호가 없으면 (즉, 완전히 새로운 시작이거나 초기화된 상태) available_numbers를 완전히 재초기화
        if not st.session_state.drawn_numbers:
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        # else: 일부 뽑힌 상태에서 리프레시 시, 남은 번호는 그대로 유지되도록 합니다. (현재 로직에서는 명시적인 else 로직 없음)


    # 총 학생 수를 입력받는 숫자 입력 필드를 생성합니다.
    # min_value는 최소값, value는 초기값, step은 증가/감소 단위를 설정합니다.
    # 초기값은 st.session_state.max_students로 설정하여 세션 상태를 유지합니다.
    max_students_input = st.number_input(
        "총 학생 수를 입력하세요:",
        min_value=1,
        value=st.session_state.max_students,
        step=1,
        help="발표에 참여할 학생의 총 인원수를 입력하세요."
    )

    # 입력된 학생 수가 이전과 다르면 룰렛을 초기화합니다.
    # 이 조건은 사용자가 학생 수를 변경했을 때 자동으로 룰렛을 재설정하는 역할을 합니다.
    if max_students_input != st.session_state.max_students:
        st.session_state.max_students = max_students_input
        # 1부터 max_students_input까지의 번호로 available_numbers를 초기화합니다.
        st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
        # drawn_numbers는 비워줍니다.
        st.session_state.drawn_numbers = []
        st.success(f"✅ 룰렛이 **{st.session_state.max_students}명**의 학생으로 초기화되었습니다. 이제 '룰렛 돌리기' 버튼을 눌러주세요!")
        # max_students 변경 시 바로 반영되도록 rerurn
        st.rerun()

    st.markdown("---") # 구분선 추가

    # 현재 남아있는 번호들을 표시합니다.
    st.info(f"**남아있는 번호:** {st.session_state.available_numbers if st.session_state.available_numbers else '없음'}")
    # 추첨된 번호들을 순서대로 표시합니다.
    st.success(f"**추첨된 순서:** {st.session_state.drawn_numbers if st.session_state.drawn_numbers else '아직 추첨된 번호가 없습니다.'}")

    st.markdown("---") # 구분선 추가

    # '룰렛 돌리기' 버튼을 생성합니다.
    col1, col2 = st.columns(2) # 버튼을 나란히 배치하기 위해 두 개의 컬럼을 생성합니다.

    with col1:
        if st.button("룰렛 돌리기 🎰", help="남아있는 학생 중 한 명을 무작위로 추첨합니다."):
            # available_numbers 리스트에 번호가 남아있는지 확인합니다.
            if st.session_state.available_numbers:
                # 룰렛이 돌아가는 시각적인 효과를 추가합니다.
                with st.spinner('룰렛이 힘차게 돌아가는 중...'):
                    time.sleep(1.5) # 1.5초 동안 스피너를 보여줍니다.

                # random.choice를 사용하여 남아있는 번호 중 하나를 무작위로 선택합니다.
                drawn_number = random.choice(st.session_state.available_numbers)
                # 선택된 번호를 available_numbers 리스트에서 제거합니다.
                st.session_state.available_numbers.remove(drawn_number)
                # 선택된 번호를 drawn_numbers 리스트의 끝에 추가합니다.
                st.session_state.drawn_numbers.append(drawn_number)
                # 추첨 결과를 크게 표시합니다.
                st.balloons() # 축하 풍선 효과!
                st.markdown(f"## 🎉 **{drawn_number}번 학생 당첨!**")
                st.rerun() # 변경사항 즉시 반영
            else:
                # 더 이상 뽑을 번호가 없을 때 경고 메시지를 표시합니다.
                st.warning("더 이상 뽑을 학생이 없습니다. '룰렛 초기화' 버튼을 눌러 다시 시작하세요.")

    with col2:
        # '룰렛 초기화' 버튼을 생성합니다.
        if st.button("룰렛 초기화 🔄", help="모든 추첨 상태를 처음으로 되돌립니다."):
            # 총 학생 수에 맞춰 available_numbers를 다시 초기화합니다.
            st.session_state.available_numbers = list(range(1, st.session_state.max_students + 1))
            # drawn_numbers를 비워줍니다.
            st.session_state.drawn_numbers = []
            st.info("룰렛이 초기화되었습니다.")
            st.rerun() # 앱을 새로고침하여 초기 상태로 돌아갑니다.

# 이 스크립트가 직접 실행될 때 main 함수를 호출합니다.
if __name__ == "__main__":
    main()
