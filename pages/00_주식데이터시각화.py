# app.py

import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Streamlit 페이지 설정: 전체 너비 사용
st.set_page_config(layout="wide")

# 앱의 제목과 설명
st.title("글로벌 시가총액 상위 기업 최근 3년간 주가 변화")
st.markdown("""
이 앱은 `yfinance` 라이브러리를 사용하여 글로벌 시가총액 상위 기업들의 최근 3년간 주가 변화를 시각화합니다.
**주의:** 아래 기업 리스트는 예시이며, 실시간 시가총액 상위 10개 기업과는 다를 수 있습니다.
앱 실행 전에 정확한 최신 티커 리스트로 업데이트하는 것을 권장합니다.
""")

# 글로벌 시가총액 상위권에 있을 가능성이 높은 기업들 (예시)
# 실제 사용 시에는 이 리스트를 최신 정보로 업데이트해야 합니다.
# 한국 기업을 추가하려면 "005930.KS" (삼성전자) 와 같이 ".KS"를 붙여야 합니다.
# TICKERS를 딕셔너리 형태로 변경하여 티커와 전체 기업명을 매핑합니다.
TICKERS = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corp.",
    "GOOGL": "Alphabet Inc. (Class A)",
    "AMZN": "Amazon.com Inc.",
    "NVDA": "NVIDIA Corp.",
    "META": "Meta Platforms Inc.",
    "TSLA": "Tesla Inc.",
    "BRK-A": "Berkshire Hathaway Inc. (Class A)",
    "JPM": "JPMorgan Chase & Co.",
    "LLY": "Eli Lilly and Company",
    # "005930.KS": "Samsung Electronics Co., Ltd.", # 예시: 삼성전자
}

# yfinance에 전달할 티커 목록 (딕셔너리의 키 값들)
yf_tickers = list(TICKERS.keys())

# 최근 3년 데이터 가져오기 위한 날짜 설정
end_date = datetime.now()
start_date = end_date - timedelta(days=3 * 365) # 대략 3년 전

# yfinance를 사용하여 주가 데이터를 가져오는 함수
# @st.cache_data 데코레이터를 사용하여 데이터를 캐싱하여 앱 성능 향상
@st.cache_data
def get_stock_data(tickers, start, end):
    """
    주어진 티커 리스트에 대해 yfinance에서 주가 데이터를 다운로드합니다.
    """
    # yfinance.download는 멀티인덱스 DataFrame을 반환합니다.
    # group_by='ticker'를 사용하면 각 티커별로 데이터가 그룹화됩니다.
    data = yf.download(tickers, start=start, end=end, group_by='ticker')
    return data

# 주가 데이터 가져오기
stock_data = get_stock_data(yf_tickers, start_date, end_date)

# 데이터가 성공적으로 로드되었는지 확인
if not stock_data.empty:
    # 각 기업의 'Close' (종가) 가격만 추출하여 하나의 DataFrame으로 결합
    close_prices = pd.DataFrame()
    for ticker in yf_tickers:
        # yfinance 다운로드 결과는 멀티인덱스 컬럼을 가질 수 있습니다.
        # 각 티커의 'Close' 가격을 올바르게 참조합니다.
        if (ticker, 'Close') in stock_data.columns:
            close_prices[ticker] = stock_data[(ticker, 'Close')]
        elif ticker in stock_data.columns: # 단일 티커 요청 시 컬럼이 단일 레벨일 수 있음
             close_prices[ticker] = stock_data[ticker]['Close']
        else:
            st.warning(f"티커 '{ticker}'의 데이터를 가져오지 못했습니다. 올바른 티커인지 확인해주세요.")

    if not close_prices.empty:
        # 결측치 제거 (주말, 공휴일 등으로 데이터가 없는 경우)
        close_prices = close_prices.dropna()

        # close_prices DataFrame의 컬럼 이름을 전체 기업명으로 변경
        # 이렇게 하면 그래프의 범례와 호버 텍스트에 전체 기업명이 표시됩니다.
        close_prices.rename(columns=TICKERS, inplace=True)

        # 주가 변화율 계산 (첫 번째 날짜의 가격을 100으로 정규화)
        # 이를 통해 각 기업의 상대적인 성과를 비교하기 용이합니다.
        # .iloc[0]은 DataFrame의 첫 번째 행(즉, 첫 번째 날짜의 가격)을 가져옵니다.
        normalized_prices = close_prices / close_prices.iloc[0] * 100

        # --- 정규화된 주가 변화 시각화 ---
        st.subheader("최근 3년간 주가 변화 (정규화된 값, 시작일=100)")
        # Plotly Express를 사용하여 대화형 라인 차트 생성
        fig_normalized = px.line(
            normalized_prices,
            x=normalized_prices.index, # x축: 날짜
            y=normalized_prices.columns, # y축: 각 기업의 전체 기업명
            title="글로벌 시가총액 상위 기업 최근 3년간 주가 변화 (시작일 기준 100)",
            labels={"value": "주가 (시작일 기준 100)", "index": "날짜", "variable": "기업"},
            hover_name="variable" # 마우스 오버 시 기업 이름 표시
        )
        # 마우스 오버 시 모든 라인 정보 표시
        fig_normalized.update_layout(
            hovermode="x unified",
            # height=600, # 차트 높이 증가 설정 제거
            legend=dict(
                orientation="v", # 범례를 수직으로 정렬
                xanchor="left",  # x축 앵커를 왼쪽으로 설정
                x=1.02,          # 차트 영역 바깥, 오른쪽에 위치 (여백 추가)
                yanchor="top",   # y축 앵커를 위쪽으로 설정
                y=1              # 차트 영역 상단에 위치
            ),
            margin=dict(l=0, r=180, t=30, b=0) # 오른쪽 여백을 늘려 범례 공간 확보
        )
        # Streamlit에 Plotly 차트 표시 (컨테이너 너비에 맞춤)
        st.plotly_chart(fig_normalized, use_container_width=True)

        # --- 실제 주가 (종가) 시각화 ---
        st.subheader("실제 주가 (종가)")
        fig_raw = px.line(
            close_prices,
            x=close_prices.index,
            y=close_prices.columns,
            title="글로벌 시가총액 상위 기업 실제 주가",
            labels={"value": "종가", "index": "날짜", "variable": "기업"},
            hover_name="variable"
        )
        fig_raw.update_layout(
            hovermode="x unified",
            # height=600, # 차트 높이 증가 설정 제거
            legend=dict(
                orientation="v", # 범례를 수직으로 정렬
                xanchor="left",  # x축 앵커를 왼쪽으로 설정
                x=1.02,          # 차트 영역 바깥, 오른쪽에 위치 (여백 추가)
                yanchor="top",   # y축 앵커를 위쪽으로 설정
                y=1              # 차트 영역 상단에 위치
            ),
            margin=dict(l=0, r=180, t=30, b=0) # 오른쪽 여백을 늘려 범례 공간 확보
        )
        st.plotly_chart(fig_raw, use_container_width=True)

        # --- 개별 기업 주가 데이터 보기 ---
        st.subheader("개별 기업 주가 데이터 자세히 보기")
        # 사용자가 드롭다운 메뉴에서 기업을 선택하도록 허용 (전체 기업명 표시)
        selected_company_name = st.selectbox("기업을 선택하세요:", list(TICKERS.values()))

        if selected_company_name:
            # 선택된 기업명에 해당하는 티커를 찾음
            selected_ticker = next((ticker for ticker, name in TICKERS.items() if name == selected_company_name), None)

            if selected_ticker and selected_company_name in close_prices.columns:
                st.write(f"**{selected_company_name} 주가 데이터 (최근 3년 종가):**")
                
                # 선택된 기업의 종가 Series를 DataFrame으로 변환하고 인덱스를 리셋하여 'Date' 컬럼으로 만듦
                individual_df = pd.DataFrame(close_prices[selected_company_name]).reset_index()
                # 컬럼 이름 명확히 설정 (첫 번째 컬럼은 날짜, 두 번째 컬럼은 기업명)
                individual_df.columns = ['Date', selected_company_name]
                
                # plotly.express.line을 사용하여 개별 기업 차트 생성
                # trendline="ols"를 추가하여 추세선 표현
                fig_individual = px.line(
                    individual_df,
                    x="Date", # 'Date' 컬럼 사용
                    y=selected_company_name, # 단일 컬럼의 이름 (기업명)
                    title=f"{selected_company_name} 주가",
                    labels={"value": "종가", "Date": "날짜"}, # 라벨도 'Date'로 변경
                    trendline="ols" # OLS(최소제곱법) 기반 추세선 추가
                )
                fig_individual.update_layout(hovermode="x unified")
                st.plotly_chart(fig_individual, use_container_width=True)

                st.write(f"**{selected_company_name} 원본 데이터 (상위 5개 행):**")
                # 원본 stock_data는 티커를 키로 사용하므로 selected_ticker를 사용
                st.dataframe(stock_data[selected_ticker].head())
            else:
                st.info(f"선택하신 '{selected_company_name}'의 주가 데이터를 찾을 수 없습니다. 티커를 확인해주세요.")

    else:
        st.error("선택된 기업들의 유효한 주가 데이터를 가져오는 데 실패했습니다. 티커 리스트를 확인하거나, 데이터가 존재하지 않을 수 있습니다.")
else:
    st.error("주가 데이터를 가져오는 데 실패했습니다. 인터넷 연결 상태나 티커 리스트가 올바른지 확인해주세요.")
