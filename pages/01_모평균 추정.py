import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

st.set_page_config(layout="wide")

st.title("📊 모평균 추정 시각화 활동지")
st.markdown("---")

st.sidebar.header("모집단 및 실험 설정")

# 1. 모집단 설정
st.sidebar.subheader("1. 모집단 설정")
population_mean = st.sidebar.slider("모집단 평균 (μ)", min_value=50, max_value=150, value=100, step=1)
population_std = st.sidebar.slider("모집단 표준편차 (σ)", min_value=5, max_value=30, value=15, step=1)
population_size = 100000 # 가상의 모집단 크기 (충분히 크게 설정)

st.sidebar.markdown(f"**현재 모집단:** 정규분포 $N(\\mu={population_mean}, \\sigma={population_std})$")

# 2. 표본 추출 설정
st.sidebar.subheader("2. 표본 추출 설정")
sample_size = st.sidebar.slider("표본 크기 (n)", min_value=5, max_value=100, value=30, step=5)
num_samples = st.sidebar.slider("표본 추출 횟수", min_value=100, max_value=5000, value=1000, step=100)

st.markdown(f"""
안녕하세요! 이 활동지에서는 **모평균 추정의 원리**를 시각적으로 학습할 수 있습니다.
오른쪽 사이드바에서 모집단의 특성과 표본 추출 조건을 변경하면서 어떤 변화가 나타나는지 직접 확인해보세요.

**🤔 무엇을 배울 수 있나요?**
* **표본 평균의 분포**: 표본을 여러 번 추출했을 때 표본 평균들이 어떻게 분포하는지 관찰합니다.
* **중심극한정리**: 표본의 크기가 커질수록 표본 평균의 분포가 정규분포에 가까워지고 모집단 평균에 수렴함을 이해합니다.
* **신뢰구간**: 표본 정보를 이용하여 모평균이 포함될 것이라고 '믿을 수 있는' 구간을 어떻게 추정하는지 알아봅니다.
""")
st.markdown("---")

# 모집단 데이터 생성 (시각화용)
population_data = np.random.normal(population_mean, population_std, population_size)

col1, col2 = st.columns(2)

with col1:
    st.subheader("모집단 분포")
    fig_pop, ax_pop = plt.subplots(figsize=(8, 5))
    ax_pop.hist(population_data, bins=50, density=True, alpha=0.6, color='skyblue', edgecolor='black')
    ax_pop.axvline(population_mean, color='red', linestyle='dashed', linewidth=2, label=f'모집단 평균 (μ={population_mean})')
    ax_pop.set_title("모집단 분포 (가상)")
    ax_pop.set_xlabel("값")
    ax_pop.set_ylabel("밀도")
    ax_pop.legend()
    st.pyplot(fig_pop)
    st.markdown("""
    위 그래프는 우리가 알 수 없는 **모집단의 분포**를 가상으로 보여줍니다.
    우리의 목표는 이 모집단의 평균(빨간색 점선)을 **모르더라도** 표본을 통해 추정하는 것입니다.
    """)

# 표본 추출 및 표본 평균 계산
sample_means = []
for _ in range(num_samples):
    sample = np.random.choice(population_data, size=sample_size, replace=False)
    sample_means.append(np.mean(sample))

with col2:
    st.subheader(f"표본 평균 분포 (n={sample_size}, 추출 횟수={num_samples})")
    fig_sample_means, ax_sample_means = plt.subplots(figsize=(8, 5))
    ax_sample_means.hist(sample_means, bins=30, density=True, alpha=0.7, color='lightgreen', edgecolor='black')
    ax_sample_means.axvline(np.mean(sample_means), color='blue', linestyle='dashed', linewidth=2, label=f'표본 평균들의 평균 ({np.mean(sample_means):.2f})')
    ax_sample_means.axvline(population_mean, color='red', linestyle='dashed', linewidth=2, label=f'모집단 평균 ({population_mean})')
    ax_sample_means.set_title("표본 평균들의 분포")
    ax_sample_means.set_xlabel("표본 평균")
    ax_sample_means.set_ylabel("밀도")
    ax_sample_means.legend()
    st.pyplot(fig_sample_means)
    st.markdown(f"""
    이 그래프는 모집단에서 **표본을 {num_samples}번 추출**하여 얻은 **표본 평균들의 분포**를 보여줍니다.
    **중심극한정리**에 따르면, 표본의 크기($n$)가 충분히 커질수록 표본 평균들의 분포는 모집단의 분포와 상관없이 **정규분포**에 가까워지며,
    그 평균은 모집단 평균($\\mu$)과 같아지고, 표준편차는 $\\sigma / \\sqrt{{n}}$이 됩니다.
    """)
    st.markdown(f"**관찰:** 표본 평균들의 평균($\\bar{{\\bar{{X}}}} \\approx {np.mean(sample_means):.2f}$)이 모집단 평균($\\mu = {population_mean}$)에 가까워지는 것을 확인할 수 있습니다.")
    st.markdown(f"**이론적인 표본 평균의 표준편차 (표준오차):** $\\sigma / \\sqrt{{n}} = {population_std} / \\sqrt{{{sample_size}}} \\approx {(population_std / np.sqrt(sample_size)):.2f}$")
    st.markdown(f"**실제 표본 평균들의 표준편차:** ${np.std(sample_means):.2f}$")

st.markdown("---")
st.subheader("모평균 신뢰구간 추정")

st.markdown("""
이제 하나의 표본을 가지고 모집단의 평균을 추정하는 **신뢰구간**에 대해 알아보겠습니다.
우리는 하나의 표본 평균을 이용하여 모평균이 있을 것으로 '믿을 수 있는' 구간을 계산합니다.
""")

confidence_level = st.slider("신뢰수준 (%)", min_value=80, max_value=99, value=95, step=1)

# 하나의 표본 추출 및 신뢰구간 계산 (가장 최근에 추출된 표본 평균 중 하나를 사용하거나 새로 추출)
# 여기서는 가장 최근에 추출된 sample_means 리스트의 마지막 표본 평균을 사용하거나,
# 사용자가 '새로운 표본으로 계산' 버튼을 누르면 새로운 표본으로 계산하도록 할 수 있습니다.
# 여기서는 단순화를 위해 sample_means 중 하나를 임의로 선택하거나 새로 추출
if 'current_sample' not in st.session_state:
    st.session_state.current_sample = np.random.choice(population_data, size=sample_size, replace=False)

if st.button("새로운 표본으로 신뢰구간 계산"):
    st.session_state.current_sample = np.random.choice(population_data, size=sample_size, replace=False)

current_sample = st.session_state.current_sample
sample_mean_ci = np.mean(current_sample)
sample_std_ci = np.std(current_sample, ddof=1) # 표본 표준편차 (n-1 자유도)

# z-분포 또는 t-분포 사용 (표본 크기가 30 이상이면 z, 미만이면 t)
# 모집단 표준편차를 알면 z, 모르면 t를 사용하는 것이 원칙이나, 여기서는 모집단 표준편차를 알고 있다는 가정하에 z 사용.
# 실제로는 모르면 t를 사용해야 함. 하지만 활동지 목적상 단순화를 위해 z 사용.
# 만약 모집단 표준편차를 모른다고 가정하면 t-분포 사용:
# if sample_size < 30:
#     t_critical = stats.t.ppf(1 - (100 - confidence_level) / 200, df=sample_size - 1)
#     margin_of_error = t_critical * (sample_std_ci / np.sqrt(sample_size))
# else:
z_critical = stats.norm.ppf(1 - (100 - confidence_level) / 200) # 양측 검정이므로 1 - alpha/2
# 모집단 표준편차를 알고 있다고 가정하면
margin_of_error = z_critical * (population_std / np.sqrt(sample_size)) # 모표준편차 사용

lower_bound = sample_mean_ci - margin_of_error
upper_bound = sample_mean_ci + margin_of_error

st.markdown(f"""
선택된 표본($n={sample_size}$)의 평균($\\bar{{x}}$)은 ${sample_mean_ci:.2f}$ 입니다.

**신뢰구간 계산:**
* **신뢰수준:** ${confidence_level}\\%$
* **임계값 (Z-값):** ${z_critical:.2f}$ (신뢰수준 ${confidence_level}\\%$에 해당하는 양측 Z-값)
* **표준오차 (Standard Error):** $\\sigma / \\sqrt{{n}} = {population_std} / \\sqrt{{{sample_size}}} = {(population_std / np.sqrt(sample_size)):.2f}$
* **오차 한계 (Margin of Error):** 임계값 $\\times$ 표준오차 = ${z_critical:.2f} \\times {(population_std / np.sqrt(sample_size)):.2f} = {margin_of_error:.2f}$

**${confidence_level}\\%$ 신뢰구간:**
$\\bar{{x}} \\pm \\text{{오차 한계}} = {sample_mean_ci:.2f} \\pm {margin_of_error:.2f}$
**$[{lower_bound:.2f}, {upper_bound:.2f}]$**
""")

fig_ci, ax_ci = plt.subplots(figsize=(10, 3))
ax_ci.errorbar(sample_mean_ci, 1, xerr=margin_of_error, fmt='o', color='purple', capsize=5, markersize=8, label=f'${confidence_level}\\%$ 신뢰구간')
ax_ci.axvline(population_mean, color='red', linestyle='dashed', linewidth=2, label=f'모집단 평균 (μ={population_mean})')
ax_ci.set_ylim(0.5, 1.5)
ax_ci.set_xlim(population_mean - 4 * population_std / np.sqrt(sample_size), population_mean + 4 * population_std / np.sqrt(sample_size)) # 적절한 x축 범위 설정
ax_ci.set_yticks([])
ax_ci.set_title(f"모평균 {confidence_level}% 신뢰구간")
ax_ci.set_xlabel("값")
ax_ci.legend()
st.pyplot(fig_ci)

st.markdown(f"""
**해석:** 이 ${confidence_level}\\%$ 신뢰구간은 우리가 표본을 통해 추정한 모평균의 '범위'를 의미합니다.
만약 동일한 방식으로 표본을 100번 추출하여 100개의 신뢰구간을 만든다면, 이론적으로 그 중 약 ${confidence_level}$개의 신뢰구간이 실제 모집단 평균($\\mu={population_mean}$)을 포함할 것으로 기대할 수 있습니다.

**🤔 직접 해보세요!**
* **표본 크기(n)를 바꿔보세요:** 표본 크기가 커지면 표본 평균들의 분포가 어떻게 변하나요? 신뢰구간의 길이는 어떻게 변하나요?
* **표본 추출 횟수를 늘려보세요:** 표본 평균 분포의 모양이 더 정규분포에 가까워지는 것을 확인할 수 있습니다.
* **신뢰수준을 바꿔보세요:** 신뢰수준을 높이면 신뢰구간의 길이는 어떻게 변하나요? (넓어지는지 좁아지는지)
* **'새로운 표본으로 신뢰구간 계산' 버튼을 여러 번 눌러보세요:** 각 표본마다 신뢰구간이 달라지지만, 대부분의 경우 모집단 평균을 포함하는 것을 볼 수 있습니다. (하지만 가끔 포함하지 않을 수도 있습니다!)
""")

st.markdown("---")
st.subheader("마무리 학습")
st.markdown("""
이 활동지를 통해 모평균 추정의 핵심 원리인 **표본 평균의 분포**와 **중심극한정리**, 그리고 **신뢰구간의 의미**를 시각적으로 경험하셨기를 바랍니다.
통계학에서 모수를 추정하는 것은 매우 중요한 과정이며, 이 시각화 도구가 여러분의 이해를 돕는 데 도움이 되었으면 합니다.
""")

st.markdown("---")
st.caption("© 2025 스트림릿을 활용한 통계 학습 활동지")
