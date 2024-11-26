from vnstock3 import Vnstock
from datetime import datetime, timedelta
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(layout="wide")

now = datetime.now().strftime('%Y-%m-%d')
st.title('Biểu đồ nến theo cổ phiếu')


selected_stock = st.session_state['selected_stock']
stock = Vnstock().stock(symbol=selected_stock, source='TCBS')

# Đọc dữ liệu từ file CSV
df = pd.read_csv('list_stock.csv')
df['Stock'] = df['Stock'][::-1].reset_index(drop=True)

# Tìm ngày bắt đầu từ dữ liệu
matching_rows = df[df['Stock'] == selected_stock]
date = '2010-01-01'
start_date = ''
if not matching_rows.empty:
    start_date = matching_rows['Date'].values[0]
else:
    start_date = date

# Cập nhật hàm load_data để hỗ trợ thời gian tùy chọn
def load_data(timeframe,now, custom_start, custom_end, show_sma, show_sma50,show_bollinger):
    if timeframe:
        if timeframe == '1Y':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif timeframe == '3Y':
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
        elif timeframe == 'All':
            start_date = date  # To load from 2010 onwards
        else:
            start_date = custom_start  # Sử dụng thời gian người dùng nhập
            now = custom_end  # Thời gian kết thúc người dùng nhập
    
    # Lấy dữ liệu lịch sử cổ phiếu
    data = stock.quote.history(start=start_date, end=now, interval='1D')
    data['time'] = pd.to_datetime(data['time'])
    data = data.drop_duplicates(subset=['time', 'close'], keep='first')

    # Tính toán các chỉ số (SMA, MACD, bollinger)
    data['SMA_20'] = data['close'].rolling(window=20).mean()
    data['SMA_50'] = data['close'].rolling(window=50).mean()
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['Bollinger_Upper'] = data['SMA_20'] + (data['close'].rolling(window=20).std() * 2)
    data['Bollinger_Lower'] = data['SMA_20'] - (data['close'].rolling(window=20).std() * 2)

    fig = go.Figure(data=[go.Candlestick(x=data['time'], open=data['open'],
                                        high=data['high'], low=data['low'], close=data['close'])])

    if show_sma:
        fig.add_trace(go.Scatter(x=data['time'], y=data['SMA_20'], mode='lines', line=dict(color='blue', width=1.5), name='SMA 20'))
    if show_sma50:
        fig.add_trace(go.Scatter(x=data['time'], y=data['SMA_50'], mode='lines', line=dict(color='green', width=1.5), name='SMA 50'))
    if show_bollinger:
        fig.add_trace(go.Scatter(x=data['time'], y=data['Bollinger_Upper'], 
                                mode='lines', line=dict(color='blue', width=0.2), 
                                name='Bollinger Upper'))
        fig.add_trace(go.Scatter(x=data['time'], y=data['Bollinger_Lower'], 
                                mode='lines', line=dict(color='blue', width=0.2), 
                                name='Bollinger Lower', fill='tonexty', fillcolor='rgba(0, 0, 255, 0.05)'))
        fig.update_layout(
            legend=dict(
                orientation="h",  # Đặt legend theo chiều ngang
                yanchor="top",  # Gắn legend vào đỉnh biểu đồ
                y=1,  # Đặt vị trí legend sát phía trên biểu đồ
                xanchor="left",  # Gắn legend vào cạnh trái
                x=0  # Đặt legend tại cạnh trái
            )
        )

    fig.update_layout(
        #title=f'Biểu đồ nến và MACD của cổ phiếu {selected_stock}',
        xaxis_title='Ngày giao dịch',yaxis_title='Giá cổ phiếu',xaxis_rangeslider_visible=False, 
        yaxis=dict(title='Giá cổ phiếu'),xaxis2=dict(title='MACD', overlaying='y', side='right'),height=600,margin=dict(l=0, r=0, t=15, b=0))
    st.plotly_chart(fig)

def macd(timeframe,now, custom_start, custom_end):
    if timeframe:
        if timeframe == '1Y':
            start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
        elif timeframe == '3Y':
            start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
        elif timeframe == 'All':
            start_date = date  
        else:
            start_date = custom_start  
            now = custom_end  
    data = stock.quote.history(start=start_date, end=now, interval='1D')
    data['time'] = pd.to_datetime(data['time'])
    data = data.drop_duplicates(subset=['time', 'close'], keep='first')
    data['EMA_12'] = data['close'].ewm(span=12, adjust=False).mean()
    data['EMA_26'] = data['close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA_12'] - data['EMA_26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    data['Histogram'] = data['MACD'] - data['Signal']


    fig = go.Figure()
    fig.add_trace(
        go.Bar(x=data['time'],y=data['Histogram'], 
            marker_color=data['Histogram'].apply(lambda x: 'green' if x >= 0 else 'red'), name='MACD Histogram'))
    fig.add_trace(
        go.Scatter(x=data['time'],y=data['MACD'],mode='lines',line=dict(color='purple', width=1),name='MACD'))
    fig.add_trace(
        go.Scatter(
            x=data['time'],y=data['Signal'],mode='lines',line=dict(color='orange', width=1, dash='dash'),name='Signal Line'))
    fig.update_layout(
        xaxis_title="Ngày giao dịch",
        yaxis_title="Giá trị MACD",
        height=300,xaxis_rangeslider_visible=False,showlegend=True,margin=dict(l=0, r=0, t=15, b=0),
        legend=dict(
            orientation="h",  # Đặt legend theo chiều ngang
            yanchor="bottom",  # Gắn legend vào đáy biểu đồ
            y=-0.6,  # Khoảng cách từ đáy biểu đồ
            xanchor="center",  # Gắn legend vào giữa
            x=0.5  # Đặt vị trí của legend ở giữa trục X
            ))
    st.plotly_chart(fig)

col1, col2, col3 = st.columns([2, 14, 4])
with col1:
    st.write("Thời gian:")
    timeframe = st.radio('', ['1Y', '3Y', 'All', 'Custom'], index=0)
    custom_start = None
    custom_end = None

    start_date = pd.to_datetime(start_date)
    start_date = start_date.to_pydatetime()
    if timeframe == 'Custom':
        custom_start = st.date_input("Thời gian bắt đầu",start_date)
        custom_end = st.date_input("Thời gian kết thúc", datetime.now())
    st.write("Chỉ báo:")
    show_sma = st.checkbox('SMA 20', value=False)
    show_sma50 = st.checkbox('SMA 50', value=False)
    show_macd = st.checkbox('MACD', value=False)
    show_bollinger = st.checkbox('Bollinger Bands', value=False)

with col2:
    if timeframe == 'Custom':
        load_data(timeframe,now, custom_start.strftime('%Y-%m-%d'), custom_end.strftime('%Y-%m-%d'), show_sma, show_sma50,show_bollinger)
        if show_macd:
            macd(timeframe,now, custom_start.strftime('%Y-%m-%d'), custom_end.strftime('%Y-%m-%d'))
    else:
        load_data(timeframe,now, custom_start, custom_end, show_sma, show_sma50,show_bollinger)
        if show_macd:
            macd(timeframe,now, custom_start, custom_end)

with col3:
    # Lấy lại dữ liệu cổ phiếu
    stock = Vnstock().stock(symbol=selected_stock, source='TCBS')
    now = datetime.now().strftime('%Y-%m-%d')
    data = stock.quote.history(start='2024-01-01', end=now, interval='1D')
    data['time'] = pd.to_datetime(data['time'])
    data.set_index('time', inplace=True)
    data['week'] = data.index.isocalendar().week
    weekly_avg = data.resample('W-Mon')['close'].mean()

    fig = make_subplots(
        rows=2, cols=1,
        specs=[[{'type': 'indicator'}], [{'type': 'xy'}]],  # Hàng 1 là indicator, hàng 2 là xy
        subplot_titles=[' ', 'Biểu đồ giá trung bình hàng tuần'],
        row_heights=[0.42, 0.8],  # Điều chỉnh tỷ lệ chiều cao giữa các hàng
        vertical_spacing=0.1
    )

    # Biểu đồ 1: Gauge (hàng 1)
    min_price = data['close'].min()
    max_price = data['close'].max()
    current_price = data['close'].iloc[-1]

    fig.add_trace(go.Indicator(
    mode="gauge+number+delta",value=current_price,
    title={'text': f'Giá CP {selected_stock} năm 2024'},
    gauge={
        'axis': {'range': [min_price, max_price]},
        'bar': {'color': "blue"},
        'steps': [{'range': [min_price, max_price], 'color': "lightgray"}],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': current_price
        }
    },
    delta={'reference': min_price, 'relative': True}
    ), row=1, col=1)

    # Biểu đồ 2: Line (hàng 2)
    fig.add_trace(go.Scatter(
        x=weekly_avg.index, y=weekly_avg.values, mode='lines',
        line=dict(color='blue', width=2), name='Giá Trung Bình Hàng Tuần'
    ), row=2, col=1)

    # Cập nhật layout
    fig.update_layout(
        title='',
        height=450,  # Tăng chiều cao để hiển thị cả hai biểu đồ rõ ràng
        showlegend=False,
        margin=dict(l=10, r=0, t=40, b=20)
    )

    # Hiển thị biểu đồ trong Streamlit
    st.plotly_chart(fig)

    st.write('Cổ phiếu cùng ngành tăng trưởng tốt nhất tuần qua')
    # danh sách các cổ phiếu trong cùng ngành
    df_industries = stock.listing.symbols_by_industries()
    icb_group = df_industries.loc[df_industries['symbol'] == selected_stock, 'icb_name3'].values[0]
    same_industry_stocks = df_industries[df_industries['icb_name3'] == icb_group]['symbol']

    # Tính toán % tăng trưởng của các cổ phiếu cùng ngành
    result = []
    for symbol in same_industry_stocks:
        df_price = stock.quote.history(symbol=symbol, start='2024-11-01', end='2024-11-18', interval='1D')
        if len(df_price) >= 2:  # Đảm bảo có ít nhất 2 phiên giao dịch
            last_close = df_price['close'].iloc[-1]
            prev_close = df_price['close'].iloc[-2]
            growth = ((last_close - prev_close) / prev_close) * 100  
            result.append({'CP': symbol, 'Giá': last_close, '%': growth})
        else:
            result.append({'CP': symbol, 'Giá': None, '%': None})  

    df_result = pd.DataFrame(result)
    df_sorted = df_result[df_result['CP'] != selected_stock].sort_values(by='%', ascending=False).reset_index(drop=True)

    # Hiển thị bảng kết quả (cổ phiếu cùng ngành)
    styled_df = df_sorted.head(3).style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'gray'), ('color', 'white'), ('font-weight', 'bold')]},  # Tên cột
        {'selector': 'tbody td', 'props': [('text-align', 'center')]},  # Căn giữa dữ liệu trong bảng
    ])
    st.table(styled_df)

