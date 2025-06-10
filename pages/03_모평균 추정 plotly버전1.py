import streamlit as st
import numpy as np
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(layout="wide")

st.title("📊 모평균 추정 시각화 활동지")
st.markdown("---")

st.sidebar.header("설정")
population_mean = st.sidebar.slider("모평균 ($\mu$)", 0, 100, 50)
population_std = st.sidebar.slider("모표준편차 ($\sigma$)", 1, 30, 10)
sample_size = st.sidebar.slider("표본 크기 (n)", 5, 200, 30)
num_samples = st.sidebar.slider("표본 추출 횟수", 10, 1000, 100)
confidence_level = st.sidebar.slider("신뢰수준 (%)", 80, 99, 95)

st.sidebar.markdown("---")
st.sidebar.info(
    "이 활동지는 모평균 추정의 원리를 시각적으로 이해하는 데 도움을 줍니다.\n\n"
    "왼쪽 사이드바에서 모수와 표본 추출 조건을 변경하며 결과를 관찰해 보세요."
)

st.header("1. 모집단 분포")
st.markdown(
    "모집단은 정규 분포를 따른다고 가정합니다. 아래 그래프는 여러분이 설정한 모평균과 모표준편차에 따른 모집단 분포를 보여줍니다."
)

x_population = np.linspace(population_mean - 4 * population_std, population_mean + 4 * population_std, 500)
y_population = stats.norm.pdf(x_population, population_mean, population_std)

fig_population = go.Figure(data=go.Scatter(x=x_population, y=y_population, mode='lines', name='모집단 분포', fill='tozeroy'))
fig_population.update_layout(title="모집단 정규 분포",
                             xaxis_title="값",
                             yaxis_title="확률 밀도",
                             height=400,
                             xaxis_range=[-50, 150]) # 모집단 분포의 x축 범위를 고정
st.plotly_chart(fig_population, use_container_width=True)

st.header("2. 표본 추출 및 표본 평균 분포 (중심 극한 정리)")
st.markdown(
    "모집단에서 여러 번 표본을 추출하고 각 표본의 평균을 계산합니다. 표본 평균들의 분포가 어떻게 변하는지 확인해 보세요. "
    "**표본의 크기가 커질수록 표본 평균의 분포는 모집단 분포와 관계없이 정규 분포에 가까워지며, 그 분산이 작아져 더 좁아집니다.** (중심 극한 정리)"
)

sample_means = []
for _ in range(num_samples):
    sample = np.random.normal(population_mean, population_std, sample_size)
    sample_means.append(np.mean(sample))

fig_sample_means = go.Figure()
fig_sample_means.add_trace(go.Histogram(x=sample_means, nbinsx=30, name='표본 평균 분포', marker_color='lightblue'))
fig_sample_means.add_vline(x=population_mean, line_dash="dash", line_color="red", annotation_text=f"모평균 ($\mu$) = {population_mean:.2f}")

# 표본 평균의 평균과 표준오차 계산
mean_of_sample_means = np.mean(sample_means)
std_error_of_mean = population_std / np.sqrt(sample_size)
st.write(f"**표본 평균의 평균**: {mean_of_sample_means:.2f}")
st.write(f"**표본 평균의 표준편차 (표준오차)**: {std_error_of_mean:.2f}")

# 표본 평균 분포의 x축 범위를 고정하여 분산 변화를 시각적으로 명확하게 보여줍니다.
# 이제 x축 범위는 25에서 75사이로 고정됩니다.
fixed_x_min_sampling = 25
fixed_x_max_sampling = 75

fig_sample_means.update_layout(title="표본 평균의 분포 (샘플링 분포)",
                               xaxis_title="표본 평균",
                               yaxis_title="빈도",
                               height=400,
                               xaxis_range=[fixed_x_min_sampling, fixed_x_max_sampling]) # 고정된 x축 범위 적용
st.plotly_chart(fig_sample_means, use_container_width=True)

st.header("3. 신뢰구간")
st.markdown(
    "우리는 하나의 표본을 통해 모평균을 추정합니다. 신뢰구간은 우리가 계산한 표본 평균이 모평균을 포함할 것으로 '신뢰'하는 구간입니다. "
    "신뢰수준이 높을수록 신뢰구간은 넓어집니다."
)

st.subheader("하나의 표본에서 신뢰구간 계산")

# 하나의 표본 추출
np.random.seed(42) # 재현성을 위해 시드 고정
single_sample = np.random.normal(population_mean, population_std, sample_size)
single_sample_mean = np.mean(single_sample)
single_sample_std = np.std(single_sample, ddof=1) # 표본 표준편차 (n-1 자유도)

st.write(f"**추출된 하나의 표본 평균**: {single_sample_mean:.2f}")
st.write(f"**추출된 하나의 표본 표준편차**: {single_sample_std:.2f}")

# t-분포를 사용한 신뢰구간 계산 (모표준편차를 모르는 경우)
degrees_freedom = sample_size - 1
alpha = 1 - (confidence_level / 100)
t_critical = stats.t.ppf(1 - alpha / 2, degrees_freedom)

margin_of_error = t_critical * (single_sample_std / np.sqrt(sample_size))
confidence_interval_lower = single_sample_mean - margin_of_error
confidence_interval_upper = single_sample_mean + margin_of_error

st.write(f"**선택된 신뢰수준**: {confidence_level}%")
st.write(f"**오차 한계 (Margin of Error)**: {margin_of_error:.2f}")
st.success(f"**{confidence_level}% 신뢰구간**: [{confidence_interval_lower:.2f}, {confidence_interval_upper:.2f}]")

fig_confidence_interval = go.Figure()
fig_confidence_interval.add_trace(go.Scatter(
    x=[confidence_interval_lower, confidence_interval_upper],
    y=[0, 0],
    mode='lines',
    line=dict(color='blue', width=4),
    name=f'{confidence_level}% 신뢰구간'
))
fig_confidence_interval.add_trace(go.Scatter(
    x=[single_sample_mean],
    y=[0],
    mode='markers',
    marker=dict(size=10, color='red'),
    name='표본 평균'
))
fig_confidence_interval.add_vline(x=population_mean, line_dash="dash", line_color="green", annotation_text=f"모평균 = {population_mean:.2f}")

# 신뢰구간 그래프는 계산된 구간 자체를 명확하게 보여주기 위해 x축 범위를 동적으로 유지합니다.
fig_confidence_interval.update_layout(title=f"하나의 표본에서 계산된 {confidence_level}% 신뢰구간",
                                       xaxis_title="값",
                                       yaxis_title="",
                                       yaxis_range=[-0.1, 0.1],
                                       showlegend=True,
                                       height=300)
st.plotly_chart(fig_confidence_interval, use_container_width=True)

st.subheader("여러 개의 표본에 대한 신뢰구간")
st.markdown(
    "여러 개의 표본을 추출하여 각각의 신뢰구간을 계산했을 때, 신뢰수준만큼의 신뢰구간이 실제로 모평균을 포함하는지 확인해 보세요."
)

num_ci_samples = st.slider("신뢰구간을 그릴 표본 개수", 10, 100, 20)
st.button("새로운 신뢰구간 그리기", key="draw_new_cis")

ci_data = []
contained_count = 0
for i in range(num_ci_samples):
    sample = np.random.normal(population_mean, population_std, sample_size)
    sample_mean = np.mean(sample)
    sample_std = np.std(sample, ddof=1)

    degrees_freedom_ci = sample_size - 1
    alpha_ci = 1 - (confidence_level / 100)
    t_critical_ci = stats.t.ppf(1 - alpha_ci / 2, degrees_freedom_ci)

    margin_of_error_ci = t_critical_ci * (sample_std / np.sqrt(sample_size))
    ci_lower = sample_mean - margin_of_error_ci
    ci_upper = sample_mean + margin_of_error_ci

    contains_mean = (ci_lower <= population_mean <= ci_upper)
    if contains_mean:
        contained_count += 1
    
    ci_data.append({
        'lower': ci_lower,
        'upper': ci_upper,
        'mean': sample_mean,
        'color': 'green' if contains_mean else 'red'
    })

fig_multi_ci = go.Figure()
for i, ci in enumerate(ci_data):
    fig_multi_ci.add_trace(go.Scatter(
        x=[ci['lower'], ci['upper']],
        y=[i, i],
        mode='lines',
        line=dict(color=ci['color'], width=2),
        showlegend=False
    ))
    fig_multi_ci.add_trace(go.Scatter(
        x=[ci['mean']],
        y=[i],
        mode='markers',
        marker=dict(size=5, color='black'),
        showlegend=False
    ))

# 여러 신뢰구간 그래프 역시 각 구간의 명확한 표현을 위해 동적 x축 범위를 사용합니다.
# 다만, 모든 구간이 잘 보이도록 계산된 구간의 최소/최대 값에 기반하여 범위를 조정합니다.
if ci_data: # ci_data가 비어있지 않은 경우에만 계산
    all_ci_points = [point['lower'] for point in ci_data] + [point['upper'] for point in ci_data]
    ci_plot_x_min = min(all_ci_points) - (max(all_ci_points) - min(all_ci_points)) * 0.1 # 10% 버퍼
    ci_plot_x_max = max(all_ci_points) + (max(all_ci_points) - min(all_ci_points)) * 0.1 # 10% 버퍼
else: # ci_data가 비어있으면 기본 범위 설정
    ci_plot_x_min = population_mean - 20
    ci_plot_x_max = population_mean + 20

fig_multi_ci.add_vline(x=population_mean, line_dash="dash", line_color="blue", annotation_text="모평균")
fig_multi_ci.update_layout(title="여러 표본에 대한 신뢰구간",
                           xaxis_title="값",
                           yaxis_title="표본 번호",
                           height=min(600, num_ci_samples * 20 + 100),
                           showlegend=False,
                           xaxis_range=[ci_plot_x_min, ci_plot_x_max]) # 동적 x축 범위 적용
st.plotly_chart(fig_multi_ci, use_container_width=True)

st.write(f"**모평균을 포함하는 신뢰구간의 수**: {contained_count} / {num_ci_samples}")
st.write(f"**모평균 포함 비율**: {contained_count / num_ci_samples * 100:.2f}%")
st.info(f"이 비율은 설정한 신뢰수준({confidence_level}%)에 가까워져야 합니다.")


st.header("4. 활동지 마무리 및 질문")
st.markdown(
    "이 활동을 통해 모평균 추정에 대해 무엇을 배우셨나요? 아래 질문에 답해보세요."
)
st.subheader("질문 1: 표본의 크기가 커질수록 표본 평균의 분포는 어떻게 변하나요?")
st.text_area("답변", key="q1")

st.subheader("질문 2: 신뢰수준을 높이면 신뢰구간은 어떻게 변하며, 그 이유는 무엇인가요?")
st.text_area("답변", key="q2")

st.subheader("질문 3: 여러 개의 표본에서 계산된 신뢰구간 중 실제로 모평균을 포함하는 비율이 신뢰수준과 비슷하게 나오는 이유를 설명해 보세요.")
st.text_area("답변", key="q3")

st.subheader("자유롭게 궁금한 점이나 의견을 남겨주세요.")
st.text_area("자유로운 의견", key="q4")

st.markdown("---")
st.markdown("© 2025 모평균 추정 시각화 활동지")
