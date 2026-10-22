import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium

# 페이지 설정
st.title("🚇 부산 지하철 역별 이용객 수 지도")

# ① CSV 파일 업로드
uploaded_file = st.file_uploader("busan_subway.csv 파일을 업로드하세요", type=["csv"])

if uploaded_file is not None:
    # 데이터 읽기
    df = pd.read_csv(uploaded_file)
    
    # 이용객수 컬럼을 숫자로 안전하게 변환 (문자열/쉼표 제거 처리)
    df['이용객수'] = pd.to_numeric(df['이용객수'].astype(str).str.replace(',', ''), errors='coerce').fillna(0)

    # 호선별 지정 색상 (1호선 주황, 2호선 초록, 3호선 갈색, 4호선 파랑)
    line_colors = {
        '1호선': '#F26A36',
        '2호선': '#3CB44A',
        '3호선': '#BB8C00',
        '4호선': '#2C8AEC'
    }

    # [호선 필터] multiselect 선택 (버전 호환성을 위해 options/default 안전 처리)
    all_lines = list(df['호선'].unique())
    selected_lines = st.multiselect("보여줄 호선을 선택하세요", options=all_lines, default=all_lines)
    
    # 선택된 호선만 데이터 필터링
    filtered_df = df[df['호선'].isin(selected_lines)]

    # [표] 이용객 상위 5개 역 표시 (st.dataframe 호환용 처리)
    st.subheader("🏆 이용객 수 상위 5개 역")
    top5_df = filtered_df.sort_values(by='이용객수', ascending=False).head(5)
    st.dataframe(top5_df[['호선', '역명', '이용객수']])

    # ② 부산 중심 기본 지도 생성
    m = folium.Map(location=[35.1795543, 129.0756416], zoom_start=11)

    # 필터링된 역별 CircleMarker 추가
    for _, row in filtered_df.iterrows():
        # 이용객수에 비례하는 반지름 계산 (제곱근 사용)
        radius_val = (row['이용객수'] ** 0.5) * 0.08
        
        # 호선별 지정 색상 적용 (기본값 검은색)
        marker_color = line_colors.get(str(row['호선']), 'black')
        
        # ③ 마우스 Hover시 역명, 클릭시 이용객 수 표시
        folium.CircleMarker(
            location=[float(row['위도']), float(row['경도'])],
            radius=max(radius_val, 2),  # 최소 크기 보장
            color=marker_color,
            fill=True,
            fill_color=marker_color,
            fill_opacity=0.6,
            tooltip=f"{row['호선']} {row['역명']}",
            popup=f"{row['역명']} 이용객 수: {int(row['이용객수']):,}명"
        ).add_to(m)

    # 지도 표시
    st.subheader("🗺️ 역별 이용객 수 지도")
    st_folium(m, width=700, height=500)