import streamlit as st
import pandas as pd
import FinanceDataReader as fdr
# import datetime
import datetime
import matplotlib.pyplot as plt
import matplotlib 
from io import BytesIO
import plotly.graph_objects as go
import pandas as pd
#한글폰트깨짐 해결책
from matplotlib import font_manager, rc

# 한글 폰트 경로 설정 (여기서는 Windows의 기본 한글 폰트 경로 예시)
font_path = 'C:/Windows/Fonts/malgun.ttf'
font = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font)

# caching
# 인자가 바뀌지 않는 함수 실행 결과를 저장 후 크롬의 임시 저장 폴더에 저장 후 재사용
@st.cache_data
def get_stock_info():
    base_url =  "http://kind.krx.co.kr/corpgeneral/corpList.do"    
    method = "download"
    url = "{0}?method={1}".format(base_url, method)
    df = pd.read_html(url, header=0, encoding='cp949')[0]
    df['종목코드']= df['종목코드'].apply(lambda x: f"{x:06d}")     
    df = df[['회사명','종목코드']]
    return df

def get_ticker_symbol(company_name):     
    df = get_stock_info()
    code = df[df['회사명']==company_name]['종목코드'].values    
    ticker_symbol = code[0]
    return ticker_symbol

#메인 창
st.markdown('# 무슨 주식을 사야 부자가 되려나...')

# 사이드바 작성
with st.sidebar:
    stock_name=st.text_input("회사이름")
    # st.write(stock_name)
    date_range = st.date_input(
        "시작일 - 종료일",
        [datetime.datetime(2019, 1, 1), datetime.datetime(2023, 7, 31)],
        format="YYYY-MM-DD")
    check_button=st.button('주가 데이터 확인')
       

if check_button:
    # 코드 조각 추가
    ticker_symbol = get_ticker_symbol(stock_name)     
    start_p = date_range[0]               
    end_p = date_range[1] + datetime.timedelta(days=1) 
    df = fdr.DataReader(f'KRX:{ticker_symbol}', start_p, end_p)
    df.index = df.index.date
    st.subheader(f"[{stock_name}] 주가 데이터")
    st.dataframe(df.tail(7))

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Open'], name='주가데이터_Open', mode='lines', marker_color='darkgreen'))
    fig.add_trace(go.Scatter(x=df.index, y=df['High'], name='주가데이터_High', mode='lines', marker_color='red'))
    fig.add_trace(go.Scatter(x=df.index, y=df['Low'], name='주가데이터_Low', mode='lines', marker_color='Blue'))
    st.plotly_chart(fig)

    excel_data = BytesIO()      
    csv_data=BytesIO()
    df.to_excel(excel_data)
    df.to_csv(csv_data)

    # 열을 나누어 좌우로 배치
    col1, col2 = st.columns(2)
    with col1:
            st.download_button(
                "CSV 파일 다운로드",
                csv_data,
                file_name='stock_data.csv'
            )
    with col2:
        st.download_button(
            "엑셀 파일 다운로드",
            excel_data,
            file_name='stock_data.xlsx'
        )
else:
    st.write('')