import streamlit as st
from vnstock3 import Vnstock
from datetime import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from overview import selected_stock
import plotly.express as px

#st.set_page_config(layout="wide")

now =  datetime.now().strftime('%Y-%m-%d')
st.title('Phân Tích Cơ bản')

selected_stock = st.session_state['selected_stock']
stock = Vnstock().stock(symbol=selected_stock, source='TCBS')
# -----------------------------THÔNG TIN CHI TIẾT BCTC-----------------------------------
tabs = st.tabs(['Bảng cân đối kế toán','Kết quả kinh doanh lãi lỗ','Lưu chuyển tiền tệ'])

#------------------------------BẢNG CÂN ĐỐI KẾ TOÁN--------------------------------------
with tabs[0]:
#--------------------------------Cho cổ phiếu non bank-----------------------------------
    selected_industry =  st.session_state['selected_industry']
    if selected_industry == 'Nhóm Ngành Khác':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.balance_sheet(period='year')
        with tabs[0]:
            st.subheader('Bảng cân đối kế toán')
            # Tính toán các chỉ số cần thiết
            df['TSCĐ/TS'] = df['fixed_asset'] / df['asset'] * 100  
            df['D/E'] = df['debt'] / df['equity']

            df['Nợ dài hạn trên TS dài hạn'] = df['long_debt'] / df['long_asset']
            df['Nợ ngắn hạn trên TS ngắn hạn'] = df['short_debt'] / df['short_asset']

            df['total_debt'] = df['other_debt'] + df['long_debt'] + df['short_debt'] + df['payable']
            #df['total_asset'] = df['asset'] + df['long_asset'] + df['short_asset']

            df['Nợ khác'] = df['other_debt']/df['total_debt'] * 100
            df['Nợ dài hạn'] = df['long_debt']/df['total_debt'] * 100
            df['Nợ ngắn hạn'] = df['short_debt']/df['total_debt'] * 100
            df['Khoản phải trả'] = df['payable']/df['total_debt'] * 100

            df['total_share']=df['un_distributed_income'] + df['minor_share_holder_profit']
            df['rate_un_distributed'] = df['un_distributed_income']/df['total_share'] * 100
            df = df.rename(columns = {
                'short_invest': 'Đầu tư ngắn hạn',
                'short_receivable': 'Phải thu ngắn hạn',
                'un_distributed_income': 'Thu nhập chưa phân phối',
                'minor_share_holder_profit':'Lợi nhuận của cổ đông thiểu số',
                'fixed_asset':'TSCĐ',
                'inventory':'Hàng tồn kho',
                'cash':'Tiền mặt'
            })
            # Cấu hình bố cục trang
            col1, col2, col3 = st.columns(3)  # Tạo cột có kích thước bằng nhau

            # Biểu đồ cột trồng (stacked bar) và biểu đồ đường cho tỷ lệ tăng trưởng tài sản cố định
            with col1:
                fig1 = go.Figure()

                for col, color in zip(['Tiền mặt', 'Hàng tồn kho', 'TSCĐ'], ['blue', 'green', 'orange']):
                    fig1.add_trace(go.Bar(x=df.index, y=df[col], name= col, marker_color=color))

                fig1.add_trace(go.Scatter(x=df.index, y=df['TSCĐ/TS'], name='TSCĐ/TS',
                                        mode='lines+markers', marker=dict(color='red', size=10), yaxis='y2'))

                fig1.update_layout(title="Tăng trưởng Tài Sản", xaxis_title="Năm", yaxis_title="Giá trị tài sản (Tỷ đồng)",
                                yaxis2=dict(title="Tăng trưởng (%)", overlaying='y', side='right', showgrid=False),
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig1, use_container_width=True)
            
            # Biểu đồ đường (line chart) cho hệ số đòn bẩy
            with col2:
                fig2 = go.Figure()

                for col, color in zip(['D/E', 'Nợ dài hạn trên TS dài hạn', 'Nợ ngắn hạn trên TS ngắn hạn'],
                                    ['blue', 'green', 'orange']):
                    fig2.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

                fig2.update_layout(title="Hệ số Đòn Bẩy", xaxis_title="Năm", yaxis_title="Hệ số Đòn Bẩy",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig2, use_container_width=True)
            
            # Biểu đồ cột trồng (100%) cho các khoản nợ & phải trả
            with col3:
                fig3 = go.Figure()

                for col, color in zip(['Khoản phải trả','Nợ ngắn hạn','Nợ dài hạn','Nợ khác'],
                                    ['blue', 'green', 'orange', 'red']):
                    fig3.add_trace(go.Bar(x=df.index, y=df[col], name= col.replace('_',' ').capitalize(), marker_color = color))

                fig3.update_layout(title="Tỷ lệ nợ & phải trả", xaxis_title="Period", yaxis_title="Tỷ lệ (%)",
                                
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig3, use_container_width=True)
            col1, col2, spacer, col3, col4 = st.columns([1,3,0.5,3,1])
            with col2:
                fig4 = go.Figure()

                for col, color in zip(['Đầu tư ngắn hạn', 'Phải thu ngắn hạn'],
                                    ['blue', 'green']):
                    fig4.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

                fig4.update_layout(title="Đầu tư và phải thu ngắn hạn qua các năm", xaxis_title="Period", yaxis_title="VND",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig4, use_container_width=True)


            with col3:
                fig5 = go.Figure()

                fig5.add_trace(go.Bar(x=df.index, y=df['Thu nhập chưa phân phối'],name='Thu nhập chưa phân phối', marker_color='blue'))
                fig5.add_trace(go.Bar(x=df.index, y=df['Lợi nhuận của cổ đông thiểu số'], name ='Lợi nhuận của cổ đông thiểu số', marker_color='green'))

                fig5.update_layout(title="TN chưa phân phối và LN của cổ đông thiểu số qua các năm",
                                xaxis_title="Period", yaxis_title="VND",
                                barmode='group',  # Biểu đồ cột ghép
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
                st.plotly_chart(fig5, use_container_width=True)
    #--------------------------------Cho cổ phiếu bank---------------------------------------------------------------
    elif selected_industry == 'Nhóm Ngân Hàng':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.balance_sheet(period='year')
        # Cấu hình bố cục trang
        col1, col2, col3 = st.columns(3)

        with col1:

            fig11 = go.Figure()
            df_filtered = df[df.index == '2023']
            df_filtered = df_filtered[['cash', 'fixed_asset', 'central_bank_deposit', 'other_bank_deposit', 'other_bank_loan', 'stock_invest', 'customer_loan']]
            df_filtered = df_filtered.rename(columns={
            'cash': 'Tiền mặt',
            'fixed_asset': 'Tài sản cố định',
            'central_bank_deposit': 'Tiền gửi tại Ngân hàng Trung ương',
            'other_bank_deposit': 'Tiền gửi tại ngân hàng khác',
            'other_bank_loan': 'Cho vay ngân hàng khác',
            'stock_invest': 'Đầu tư chứng khoán',
            'customer_loan': 'Cho vay khách hàng'
            })
            first_row_values = df_filtered.iloc[0].to_dict()
            df_melted = pd.DataFrame(list(first_row_values.items()), columns=['Category', 'Value'])
            df_melted['Category'] = df_melted['Category'].str.replace('_', ' ')

            fig11 = px.treemap(df_melted, path=['Category'], values='Value', 
                            title='Biểu đồ Phân Bổ Các Hạng Mục Tài Sản (đv: Tỷ đồng) ')
            #Tùy chỉnh font cho các nhãn và tiêu đề
            fig11.update_traces(
                textinfo='label+value',  # Hiển thị nhãn và giá trị trong ô, không có chú thích bên trên
                textfont=dict(size=10, color='black', family='Arial')
            )
            fig11.update_layout(
                title_font_family='Arial',
                title_font_color='black',

            )
            fig11.update_layout(height=250, margin=dict(r=5, l=5, t=25, b=5))

            # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig11, use_container_width=True)
        with col2:
            fig12 = go.Figure()
            df['Tăng trưởng TSCĐ %'] = df['fixed_asset'] / df['asset'] * 100
            for col, color, label in zip(['fixed_asset', 'customer_loan', 'net_customer_loan'], ['green', 'orange','yellow'],
                                         ['Tài sản cố định', 'Cho vay khách hàng', 'Dư nợ cho vay ròng']):
                fig12.add_trace(go.Bar(x=df.index, y=df[col], name= label, marker_color=color))
            
            fig12.add_trace(go.Scatter(x=df.index, y=df['Tăng trưởng TSCĐ %'], name='Tăng trưởng TSCĐ (%)',
                                        mode='lines+markers', marker=dict(color='red', size=10), yaxis='y2'))

            fig12.update_layout(title="Phân Tích Tăng Trưởng Tài Sản", xaxis_title="Năm", yaxis_title="Giá trị tài sản",
                                yaxis2=dict(title="Tăng trưởng (%)", overlaying='y', side='right', showgrid=False),
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
            st.plotly_chart(fig12, use_container_width=True)
        with col3:
            fig13 = go.Figure()
            df.rename(columns={'bad_loan':'Nợ xấu của KH','provision':'Dự phòng cho nợ xấu'}, inplace = True)
            for col, color in zip(['Nợ xấu của KH', 'Dự phòng cho nợ xấu'],
                                    ['blue', 'green']):
                    fig13.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

            fig13.update_layout(title="Trendlines nợ xấu và dự phòng nợ xấu của NH", xaxis_title="Năm", yaxis_title="Giá trị (Tỷ đồng)",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig13, use_container_width=True)
            fig = go.Figure()
        st.empty()
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            fig22 = go.Figure()
            df_filtered = df[df.index == '2023']

            # Tính tổng dư nợ và tỷ trọng các thành phần
            df_filtered['total_loan'] = (
                df_filtered['owe_other_bank'] + 
                df_filtered['owe_central_bank'] + 
                df_filtered['valuable_paper'] + 
                df_filtered['payable_interest'] + 
                df_filtered['receivable_interest'] + 
                df_filtered['other_debt'] + 
                df_filtered['deposit']
            )

            # Tính tỷ trọng các thành phần
            df_filtered['rate_owe_other_bank'] = df_filtered['owe_other_bank'] / df_filtered['total_loan'] 
            df_filtered['rate_owe_central_bank'] = df_filtered['owe_central_bank'] / df_filtered['total_loan'] 
            df_filtered['rate_valuable_paper'] = df_filtered['valuable_paper'] / df_filtered['total_loan'] 
            df_filtered['rate_payable_interest'] = df_filtered['payable_interest'] / df_filtered['total_loan'] 
            df_filtered['rate_receivable_interest'] = df_filtered['receivable_interest'] / df_filtered['total_loan'] 
            df_filtered['rate_other_debt'] = df_filtered['other_debt'] / df_filtered['total_loan'] 
            df_filtered['rate_deposit'] = df_filtered['deposit'] / df_filtered['total_loan'] 

            # Tạo dữ liệu cho biểu đồ tròn
            pie_data = {
                'Danh mục': [
                    'Nợ NH Khác', 
                    'Nợ NH TW', 
                    'Giấy Tờ Có Giá', 
                    'Lãi Phải Trả', 
                    'Lãi Phải Thu', 
                    'Khoản Nợ Khác', 
                    'Tiền Gửi'
                ],
                'Tỷ trọng': [
                    df_filtered['rate_owe_other_bank'].iloc[0],
                    df_filtered['rate_owe_central_bank'].iloc[0],
                    df_filtered['rate_valuable_paper'].iloc[0],
                    df_filtered['rate_payable_interest'].iloc[0],
                    df_filtered['rate_receivable_interest'].iloc[0],
                    df_filtered['rate_other_debt'].iloc[0],
                    df_filtered['rate_deposit'].iloc[0]
                ]
            }

            df_pie = pd.DataFrame(pie_data)

            # Vẽ biểu đồ tròn với nhãn và tiêu đề tiếng Việt
            fig22 = px.pie(
                df_pie, 
                names='Danh mục', 
                values='Tỷ trọng', 
                title='Tỷ Trọng Dư Nợ Tài Chính'
            )
            fig22.update_layout(
                autosize=True,
                height=450,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.5, xanchor="center", x=0.5)
            )

            # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig22, use_container_width=True)

        with col2:
            fig22 =  go.Figure()
        #nợ trên vốn chủ sở hữu= Tổng nợ/Vốn chủ sở hữu
        #Tỷ lệ nợ trên tổng tài sản = Tổng nợ/Tổng tài sản
        #Lần lãi bao phủ lãi vay = LNTT và Lãi vay/lãi vay
            df['Hệ số đòn bẩy VCSH'] = df['debt']/df['equity']
            df['Hệ số đòn bẩy TS'] = df['debt']/df['asset']
            
            for col, color in zip(['Hệ số đòn bẩy VCSH', 'Hệ số đòn bẩy TS'],
                                    ['blue', 'green']):
                    fig22.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

            fig22.update_layout(title="Hệ số Đòn Bẩy", xaxis_title="Năm", yaxis_title="Hệ số Đòn Bẩy (%)",
                                autosize=True, height=500, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig22, use_container_width=True)

        with col3:
            fig33 = go.Figure()

            fig33.add_trace(go.Bar(x=df.index, y=df['capital'],name='Vốn điều lệ', marker_color='blue'))
            fig33.add_trace(go.Bar(x=df.index, y=df['equity'],name='Vốn chủ sở hữu', marker_color='green'))

            fig33.update_layout( title="Capital và Equity qua các năm", xaxis_title="Năm", yaxis_title="Giá trị (Tỷ đồng)", barmode='group',
            autosize=True,height=400, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig33, use_container_width=True)

        with col4:
            df['growth_un_distributed_income'] = df['un_distributed_income'].pct_change() * 100
            df['growth_minor_share_holder_profit'] = df['minor_share_holder_profit'].pct_change() * 100

            # Tạo một figure cho biểu đồ đường
            fig32 = go.Figure()

            # Thêm các đường cho tỷ lệ tăng trưởng của 'un_distributed_income' và 'minor_share_holder_profit'
            fig32.add_trace(go.Scatter(x=df.index, y=df['growth_un_distributed_income'], mode='lines+markers',
                                    name='Tỷ lệ tăng trưởng LNST chưa phân phối', marker=dict(color='blue')))
            fig32.add_trace(go.Scatter(x=df.index, y=df['growth_minor_share_holder_profit'], mode='lines+markers',
                                    name='Tỷ lệ tăng trưởng Lợi nhuận của cổ đông thiểu số', marker=dict(color='green')))

            # Cập nhật bố cục biểu đồ
            fig32.update_layout(
                title="Tăng trưởng LNST chưa phân phối và LN cổ đông thiểu số",
                xaxis_title="Năm",
                yaxis_title="Tỷ lệ tăng trưởng (%)",
                autosize=True,
                height=400,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.45, xanchor="center", x=0.5)
            )

            # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig32, use_container_width=True)
            

    df = stock.finance.income_statement(period='year')
    #df['Biên lợi nhuận'] = (df['LN trước thuế'] - df['Thuế TNDN'])/ df['Doanh thu (Tỷ đồng)']
    #df = df[['Biên lợi nhuận','Doanh thu (Tỷ đồng)','Lãi/Lỗ từ hoạt động kinh doanh','Lợi nhuận thuần']]
    #df = df.loc[:,~df.columns.duplicated()]
#------------------------------ KẾT QUẢ KINH DOANH------------------------------
with tabs[1]:
#------------------------------ Nhóm ngành khác------------------------------
    selected_industry =  st.session_state['selected_industry']
    if selected_industry == 'Nhóm Ngành Khác':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.income_statement(period='year')
        df['cost_of_good_sold'] = df['cost_of_good_sold']*-1
        col1, col2 = st.columns(2)
        with col1:
            fig = go.Figure()

            # Cột ghép: revenue
            fig.add_trace(go.Bar(x=df.index, y=df['revenue'], name='Doanh thu',marker_color='blue', offsetgroup=0))
            # Cột trồng: cost_of_good_sold và gross_profit
            fig.add_trace(go.Bar(x=df.index,y=df['cost_of_good_sold'], name='COGS', marker_color='orange',offsetgroup=1))
            fig.add_trace(go.Bar(x=df.index,y=df['gross_profit'], name='Lợi nhuận', marker_color='green', base=df['cost_of_good_sold'],offsetgroup=1 ))

            # Đường biểu diễn tăng trưởng: year_revenue_growth
            fig.add_trace(go.Scatter( x=df.index,y=df['year_revenue_growth'], mode='lines+markers', name='Tăng trưởng DT(%)',
                                        marker=dict(color='red', size=8),yaxis='y2' ))
            # Cập nhật layout cho biểu đồ
            fig.update_layout(
                title="Biểu đồ thể hiện doanh thu, chi phí và lợi nhuận",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                yaxis2=dict(title="Tăng trưởng (%)",overlaying='y',side='right',showgrid=False
                ),barmode='group', autosize=True,
                height=320,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            fig12 = go.Figure()
            df['Lợi nhuận']=df['year_operation_profit_growth']*100
            df['Doanh thu']=df['year_revenue_growth']*100
            df['Lợi nhuận cổ đông'] = df['year_share_holder_income_growth']*100

            for col, color in zip(['Lợi nhuận','Doanh thu','Lợi nhuận cổ đông'],
                                ['blue','green','red']):
                fig12.add_trace(go.Scatter(x=df.index, y=df[col],name=col.replace('_', ' ').capitalize(),
                                                    mode='lines+markers', marker=dict(color=color, size=10)))
            fig12.update_layout(title="Tỷ lệ tăng trưởng Lợi nhuận và Doanh thu qua các năm", xaxis_title="Năm", yaxis_title="Tỷ lệ (%)",
                                        autosize=True, height=320, margin=dict(l=0, r=0, t=40, b=0),
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig12, use_container_width=True)
        
        col1, col2 = st.columns(2)
        with col1:
            fig4 = go.Figure()

            fig4.add_trace(go.Bar(x=df.index, y=df['cost_of_good_sold'], name='COGS', marker_color='blue'))
            fig4.add_trace(go.Bar(x=df.index, y=df['operation_expense'], name='Chi phí hoạt động', marker_color='green'))
            fig4.add_trace(go.Bar(x=df.index, y=df['interest_expense'], name='Chi phí tài chính', marker_color='red'))

            fig4.update_layout(title="Chi phí qua các năm",
                            xaxis_title="Năm", yaxis_title="Giá trị (Tỷ VND)",
                            barmode='group',  # Biểu đồ cột ghép
                            autosize=True, height=320, margin=dict(l=0, r=0, t=40, b=0),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
            st.plotly_chart(fig4, use_container_width=True)
        with col2:
            fig = go.Figure()

            # Stacked bar for ebitda and share_holder_income
            fig.add_trace(go.Bar(x=df.index, y=df['ebitda'],name='EBITDA',marker_color='royalblue',offsetgroup= 0))
            fig.add_trace(go.Bar(x=df.index,y=df['share_holder_income'],name='Lợi nhuận cổ đồng', marker_color='gold',  offsetgroup=1 ))
            fig.add_trace(go.Scatter( x=df.index, y=df['year_share_holder_income_growth'],
                mode='lines+markers', name='Tỷ lệ tăng trưởng LN cổ đông(%)', marker=dict(color='darkgreen', size=8),yaxis='y2'
            ))

            # Customize layout
            fig.update_layout(
                title="Biểu đồ cột ghép thể hiện Ebitda, LN cổ đông và Tỷ lệ tăng trưởng LN cổ đông", 
                yaxis_title="Giá trị (Tỷ VND)", yaxis2=dict(title="Tỷ lệ tăng trưởng (%)", overlaying='y', side='right',showgrid=False
                ),barmode='group',  autosize=True,height=320,margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.55, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = go.Figure()

            # Cột ghép: revenue
            fig.add_trace(go.Bar(x=df.index, y=df['revenue'], name='Thu nhập lãi thuần',marker_color='blue', offsetgroup=0))
            fig.add_trace(go.Bar(x=df.index,y=df['operation_profit'], name='Tổng thu nhập hoạt động', marker_color='green',offsetgroup=1 ))
            fig.add_trace(go.Bar(x=df.index,y=df['post_tax_profit'], name='Lợi nhuận sau thuế', marker_color='orange',offsetgroup=2 ))

            fig.update_layout(
                title="Biểu đồ thể hiện TN lãi thuần, TN hoạt động và LNST",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.65   , xanchor="center", x=0.5)
            )

            # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig12 = go.Figure()
            df['Thu nhập lãi thuần']=df['year_revenue_growth']*100
            df['Thu nhập hoạt động']=df['year_operation_profit_growth']*100 
            df['Lợi nhuận cổ đông'] = df['year_share_holder_income_growth']*100

            for col, color in zip(['Thu nhập lãi thuần','Thu nhập hoạt động','Lợi nhuận cổ đông'],
                                ['blue','green','red']):
                fig12.add_trace(go.Scatter(x=df.index, y=df[col],name=col.replace('_', ' ').capitalize(),
                                                    mode='lines+markers', marker=dict(color=color, size=5)))
            fig12.update_layout(title="Tỷ lệ tăng trưởng Lợi nhuận và Thu nhập", xaxis_title="Năm", yaxis_title="Tỷ lệ (%)",
                                        autosize=True, height=400, margin=dict(l=0, r=0, t=40, b=0),
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig12, use_container_width=True)

        with col3:
            df['operation_expense'] =df['operation_expense']*-1
            fig13 = go.Figure()

            # Cột ghép: revenue
            fig13.add_trace(go.Bar(x=df.index, y=df['operation_profit'], name='Tổng thu nhập',marker_color='blue', offsetgroup=0))
            # Cột trồng: cost_of_good_sold và gross_profit
            fig13.add_trace(go.Bar(x=df.index,y=df['operation_expense'], name='Chi phí hoạt động', marker_color='orange',offsetgroup=1))
            fig13.add_trace(go.Bar(x=df.index,y=df['operation_income'], name='Tổng lợi nhuận hoạt động', marker_color='green', base=df['operation_expense'],offsetgroup=1 ))
            fig13.update_layout(
                title="Biểu đồ thể hiện xu hướng dòng tiền qua các năm",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig13, use_container_width=True)
        col1, col2 = st.columns(2)
        with col1:
            fig21 = go.Figure()
            fig21.add_trace(go.Bar(x=df.index, y=df['share_holder_income'], name='LNST của cổ đông',marker_color='blue', offsetgroup=0))
            # Đường biểu diễn tăng trưởng: year_revenue_growth
            fig21.add_trace(go.Scatter( x=df.index,y=df['year_share_holder_income_growth'], mode='lines+markers', name='Tăng trưởng DT (%)',
                                        marker=dict(color='red', size=8),yaxis='y2' ))
            # Cập nhật layout cho biểu đồ
            fig21.update_layout(
                title="Biểu đồ thể hiện LNST của cổ đông",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                yaxis2=dict(title="Tăng trưởng (%)",overlaying='y',side='right',showgrid=False
                ),barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig21, use_container_width=True)
        with col2:
            fig22 = go.Figure()
            fig22.add_trace(go.Bar(x=df.index, y=df['invest_profit'], name='Đầu tư',marker_color='blue', offsetgroup=0))
            fig22.add_trace(go.Bar(x=df.index, y=df['service_profit'], name='Dịch vụ',marker_color='green', offsetgroup=1))
            fig22.add_trace(go.Bar(x=df.index, y=df['other_profit'], name='Thu nhập khác',marker_color='orange', offsetgroup=2))

            fig22.update_layout(
                title="Thu nhập khác từ hoạt động đầu tư và dịch vụ",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig22, use_container_width=True)
#------------------------------LƯU CHUYỂN TIỀN TỆ------------------------------
selected_stock = st.session_state['selected_stock']
stock = Vnstock().stock(symbol=selected_stock, source='VCI')
# Hàm chuyển đổi giá trị tiền tệ
def format_large_number(value):
    trillion = 10**12
    billion = 10**9
    million = 10**6

    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= trillion:
        return f"{sign}{value / trillion:.2f} NT"
    elif value >= billion:
        return f"{sign}{value / billion:.2f} T"
    elif value >= million:
        return f"{sign}{value / million:.2f} Tr"
    else:
        return f"{sign}{value:,}"
with tabs[2]:
    selected_industry =  st.session_state['selected_industry']
    if selected_industry == 'Nhóm Ngân Hàng':
        df = Vnstock().stock(symbol=selected_stock, source='VCI').finance.cash_flow(period='year', lang='vi')
        col1, col2, col3 = st.columns(3)
        latest_data = df.iloc[0]  
        # Thêm CSS tùy chỉnh cho các thẻ (cards)
        with col1:
            
            st.markdown(
                """
                <style>
                .card {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    width: 85%; /* Điều chỉnh width để thẻ ngắn hơn */
                    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                .card-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                }
                .card-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #007BFF;
                }
                </style>
                """,
                unsafe_allow_html=True
                )
        # Thêm các card vào cột col1 với CSS đã tạo
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">Tiền và tương đương tiền</div>
                    <div class="card-value">{format_large_number(latest_data['Tiền và tương đương tiền'])} VND</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">Tiền thu cổ tức và lợi nhuận được chia</div>
                    <div class="card-value">{format_large_number(latest_data['Tiền thu cổ tức và lợi nhuận được chia'])} VND</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                f"""<div class="card">
                    <div class="card-title">Cổ tức đã trả</div>
                    <div class="card-value">{format_large_number(latest_data['Cổ tức đã trả'])} VND</div>
                </div>
                """, unsafe_allow_html=True)
        with col2:
            fig13 = go.Figure()
            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Lưu chuyển tiền từ hoạt động tài chính'], 
                name='Lưu chuyển tiền từ hoạt động tài chính', marker_color='blue',offsetgroup=0
            ))

            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Lưu chuyển từ hoạt động đầu tư'],name='Lưu chuyển từ hoạt động đầu tư',
                                   marker_color='orange',offsetgroup=1
            ))

            fig13.add_trace(go.Bar(
                x=df['Năm'],y=df['Lưu chuyển tiền tệ ròng từ các hoạt động SXKD'], 
                name='Lưu chuyển tiền tệ ròng từ các hoạt động SXKD',marker_color='green',offsetgroup=2
            ))

            fig13.update_layout(
                title="Biểu đồ thể hiện xu hướng dòng tiền qua các năm",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=490,margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h",yanchor="bottom",y=-0.35,xanchor="center",x=0.5))

            st.plotly_chart(fig13, use_container_width=True)       
        with col3:
            line_fig = px.line(
                x=df['Năm'],
                y=df['Lưu chuyển tiền thuần trong kỳ'],
                labels={'x': 'Năm', 'y': 'Lưu chuyển tiền thuần trong kỳ'},
                title='Lưu chuyển tiền thuần trong kỳ qua các năm'
            )

            line_fig.update_layout(xaxis_title='Năm', yaxis_title='Lưu chuyển tiền thuần')

            # Hiển thị biểu đồ trong cột col3
            st.plotly_chart(line_fig)   
        
        col1, col2,spacer2, col3, col4 = st.columns([1,5,0.3,4,1])
        with col2:
            categories = [
                'Thu cổ tức & LN được chia',
                'Thu từ thanh lý TSCĐ',
                'Thu từ bán khoản đầu tư',
                'Lưu chuyển từ HĐ đầu tư',
                'Đầu tư vào DN khác',
                'Mua sắm TSCĐ',
            ]

            # Danh sách các cột trong DataFrame cần kiểm tra
            required_columns = [
                'Tiền thu cổ tức và lợi nhuận được chia',
                'Tiền thu được từ thanh lý tài sản cố định',
                'Tiền thu từ việc bán các khoản đầu tư vào doanh nghiệp khác',
                'Lưu chuyển từ hoạt động đầu tư',
                'Đầu tư vào các doanh nghiệp khác',  # Cột này có thể không có
                'Mua sắm TSCĐ'
            ]

            # Kiểm tra và lấy giá trị cho các cột, nếu không có thì mặc định là 0
            values = []
            for column in required_columns:
                value = latest_data.get(column, 0)  # Nếu cột không có trong df, trả về 0
                values.append(value)

            # Tính tổng dòng tiền và thêm vào danh sách categories và values
            total = sum(values)
            categories.append("Dòng tiền cuối kỳ")
            values.append(total)

            # Vẽ biểu đồ thác
            fig = go.Figure(go.Waterfall(
                name="Dòng tiền",
                orientation="v",
                measure=["relative"] * (len(values) - 1) + ["total"],  # Các bước + tổng cuối
                x=categories,
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},  # Màu connector
            ))

            # Cập nhật layout
            fig.update_layout(
                title="Biểu đồ thác dòng tiền hoạt động đầu tư kỳ trước",
                yaxis_title="Giá trị (Tỷ VND)",
                xaxis_title="Các thành phần dòng tiền",
                waterfallgap=0.3,
                autosize=True,
                height=400,
                margin=dict(l=40, r=40, t=40, b=40),
                showlegend=False
            )

            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
        with col3:
            fig13 = go.Figure()
            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Lưu chuyển tiền từ hoạt động tài chính'], 
                name='Lưu chuyển tiền từ hoạt động tài chính', marker_color='blue',offsetgroup=0
            ))

            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Cổ tức đã trả'],name='Cổ tức đã trả',
                                   marker_color='orange',offsetgroup=1
            ))

            fig13.add_trace(go.Bar(
                x=df['Năm'],y=df['Tăng vốn cổ phần từ góp vốn và/hoặc phát hành cổ phiếu'], 
                name='Tăng vốn cổ phần từ góp vốn và/hoặc phát hành cổ phiếu',marker_color='green',offsetgroup=2
            ))

            # Tùy chỉnh layout
            fig13.update_layout(
                title="Biểu đồ thể hiện xu hướng dòng tiền hoạt động tài chính qua các năm",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h",yanchor="bottom",y=-0.55,xanchor="center",x=0.5))

            # Hiển thị biểu đồ trên Streamlit
            st.plotly_chart(fig13, use_container_width=True)
    else:
        df = Vnstock().stock(symbol=selected_stock, source='VCI').finance.cash_flow(period='year', lang='vi')
        latest_data = df.iloc[0]  
        col1, col2, col3 = st.columns(3)
        with col1:
            
            st.markdown(
                """
                <style>
                .card {
                    background-color: #f0f2f6;
                    border-radius: 10px;
                    padding: 20px;
                    width: 85%; /* Điều chỉnh width để thẻ ngắn hơn */
                    box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
                    margin-bottom: 20px;
                }
                .card-title {
                    font-size: 18px;
                    font-weight: bold;
                    color: #333;
                }
                .card-value {
                    font-size: 24px;
                    font-weight: bold;
                    color: #007BFF;
                }
                </style>
                """,
                unsafe_allow_html=True
                )
        # Thêm các card vào cột col1 với CSS đã tạo
            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">Tiền và tương đương tiền</div>
                    <div class="card-value">{format_large_number(latest_data['Tiền và tương đương tiền'])} VND</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                f"""
                <div class="card">
                    <div class="card-title">Tiền thu cổ tức và lợi nhuận được chia</div>
                    <div class="card-value">{format_large_number(latest_data['Tiền thu cổ tức và lợi nhuận được chia'])} VND</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown(
                f"""<div class="card">
                    <div class="card-title">Cổ tức đã trả</div>
                    <div class="card-value">{format_large_number(latest_data['Cổ tức đã trả'])} VND</div>
                </div>
                """, unsafe_allow_html=True)   
        with col2:
            fig13 = go.Figure()
            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Lưu chuyển tiền từ hoạt động tài chính'], 
                name='Lưu chuyển tiền từ hoạt động tài chính', marker_color='blue',offsetgroup=0
            ))

            fig13.add_trace(go.Bar(x=df['Năm'],y=df['Lưu chuyển từ hoạt động đầu tư'],name='Lưu chuyển từ hoạt động đầu tư',
                                   marker_color='orange',offsetgroup=1
            ))

            fig13.add_trace(go.Bar(
                x=df['Năm'],y=df['Lưu chuyển tiền tệ ròng từ các hoạt động SXKD'], 
                name='Lưu chuyển tiền tệ ròng từ các hoạt động SXKD',marker_color='green',offsetgroup=2
            ))

            fig13.update_layout(
                title="Biểu đồ thể hiện xu hướng dòng tiền qua các năm",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=490,margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h",yanchor="bottom",y=-0.35,xanchor="center",x=0.5))
            st.plotly_chart(fig13, use_container_width=True) 
        with col3:
            df['Màu'] = df['Lưu chuyển tiền tệ ròng từ các hoạt động SXKD'].apply(lambda x: 'Dòng tiền dương' if x >= 0 else 'Dòng tiền âm')

            # Tạo biểu đồ bar với màu sắc phụ thuộc vào giá trị
            fig = px.bar(
                df,x='Năm',y='Lưu chuyển tiền tệ ròng từ các hoạt động SXKD',
                color='Màu',color_discrete_map={'Dòng tiền dương': 'green', 'Dòng tiền âm': 'red'},  # Map màu
                labels={'Năm': 'Năm', 'Lưu chuyển tiền tệ ròng từ các hoạt động SXKD': 'Giá trị'},
                title='Lưu chuyển tiền tệ ròng từ các hoạt động SXKD trong kỳ qua các năm'
            )

            # Cập nhật tiêu đề trục
            fig.update_layout(
                title="Biểu đồ thể hiện xu hướng dòng tiền SXKD qua các năm",xaxis_title="Năm",yaxis_title="Giá trị (Tỷ VND)",
                barmode='group', autosize=True,
                height=490,margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h",yanchor="bottom",y=-0.35,xanchor="center",x=0.5,title_text=None))
            st.plotly_chart(fig, use_container_width=True) 

        col1,col2 = st.columns(2)
        with col1:
            categories = [
                'Thu từ thanh lý TSCĐ',
                'Thu hồi cho vay, bán lại các công cụ nợ',
                'Thu từ việc bán các khoản đầu tư',
                'Thu cổ tức và lợi nhuận được chia',
                'Đầu tư vào DN khác',
                'Mua sắm TSCĐ',
                'Tiền chi cho vay, mua công cụ nợ'
            ]

            # Danh sách các cột trong DataFrame cần kiểm tra
            required_columns = [
                'Tiền thu được từ thanh lý tài sản cố định',
                'Tiền thu hồi cho vay, bán lại các công cụ nợ của đơn vị khác (Tỷ đồng)',
                'Tiền thu từ việc bán các khoản đầu tư vào doanh nghiệp khác',
                'Tiền thu cổ tức và lợi nhuận được chia',
                'Đầu tư vào các doanh nghiệp khác',  # Cột này có thể không có
                'Mua sắm TSCĐ'
                'Tiền chi cho vay, mua công cụ nợ của đơn vị khác (Tỷ đồng)'
            ]

            # Kiểm tra và lấy giá trị cho các cột, nếu không có thì mặc định là 0
            values = []
            for column in required_columns:
                value = latest_data.get(column, 0)  # Nếu cột không có trong df, trả về 0
                values.append(value)

            # Tính tổng dòng tiền và thêm vào danh sách categories và values
            total = sum(values)
            categories.append("Dòng tiền cuối kỳ")
            values.append(total)

            # Vẽ biểu đồ thác
            fig = go.Figure(go.Waterfall(
                name="Dòng tiền",
                orientation="v",
                measure=["relative"] * (len(values) - 1) + ["total"],  # Các bước + tổng cuối
                x=categories,
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},  # Màu connector
            ))

            # Cập nhật layout
            fig.update_layout(
                title="Biểu đồ thác dòng tiền hoạt động tăng vốn kỳ trước",
                yaxis_title="Giá trị (Tỷ VND)",
                xaxis_title="Các thành phần dòng tiền",
                waterfallgap=0.3,
                autosize=True,
                height=450,
                margin=dict(l=40, r=40, t=40, b=40),
                showlegend=False
            )

            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            categories = [
                'Tăng vốn cổ phần từ góp vốn và phát hành CP',
                'Tiền thu được các khoản đi vay',
                'Chi trả cho việc mua lại, trả cổ phiếu',
                'Tiền trả các khoản đi vay',
                'Thanh toán vốn gốc đi thuê tài chính',  
                'Cổ tức đã trả'
            ]

            # Danh sách các cột trong DataFrame cần kiểm tra
            required_columns = [
                'Tăng vốn cổ phần từ góp vốn và/hoặc phát hành cổ phiếu',
                'Tiền thu được các khoản đi vay',
                'Chi trả cho việc mua lại, trả cổ phiếu',
                'Tiền trả các khoản đi vay',
                'Tiền thanh toán vốn gốc đi thuê tài chính',  # Cột này có thể không có
                'Cổ tức đã trả'
            ]

            # Kiểm tra và lấy giá trị cho các cột, nếu không có thì mặc định là 0
            values = []
            for column in required_columns:
                value = latest_data.get(column, 0)  # Nếu cột không có trong df, trả về 0
                values.append(value)

            # Tính tổng dòng tiền và thêm vào danh sách categories và values
            total = sum(values)
            categories.append("Dòng tiền cuối kỳ")
            values.append(total)

            # Vẽ biểu đồ thác
            fig = go.Figure(go.Waterfall(
                name="Dòng tiền",
                orientation="v",
                measure=["relative"] * (len(values) - 1) + ["total"],  # Các bước + tổng cuối
                x=categories,
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},  # Màu connector
            ))

            # Cập nhật layout
            fig.update_layout(
                title="Biểu đồ thác dòng tiền hoạt động đầu tư kỳ trước",
                yaxis_title="Giá trị (Tỷ VND)",
                xaxis_title="Các thành phần dòng tiền",
                waterfallgap=0.3,
                autosize=True,
                height=500,
                margin=dict(l=40, r=40, t=40, b=40),
                showlegend=False
            )

            # Hiển thị biểu đồ
            st.plotly_chart(fig, use_container_width=True)

