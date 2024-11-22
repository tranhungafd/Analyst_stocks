from vnstock3 import Vnstock
from datetime import datetime, timedelta
import streamlit as st
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import pandas as pd
st.set_page_config(layout="wide")

now = datetime.now().strftime('%Y-%m-%d')
st.title('Biểu đồ nến theo cổ phiếu')

# Lấy cổ phiếu đã chọn
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

# Hàm lấy và vẽ dữ liệu
def load_data(timeframe, show_sma, show_macd, show_signal):
    if timeframe == '1W':
        start_date = (datetime.now() - timedelta(weeks=1)).strftime('%Y-%m-%d')
    elif timeframe == '1M':
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    elif timeframe == '3M':
        start_date = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    elif timeframe == '6M':
        start_date = (datetime.now() - timedelta(days=180)).strftime('%Y-%m-%d')
    elif timeframe == '1Y':
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')
    elif timeframe == '3Y':
        start_date = (datetime.now() - timedelta(days=1095)).strftime('%Y-%m-%d')
    elif timeframe == 'All':
        start_date = date  # To load from 2010 onwards

    # Lấy dữ liệu lịch sử cổ phiếu
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

    # Vẽ đường SMA nếu được chọn
    if show_sma:
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data['SMA_20'],
            mode='lines',
            line=dict(color='blue', width=1.5),
            name='SMA 20'
        ))

    # Vẽ MACD nếu được chọn
    if show_macd:
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data['MACD'],
            mode='lines',
            line=dict(color='purple', width=1),
            name='MACD'
        ))

    # Vẽ Signal Line nếu được chọn
    if show_signal:
        fig.add_trace(go.Scatter(
            x=data['time'],
            y=data['Signal'],
            mode='lines',
            line=dict(color='orange', width=1, dash='dash'),
            name='Signal Line'
        ))

    # Đặt tiêu đề và nhãn
    fig.update_layout(title=f'Biểu đồ nến của cổ phiếu {selected_stock}',
                      xaxis_title='Ngày giao dịch',
                      yaxis_title='Giá',
                      xaxis_rangeslider_visible=False,
                      yaxis=dict(range=[0, max(data['high'])]),
                      height=750
    )

    # Cập nhật định dạng trục x
    fig.update_xaxes(
        type='date',
        tickformat='%Y-%m-%d',
        ticklabelmode="instant"
    )

    # Hiển thị biểu đồ
    st.plotly_chart(fig)

# Tạo 3 cột với tỷ lệ 1:15
col1, col2, col3 = st.columns([1, 11, 3])

# Cột bên trái: radio button cho thời gian và selectbox cho các chỉ báo
with col1:
    st.write("Thời gian:")
    timeframe = st.radio('', ['1W', '1M', '3M', '6M', '1Y', '3Y', 'All'], index=6)
    st.write("Chỉ báo:", divider="gray")
    show_sma = st.checkbox('SMA', value=False)
    show_macd = st.checkbox('MACD', value=False)
    show_signal = st.checkbox('Signal Line', value=False)

# Cột bên phải: Biểu đồ nến
with col2:
    load_data(timeframe, show_sma, show_macd, show_signal)

# Cột bên phải thêm: Biểu đồ giá trung bình hàng tuần
with col3:
        # Lấy danh sách các cổ phiếu trong cùng ngành
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
            growth = ((last_close - prev_close) / prev_close) * 100  # Tính % tăng trưởng
            result.append({'CP': symbol, 'Giá': last_close, '%': growth})
        else:
            result.append({'CP': symbol, 'Giá': None, '%': None})  # Dữ liệu không đủ

    df_result = pd.DataFrame(result)
    df_sorted = df_result[df_result['CP'] != selected_stock].sort_values(by='%', ascending=False).reset_index(drop=True)

    # Hiển thị bảng kết quả (cổ phiếu cùng ngành)
    styled_df = df_sorted.head(3).style.set_table_styles([
        {'selector': 'thead th', 'props': [('background-color', 'gray'), ('color', 'white'), ('font-weight', 'bold')]},  # Tên cột
        {'selector': 'tbody td', 'props': [('text-align', 'center')]},  # Căn giữa dữ liệu trong bảng
    ])

    # Hiển thị bảng trong Streamlit
    st.table(styled_df)

    # Hàm lấy và vẽ dữ liệu gauge
    def plot_combined_chart():
        # Tạo subplot với 2 hàng và 1 cột, giảm khoảng cách giữa các biểu đồ
        fig = make_subplots(
            rows=2, cols=1,
            specs=[[{'type': 'xy'}], [{'type': 'indicator'}]],  # Hàng 1 là xy, hàng 2 là indicator
            subplot_titles=['Biểu đồ giá trung bình hàng tuần', 'Biểu đồ Gauge'],
            vertical_spacing=0.2  # Giảm khoảng cách giữa các biểu đồ
        )

        # Biểu đồ 1: Giá trung bình hàng tuần
        start_date = '2024-01-01'
        end_date = datetime.now().strftime('%Y-%m-%d')
        # Lấy dữ liệu cổ phiếu
        data = stock.quote.history(start=start_date, end=end_date, interval='1D')
        data['time'] = pd.to_datetime(data['time'])
        data.set_index('time', inplace=True)
        data['week'] = data.index.isocalendar().week
        weekly_avg = data.resample('W-Mon')['close'].mean()

        # Thêm biểu đồ đường vào hàng 1
        fig.add_trace(go.Scatter(
            x=weekly_avg.index,
            y=weekly_avg.values,
            mode='lines',
            line=dict(color='blue', width=2),
            name='Giá trung bình hàng tuần'
        ), row=1, col=1)

        # Biểu đồ 2: Gauge
        min_price = data['close'].min()
        max_price = data['close'].max()
        current_price = data['close'].iloc[-1]

        # Thêm biểu đồ Gauge vào hàng 2
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=current_price,
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
        ), row=2, col=1)

        # Cập nhật layout
        fig.update_layout(
            height=600,  # Điều chỉnh chiều cao để làm cho các biểu đồ sát nhau hơn
            showlegend=False
        )
        st.plotly_chart(fig)
    plot_combined_chart()
