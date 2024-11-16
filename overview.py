import streamlit as st
from vnstock3 import Vnstock
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(layout="wide")
now =  datetime.now().strftime('%Y-%m-%d')
st.title('Phân Tích Cổ phiếu')
st.write('Dashboard phân tích cổ phiếu - Giúp Nhà đầu tư có góc nhìn sâu sắc hơn về doanh nghiệp, công cụ hỗ trợ quan trọng cho mọi Nhà đầu tư')

symbols_df = Vnstock().stock(symbol='ACB', source='VCI').listing.all_symbols()
symbols = symbols_df['ticker'].tolist()

industry = ['Nhóm Ngân Hàng','Nhóm Ngành Khác']
industry_financal = ["ABB", "ACB", "BAB", "BID", "BVB", "CTG", "EIB", "HDB", "KLB", 
     "LPB", "MBB", "MSB", "NAB", "NVB", "OCB", "PGB", "SGB", "SHB", 
     "SSB", "STB", "TCB", "TPB", "VAB", "VBB", "VCB", "VIB"]
industry_non_financal = [symbol for symbol in symbols if symbol not in industry_financal]


col1, col2 = st.columns(2)
with col1:
    selected_industry = st.selectbox('Chọn Ngành:', industry)

with col2:
    if selected_industry == 'Nhóm Ngân Hàng':   
        selected_stock = st.selectbox('Chọn mã cổ phiếu:', industry_financal)
        st.session_state['selected_stock'] = selected_stock
    else:
        selected_stock = st.selectbox('Chọn mã cổ phiếu:', industry_non_financal)
        st.session_state['selected_stock'] = selected_stock
    st.session_state['selected_industry'] = selected_industry

stock = Vnstock().stock(symbol=selected_stock, source='TCBS')
profile = stock.company.profile()
name = profile.iloc[0,0]
st.markdown(f"""
    <h1 style='text-align: center; color: red'>{selected_stock}</h1>
    """, unsafe_allow_html=True)
st.markdown(f"""
    <h4 style='text-align: center;'>{name}</h4>
    """, unsafe_allow_html=True)