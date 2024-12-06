import streamlit as st
from vnstock3 import Vnstock
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from plotly.subplots import make_subplots

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
company = Vnstock().stock(symbol=selected_stock, source='TCBS').company
df = company.shareholders()

col1,spacer2, col2 = st.columns([3,0.5,2])
with col1:
    st.markdown("### **Cơ cấu sở hữu của cổ đông**")
    df['Tỷ lệ'] = df['share_own_percent'] * 100
    total_excluding_other = df[df['share_holder'] != 'Khác']['Tỷ lệ'].sum()
    df.loc[df['share_holder'] == 'Khác', 'Tỷ lệ'] = 100 - total_excluding_other
    df['Tên cổ đông'] = df['share_holder']
    fig = px.pie(
        df, 
        values='Tỷ lệ', 
        names='Tên cổ đông', 
        color_discrete_sequence=px.colors.qualitative.Set3,
    )
    st.plotly_chart(fig, use_container_width=True)
with col2:
    stock = Vnstock().stock(symbol=selected_stock, source='VCI')
    df = stock.finance.ratio(period='year', lang='vi', dropna=True)
    row = df['Chỉ tiêu định giá'].iloc[0]

    # Hiển thị thông tin
    st.markdown("### **Thông tin định giá**")
    st.write(f"**Vốn hóa (Tỷ đồng):** {round(row['Vốn hóa (Tỷ đồng)'],2):,}")
    st.write(f"**Số CP lưu hành (Triệu CP):** {row['Số CP lưu hành (Triệu CP)']:,}")
    st.write(f"**P/E:** {round(row['P/E'],2)}")
    st.write(f"**P/B:** {round(row['P/B'],2)}")
    st.write(f"**P/S:** {round(row['P/S'],2)}")
    st.write(f"**P/Cash Flow:** {round(row['P/E'],2)}")
    st.write(f"**EPS (VND):** {round(row['EPS (VND)'],2):,}")
    st.write(f"**BVPS (VND):** {round(row['BVPS (VND)'],2):,}")
