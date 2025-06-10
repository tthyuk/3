import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

st.set_page_config(layout="wide")

st.title("신뢰구간 추정의 원리 시각화")

st.sidebar.header("파라미터 설정")

# 사용자 입력 파라미터
pop_mean = st.sidebar.slider("모집단 평균 (μ)", 0, 100, 50)
pop_std = st.sidebar.slider("모집단 표준편차 (σ)", 1, 30, 10)
sample_size = st.sidebar.slider("표본 크기 (n)", 5, 200, 30)
num_samples = st.sidebar.slider("추출할 표본 개수", 10, 1000, 50)
confidence_level = st.sidebar.slider("신뢰수준 (%)", 80, 99, 95)
show_details = st.sidebar.checkbox("세부 정보 표시", False)

st.markdown(f"""
이 앱은 **신뢰구간(Confidence Interval)**의 원리를 시각적으로 설명합니다.
모집단에서 여러 번 표본을 추출하고, 각 표본으로부터 모집단 평균에 대한 신뢰구간을 추정합니다.
이를 통해 신뢰수준의 의미와 신뢰구간이 어떻게 변동하는지 이해할 수 있습니다.

**설정된 파라미터:**
* **모집단 평균 (μ)**: `{pop_mean}`
* **모집단 표준편차 (σ)**: `{pop_std}`
* **표본 크기 (n)**: `{sample_size}`
* **추출할 표본 개수**: `{num_samples}`
* **신뢰수준**: `{confidence_level}%`
---
""")

# 모집단 데이터 생성 (시뮬레이션)
np.random.seed(42) # 재현성을 위해 시드 고정
population = np.random.normal(loc=pop_mean, scale=pop_std, size=100000)

st.header("1. 모집단 분포")
fig_pop, ax_pop = plt.subplots(figsize=(10, 5))
ax_pop.hist(population, bins=50, density=True, alpha=0.6, color='g', label='모집단 분포')
ax_pop.axvline(pop_mean, color='r', linestyle='dashed', linewidth=2, label=f'모집단 평균 (μ={pop_mean})')
ax_pop.set_title("모집단 분포 시뮬레이션")
ax_pop.set_xlabel("값")
ax_pop.set_ylabel("밀도")
ax_pop.legend()
st.pyplot(fig_pop)
st.write("모집단은 정규분포를 따른다고 가정하고 시뮬레이션했습니다.")

st.header("2. 표본 추출 및 신뢰구간 추정")

# 신뢰구간 계산을 위한 Z-값 또는 T-값
# 표본 크기가 충분히 크고 모집단 표준편차를 알면 Z-분포 사용
# 모집단 표준편차를 모를 경우 (일반적인 경우) T-분포 사용
# 여기서는 일반적인 상황을 가정하여 T-분포 사용
alpha = 1 - (confidence_level / 100)
# 자유도는 n-1
t_critical = stats.t.ppf(1 - alpha / 2, df=sample_size - 1)

covered_count = 0
results = [] # 각 표본의 결과 저장

fig_ci, ax_ci = plt.subplots(figsize=(12, 10))
ax_ci.axvline(pop_mean, color='red', linestyle='--', label=f'모집단 평균 (μ={pop_mean})')
ax_ci.set_xlabel("값")
ax_ci.set_ylabel("표본")
ax_ci.set_title(f"각 표본의 {confidence_level}% 신뢰구간")
ax_ci.set_xlim(pop_mean - 3 * pop_std, pop_mean + 3 * pop_std) # x축 범위 조정

for i in range(num_samples):
    sample = np.random.choice(population, size=sample_size, replace=False)
    sample_mean = np.mean(sample)
    sample_std = np.std(sample, ddof=1) # 표본 표준편차 (n-1로 나눔)
    
    # 표준 오차 (Standard Error)
    se = sample_std / np.sqrt(sample_size)
    
    # 신뢰구간 계산
    margin_of_error = t_critical * se
    lower_bound = sample_mean - margin_of_error
    upper_bound = sample_mean + margin_of_error
    
    # 모집단 평균이 신뢰구간에 포함되는지 확인
    is_covered = (lower_bound <= pop_mean <= upper_bound)
    if is_covered:
        covered_count += 1
        color = 'green'
    else:
        color = 'red'
        
    # 시각화
    ax_ci.plot([lower_bound, upper_bound], [i, i], color=color, linewidth=2)
    ax_ci.plot(sample_mean, i, 'o', color='blue', markersize=5) # 표본 평균 표시
    
    results.append({
        "표본 번호": i + 1,
        "표본 평균": f"{sample_mean:.2f}",
        "하한": f"{lower_bound:.2f}",
        "상한": f"{upper_bound:.2f}",
        "모집단 포함 여부": "O" if is_covered else "X"
    })

ax_ci.legend()
st.pyplot(fig_ci)

coverage_percentage = (covered_count / num_samples) * 100

st.markdown(f"""
### 신뢰구간 포함 비율
* 총 추출된 표본 개수: **{num_samples}개**
* 모집단 평균을 포함하는 신뢰구간 개수: **{covered_count}개**
* **신뢰구간이 모집단 평균을 포함하는 비율: {coverage_percentage:.2f}%**

이 비율은 설정된 신뢰수준({confidence_level}%)에 가까워야 합니다. 이는 신뢰수준이 "동일한 방식으로 무한히 많은 신뢰구간을 만들었을 때, 그 중 몇 %가 실제 모수를 포함할 것인가"를 의미하기 때문입니다.
""")

if show_details:
    st.subheader("개별 표본 신뢰구간 상세 정보")
    st.dataframe(results)

st.header("3. 추가 설명")
st.markdown("""
### 신뢰구간이란?
신뢰구간은 표본 통계량(예: 표본 평균)으로부터 추정된 모수(예: 모집단 평균)가 포함될 것이라고 기대되는 구간입니다.
예를 들어, 95% 신뢰구간은 동일한 방식으로 100개의 신뢰구간을 만들었을 때, 약 95개의 신뢰구간이 실제 모집단 평균을 포함할 것이라는 의미입니다.

### 핵심 개념
* **모집단 평균 (μ)**: 우리가 알고자 하는 실제 값입니다. 하지만 현실에서는 이 값을 알기 어렵습니다.
* **표본 평균 (x̄)**: 모집단에서 추출한 표본들의 평균입니다. 이는 모집단 평균의 추정치로 사용됩니다.
* **표본 표준편차 (s)**: 표본 데이터의 퍼짐 정도를 나타냅니다.
* **표준 오차 (SE)**: 표본 평균의 표준 편차입니다. `s / sqrt(n)`으로 계산됩니다.
* **신뢰수준 (Confidence Level)**: 신뢰구간이 모수를 포함할 확률입니다. 일반적으로 90%, 95%, 99% 등을 사용합니다.
* **임계값 (Critical Value)**: 신뢰수준에 따라 결정되는 값으로, Z-분포나 T-분포에서 가져옵니다.

### 신뢰구간 계산 공식 (모집단 표준편차를 모를 경우, T-분포 사용)
$신뢰구간 = 표본 평균 \pm (임계값 \times 표준 오차)$

$CI = \bar{x} \pm t_{\alpha/2, n-1} \times \frac{s}{\sqrt{n}}$

여기서:
* $\bar{x}$는 표본 평균
* $t_{\alpha/2, n-1}$는 자유도가 $n-1$이고 유의수준이 $\alpha$일 때 T-분포의 임계값
* $s$는 표본 표준편차
* $n$은 표본 크기

이 시각화는 신뢰구간의 확률적인 특성을 이해하는 데 도움이 됩니다.
""")
