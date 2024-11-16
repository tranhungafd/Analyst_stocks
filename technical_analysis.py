
from vnstock3 import Vnstock
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
import pandas as pd

now = datetime.now().strftime('%Y-%m-%d')
st.title('Biểu đồ nến theo cổ phiếu')

selected_stock = st.session_state['selected_stock']
stock = Vnstock().stock(symbol=selected_stock, source='TCBS')

# Hàm lấy và vẽ dữ liệu
df = pd.read_csv('list_stock.csv')
df['Stock'] = df['Stock'][::-1].reset_index(drop=True)

matching_rows = df[df['Stock'] == selected_stock]
date = '2010-01-01'
start_date = ''
if not matching_rows.empty:
    start_date = matching_rows['Date'].values[0]
else:
    start_date = date

def load_data():
    data = stock.quote.history(start=start_date, end=now, interval='1D')
    data['time'] = pd.to_datetime(data['time'])

    # Tính SMA (ví dụ SMA 20)
    data['SMA_20'] = data['close'].rolling(window=20).mean()

    # Tính MACD
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # Vẽ biểu đồ nến
    fig = go.Figure(data=[go.Candlestick(x=data['time'], open=data['open'],
                                         high=data['high'],
                                         low=data['low'],
                                         close=data['close'])])
    # Vẽ đường SMA
    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['SMA_20'],
        mode='lines',
        line=dict(color='blue', width=1.5),
        name='SMA 20'
    ))

    # Đặt tiêu đề và nhãn
    fig.update_layout(title=f'Biểu đồ nến của cổ phiếu {selected_stock}',
                      xaxis_title='Ngày giao dịch',
                      yaxis_title='Giá',
                      xaxis_rangeslider_visible=False,
                      yaxis=dict(range=[0, max(data['high'])]),
                      height = 750
    )  
    # Thêm MACD và Signal line
    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['MACD'],
        mode='lines',
        line=dict(color='purple', width=1),
        name='MACD'
    ))
    fig.add_trace(go.Scatter(
        x=data['time'],
        y=data['Signal'],
        mode='lines',
        line=dict(color='orange', width=1, dash='dash'),
        name='Signal Line'
    ))
    # Cập nhật định dạng trục x
    fig.update_xaxes(
        type='date',
        tickformat='%Y-%m-%d',
        ticklabelmode="instant"
    )
    
    st.plotly_chart(fig)
load_data()

