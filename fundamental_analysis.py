import streamlit as st
from vnstock3 import Vnstock
from datetime import datetime
import plotly.graph_objects as go
import pandas as pd
from overview import selected_stock
import plotly.express as px

#st.set_page_config(layout="wide")

now =  datetime.now().strftime('%Y-%m-%d')
st.title('Phân Tích Cơ bản')

#symbols_df = Vnstock().stock(symbol='ACB', source='TCBS').listing.all_symbols()
#symbols = symbols_df['ticker'].tolist()

selected_stock = st.session_state['selected_stock']
stock = Vnstock().stock(symbol=selected_stock, source='TCBS')
# -----------------------------THÔNG TIN CHI TIẾT BCTC-----------------------------------
tabs = st.tabs(['Bảng cân đối kế toán','Kết quả kinh doanh lãi lỗ','Lưu chuyển tiền tệ'])

#------------------------------Bảng cân đối kế toán--------------------------------------
with tabs[0]:
#--------------------------------Cho cổ phiếu non bank-----------------------------------
    selected_industry =  st.session_state['selected_industry']
    if selected_industry == 'Nhóm Ngành Khác':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.balance_sheet(period='year')
        with tabs[0]:
            st.subheader('Bảng cân đối kế toán')
            st.write("Bảng CĐKT")
            # Tính toán các chỉ số cần thiết
            df['fixed_asset_growth'] = df['fixed_asset'] / df['asset'] * 100  
            df['debt_to_equity'] = df['debt'] / df['equity']
            df['long_debt_to_long_asset'] = df['long_debt'] / df['long_asset']
            df['short_debt_to_short_asset'] = df['short_debt'] / df['short_asset']

            df['total_debt'] = df['other_debt'] + df['long_debt'] + df['short_debt'] + df['payable']
            #df['total_asset'] = df['asset'] + df['long_asset'] + df['short_asset']

            df['rate_other_debt'] = df['other_debt']/df['total_debt'] * 100
            df['rate_long_debt'] = df['long_debt']/df['total_debt'] * 100
            df['rate_short_debt'] = df['short_debt']/df['total_debt'] * 100
            df['rate_payable'] = df['payable']/df['total_debt'] * 100

            df['total_share']=df['un_distributed_income'] + df['minor_share_holder_profit']
            df['rate_un_distributed'] = df['un_distributed_income']/df['total_share'] * 100

            # Cấu hình bố cục trang
            col1, col2, col3 = st.columns(3)  # Tạo cột có kích thước bằng nhau

            # Biểu đồ cột trồng (stacked bar) và biểu đồ đường cho tỷ lệ tăng trưởng tài sản cố định
            with col1:
                fig1 = go.Figure()

                for col, color in zip(['cash', 'inventory', 'fixed_asset'], ['blue', 'green', 'orange']):
                    fig1.add_trace(go.Bar(x=df.index, y=df[col], name= col.replace('_',' ').capitalize(), marker_color=color))

                fig1.add_trace(go.Scatter(x=df.index, y=df['fixed_asset_growth'], name='Fixed Asset Growth (%)',
                                        mode='lines+markers', marker=dict(color='red', size=10), yaxis='y2'))

                fig1.update_layout(title="Tăng trưởng Tài Sản", xaxis_title="Period", yaxis_title="Giá trị tài sản",
                                yaxis2=dict(title="Tăng trưởng (%)", overlaying='y', side='right', showgrid=False),
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig1, use_container_width=True)

            # Biểu đồ đường (line chart) cho hệ số đòn bẩy
            with col2:
                fig2 = go.Figure()

                for col, color in zip(['debt_to_equity', 'long_debt_to_long_asset', 'short_debt_to_short_asset'],
                                    ['blue', 'green', 'orange']):
                    fig2.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

                fig2.update_layout(title="Hệ số Đòn Bẩy", xaxis_title="Period", yaxis_title="Hệ số Đòn Bẩy",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig2, use_container_width=True)

            # Biểu đồ cột trồng (100%) cho các khoản nợ & phải trả
            with col3:
                fig3 = go.Figure()

                for col, color in zip(['rate_payable','rate_short_debt','rate_long_debt','rate_other_debt'],
                                    ['blue', 'green', 'orange', 'red']):
                    fig3.add_trace(go.Bar(x=df.index, y=df[col], name= col.replace('_',' ').capitalize(), marker_color = color))

                fig3.update_layout(title="Tỷ lệ nợ & phải trả", xaxis_title="Period", yaxis_title="Tỷ lệ (%)",
                                
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig3, use_container_width=True)

            with col1:
                fig4 = go.Figure()

                for col, color in zip(['short_invest', 'short_receivable'],
                                    ['blue', 'green']):
                    fig4.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

                fig4.update_layout(title="Đầu tư và phải thu ngắn hạn qua các năm", xaxis_title="Period", yaxis_title="VND",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

                st.plotly_chart(fig4, use_container_width=True)


            with col2:
                fig4 = go.Figure()

                fig4.add_trace(go.Bar(x=df.index, y=df['un_distributed_income'], name='Un-distributed income', marker_color='blue'))
                fig4.add_trace(go.Bar(x=df.index, y=df['minor_share_holder_profit'], name='Minor Share Holder Profit', marker_color='green'))

                fig4.update_layout(title="Un-distributed Profit vs Minor Share Holder Profit qua các năm",
                                xaxis_title="Period", yaxis_title="VND",
                                barmode='group',  # Biểu đồ cột ghép
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
                st.plotly_chart(fig4, use_container_width=True)
    #--------------------------------Cho cổ phiếu bank---------------------------------------------------------------
    elif selected_industry == 'Nhóm Ngân Hàng':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.balance_sheet(period='year')
        # Cấu hình bố cục trang
        col1, col2, col3 = st.columns(3)

        with col1:

            fig11 = go.Figure()
            df_filtered = df[df.index == '2023']
            df_filtered = df_filtered[['cash', 'fixed_asset', 'central_bank_deposit', 'other_bank_deposit', 'other_bank_loan', 'stock_invest', 'customer_loan']]
            first_row_values = df_filtered.iloc[0].to_dict()
            df_melted = pd.DataFrame(list(first_row_values.items()), columns=['Category', 'Value'])
            df_melted['Category'] = df_melted['Category'].str.replace('_', ' ')

            fig11 = px.treemap(df_melted, path=['Category'], values='Value', 
                            title='Treemap of Financial Data')
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
            df['fixed_asset_growth'] = df['fixed_asset'] / df['asset'] * 100
            for col, color in zip(['fixed_asset', 'customer_loan', 'net_customer_loan'], ['green', 'orange','yellow']):
                fig12.add_trace(go.Bar(x=df.index, y=df[col], name= col.replace('_',' ').capitalize(), marker_color=color))
            fig12.add_trace(go.Scatter(x=df.index, y=df['fixed_asset_growth'], name='Fixed Asset Growth (%)',
                                        mode='lines+markers', marker=dict(color='red', size=10), yaxis='y2'))

            fig12.update_layout(title="Tăng trưởng Tài Sản", xaxis_title="Period", yaxis_title="Giá trị tài sản",
                                yaxis2=dict(title="Tăng trưởng (%)", overlaying='y', side='right', showgrid=False),
                                barmode='stack', autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
            st.plotly_chart(fig12, use_container_width=True)
        with col3:
            st.empty()
        with col1:
            fig22 = go.Figure()
            df_filtered = df[df.index == '2023']
            df_filtered['total_loan'] = df_filtered['owe_other_bank'] + df_filtered['owe_central_bank'] + df_filtered['valuable_paper']+ df_filtered['payable_interest'] + df_filtered['receivable_interest'] + df_filtered['other_debt'] + df_filtered['deposit']
            df_filtered['rate_owe_other_bank'] = df_filtered['owe_other_bank']/df_filtered['total_loan'] 
            df_filtered['rate_owe_central_bank'] = df_filtered['owe_central_bank']/df_filtered['total_loan'] 
            df_filtered['rate_valuable_paper'] = df_filtered['valuable_paper']/df_filtered['total_loan'] 
            df_filtered['rate_payable_interest'] = df_filtered['payable_interest']/df_filtered['total_loan'] 
            df_filtered['rate_receivable_interest'] = df_filtered['receivable_interest']/df_filtered['total_loan'] 
            df_filtered['rate_ther_debt'] = df_filtered['other_debt']/df_filtered['total_loan'] 
            df_filtered['rate_deposit'] = df_filtered['deposit']/df_filtered['total_loan'] 
            
            pie_data = {
            'Category': ['Owe Other Bank', 'Owe Central Bank', 'Valuable Paper', 'Payable Interest', 'Receivable Interest', 'Other Debt', 'Deposit'],
            'Rate': [
                df_filtered['rate_owe_other_bank'].iloc[0],
                df_filtered['rate_owe_central_bank'].iloc[0],
                df_filtered['rate_valuable_paper'].iloc[0],
                df_filtered['rate_payable_interest'].iloc[0],
                df_filtered['rate_receivable_interest'].iloc[0],
                df_filtered['rate_ther_debt'].iloc[0],
                df_filtered['rate_deposit'].iloc[0]
            ]}
            df_pie = pd.DataFrame(pie_data)
            fig22 = px.pie(df_pie, names='Category', values='Rate', title='Pie Chart of Financial Ratios')
            st.plotly_chart(fig22, use_container_width=True)

        with col2:
            fig22 =  go.Figure()
        #nợ trên vốn chủ sở hữu= Tổng nợ/Vốn chủ sở hữu
        #Tỷ lệ nợ trên tổng tài sản = Tổng nợ/Tổng tài sản
        #Lần lãi bao phủ lãi vay = LNTT và Lãi vay/lãi vay
            df['Tỷ lệ nợ trên vốn chủ'] = df['debt']/df['equity']
            df['Tỷ lệ nợ trên tổng tài sản'] = df['debt']/df['asset']
            
            for col, color in zip(['Tỷ lệ nợ trên vốn chủ', 'Tỷ lệ nợ trên tổng tài sản'],
                                    ['blue', 'green']):
                    fig22.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

            fig22.update_layout(title="Hệ số Đòn Bẩy", xaxis_title="Period", yaxis_title="Hệ số Đòn Bẩy",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig22, use_container_width=True)

        with col3: 
            fig23 = go.Figure()
            df.rename(columns={'bad_loan':'Nợ xấu của KH','provision':'Dự phòng cho nợ xấu'}, inplace = True)
            for col, color in zip(['Nợ xấu của KH', 'Dự phòng cho nợ xấu'],
                                    ['blue', 'green']):
                    fig23.add_trace(go.Scatter(x=df.index, y=df[col], name=col.replace('_', ' ').capitalize(),
                                            mode='lines+markers', marker=dict(color=color, size=10)))

            fig23.update_layout(title="Trendlines nợ xấu và dự phòng nợ xấu của NH", xaxis_title="Period", yaxis_title="Hệ số Đòn Bẩy",
                                autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig23, use_container_width=True)

        with col1:
            fig33 = go.Figure()

            fig33.add_trace(go.Bar(x=df.index, y=df['capital'],name='Vốn điều lệ', marker_color='blue'))
            fig33.add_trace(go.Bar(x=df.index, y=df['equity'],name='Vốn chủ sở hữu', marker_color='green'))

            fig33.update_layout( title="Capital và Equity theo thời gian", xaxis_title="Period", yaxis_title="Giá trị", barmode='group',
            autosize=True,height=350, margin=dict(l=0, r=0, t=20, b=0), legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5))
        # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig33, use_container_width=True)

        with col2:
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
                title="Tỷ lệ tăng trưởng của LNST chưa phân phối và Lợi nhuận của cổ đông thiểu số",
                xaxis_title="Period",
                yaxis_title="Tỷ lệ tăng trưởng (%)",
                autosize=True,
                height=500,
                margin=dict(l=0, r=0, t=40, b=0),
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
            )

            # Hiển thị biểu đồ trong Streamlit
            st.plotly_chart(fig32, use_container_width=True)
            

    df = stock.finance.income_statement(period='year')
    #df['Biên lợi nhuận'] = (df['LN trước thuế'] - df['Thuế TNDN'])/ df['Doanh thu (Tỷ đồng)']
    #df = df[['Biên lợi nhuận','Doanh thu (Tỷ đồng)','Lãi/Lỗ từ hoạt động kinh doanh','Lợi nhuận thuần']]
    #df = df.loc[:,~df.columns.duplicated()]
#------------------------------ Kết quả kinh doanh------------------------------
with tabs[1]:
#------------------------------ Nhóm ngành khác------------------------------
    selected_industry =  st.session_state['selected_industry']
    if selected_industry == 'Nhóm Ngành Khác':
        df = Vnstock().stock(symbol=selected_stock, source='TCBS').finance.income_statement(period='year')
        df['cost_of_good_sold'] = df['cost_of_good_sold']*-1
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = go.Figure()

            # Cột ghép: revenue
            fig.add_trace(go.Bar(x=df.index, y=df['revenue'], name='Revenue',marker_color='blue', offsetgroup=0))
            # Cột trồng: cost_of_good_sold và gross_profit
            fig.add_trace(go.Bar(x=df.index,y=df['cost_of_good_sold'], name='Cost of Goods Sold', marker_color='orange',offsetgroup=1))
            fig.add_trace(go.Bar(x=df.index,y=df['gross_profit'], name='Gross Profit', marker_color='green', base=df['cost_of_good_sold'],offsetgroup=1 ))

            # Đường biểu diễn tăng trưởng: year_revenue_growth
            fig.add_trace(go.Scatter( x=df.index,y=df['year_revenue_growth'], mode='lines+markers', name='Year Revenue Growth (%)',
                                        marker=dict(color='red', size=8),yaxis='y2' ))
            # Cập nhật layout cho biểu đồ
            fig.update_layout(
                title="Biểu đồ cột ghép, cột trồng và đường tăng trưởng",xaxis_title="Period",yaxis_title="Giá trị (VND)",
                yaxis2=dict(title="Tăng trưởng (%)",overlaying='y',side='right',showgrid=False
                ),barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
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
            fig12.update_layout(title="Tỷ lệ tăng trưởng Lợi nhuận và Doanh thu qua các năm", xaxis_title="Period", yaxis_title="Tỷ lệ (%)",
                                        autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig12, use_container_width=True)

        with col3:
            fig4 = go.Figure()

            fig4.add_trace(go.Bar(x=df.index, y=df['cost_of_good_sold'], name='cost_of_good_sold', marker_color='blue'))
            fig4.add_trace(go.Bar(x=df.index, y=df['operation_expense'], name='operation_expense', marker_color='green'))
            fig4.add_trace(go.Bar(x=df.index, y=df['interest_expense'], name='interest_expense', marker_color='red'))

            fig4.update_layout(title="Chi phí qua các năm",
                            xaxis_title="Period", yaxis_title="VND",
                            barmode='group',  # Biểu đồ cột ghép
                            autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                            legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))
            st.plotly_chart(fig4, use_container_width=True)
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            fig = go.Figure()

            # Cột ghép: revenue
            fig.add_trace(go.Bar(x=df.index, y=df['revenue'], name='Thu nhập lãi thuần',marker_color='blue', offsetgroup=0))
            fig.add_trace(go.Bar(x=df.index,y=df['operation_profit'], name='Tổng thu nhập hoạt động', marker_color='green',offsetgroup=1 ))
            fig.add_trace(go.Bar(x=df.index,y=df['post_tax_profit'], name='Lợi nhuận sau thuế', marker_color='orange',offsetgroup=2 ))

            fig.update_layout(
                title="Biểu đồ thể hiện TN lãi thuần, TN hoạt động và LNST",xaxis_title="Period",yaxis_title="Giá trị (VND)",
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
            fig12.update_layout(title="Tỷ lệ tăng trưởng Lợi nhuận và Thu nhập", xaxis_title="Period", yaxis_title="Tỷ lệ (%)",
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
                title="Biểu đồ thể hiện xu hướng dòng tiền qua các năm",xaxis_title="Period",yaxis_title="Giá trị (VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig13, use_container_width=True)

        with col1:
            fig21 = go.Figure()
            fig21.add_trace(go.Bar(x=df.index, y=df['share_holder_income'], name='LNST của cổ đông',marker_color='blue', offsetgroup=0))
            # Đường biểu diễn tăng trưởng: year_revenue_growth
            fig21.add_trace(go.Scatter( x=df.index,y=df['year_share_holder_income_growth'], mode='lines+markers', name='Year Revenue Growth (%)',
                                        marker=dict(color='red', size=8),yaxis='y2' ))
            # Cập nhật layout cho biểu đồ
            fig21.update_layout(
                title="Biểu đồ thể hiện LNST của cổ đông",xaxis_title="Period",yaxis_title="Giá trị (VND)",
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
                title="Thu nhập khác từ hoạt động đầu tư và dịch vụ",xaxis_title="Period",yaxis_title="Giá trị (VND)",
                barmode='group', autosize=True,
                height=400,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.55   , xanchor="center", x=0.5)
            )
            st.plotly_chart(fig22, use_container_width=True)
#------------------------------Lưu chuyển tiền tệ------------------------------
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
        st.markdown(
            """
            <style>
            .card {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                width: 60%; /* Điều chỉnh width để thẻ ngắn hơn */
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
        with col1:
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
        # Dữ liệu cho biểu đồ thác dòng tiền
        categories = ['Hoạt động kinh doanh', 'Hoạt động đầu tư', 'Hoạt động tài chính']
        values = [
            latest_data['Lưu chuyển tiền tệ ròng từ các hoạt động SXKD'],
            latest_data['Lưu chuyển từ hoạt động đầu tư'],
            latest_data['Lưu chuyển tiền từ hoạt động tài chính']
        ]

        # Tạo biểu đồ Waterfall
        with col2:
            fig = go.Figure(go.Waterfall(
                name="Dòng tiền",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=categories,
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig.update_layout(
                title="Biểu đồ thác dòng tiền",
                waterfallgap=0.3
            )

            # Hiển thị biểu đồ trong cột col2
            st.plotly_chart(fig)


        years = df['Năm']  
        with col3:
            line_fig = px.line(
                x=years,
                y=df['Lưu chuyển tiền thuần trong kỳ'],
                labels={'x': 'Năm', 'y': 'Lưu chuyển tiền thuần trong kỳ'},
                title='Lưu chuyển tiền thuần trong kỳ qua các năm'
            )

            line_fig.update_layout(xaxis_title='Năm', yaxis_title='Lưu chuyển tiền thuần')

            # Hiển thị biểu đồ trong cột col3
            st.plotly_chart(line_fig)   

        with col1:
            fig21 = go.Figure()

            for col, color in zip(['Tiền thu được từ thanh lý tài sản cố định', 'Tiền thu từ việc bán các khoản đầu tư vào doanh nghiệp khác'],
                                ['blue', 'green']):
                fig21.add_trace(go.Bar(x=df['Năm'],y=df[col],name=col.replace('_', ' ').capitalize(),marker_color=color))

            for col, color in zip(['Mua sắm TSCĐ', 'Đầu tư vào các doanh nghiệp khác'],['red', 'orange']):
                fig21.add_trace(go.Bar(x=df['Năm'],y=df[col],name=col.replace('_', ' ').capitalize(),marker_color=color))

            fig21.update_layout(
                title="Biểu đồ chồng-Hoạt động đầu tư",xaxis_title="Năm",yaxis_title="Tiền (VNĐ)",barmode='relative',  # Chế độ chồng, hỗ trợ giá trị âm
                autosize=True,height=300,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.9, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig21, use_container_width=True)

        with col2:
            fig22 = go.Figure()
            for col, color in zip(['Cổ tức đã trả', 'Chi từ các quỹ của TCTD'],
                                            ['blue', 'green']):
                fig22.add_trace(go.Scatter(x=df['Năm'], y=df[col], name=col.replace('_', ' ').capitalize(),
                                                    mode='lines+markers', marker=dict(color=color, size=10)))

            fig22.update_layout(title="Biểu đồ đường hoạt động tài chính", xaxis_title="Năm", yaxis_title="Tiền (VNĐ)",
                                        autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig22, use_container_width=True)
    else:
        df = Vnstock().stock(symbol=selected_stock, source='VCI').finance.cash_flow(period='year', lang='vi')
        latest_data = df.iloc[0]  

        # Thêm CSS tùy chỉnh cho các thẻ (cards)
        st.markdown(
            """
            <style>
            .card {
                background-color: #f0f2f6;
                border-radius: 10px;
                padding: 20px;
                width: 60%; /* Điều chỉnh width để thẻ ngắn hơn */
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


        # Tạo cột hiển thị
        col1, col2, col3 = st.columns(3)

        # Thêm các card vào cột col1 với CSS đã tạo
        with col1:
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
        # Dữ liệu cho biểu đồ thác dòng tiền
        categories = ['Hoạt động kinh doanh', 'Hoạt động đầu tư', 'Hoạt động tài chính']
        values = [
            latest_data['Lưu chuyển tiền tệ ròng từ các hoạt động SXKD'],
            latest_data['Lưu chuyển từ hoạt động đầu tư'],
            latest_data['Lưu chuyển tiền từ hoạt động tài chính']
        ]

        # Tạo biểu đồ Waterfall
        with col2:
            fig = go.Figure(go.Waterfall(
                name="Dòng tiền",
                orientation="v",
                measure=["relative", "relative", "total"],
                x=categories,
                y=values,
                connector={"line": {"color": "rgb(63, 63, 63)"}},
            ))

            fig.update_layout(
                title="Biểu đồ thác dòng tiền",
                waterfallgap=0.3
            )

            # Hiển thị biểu đồ trong cột col2
            st.plotly_chart(fig)


        years = df['Năm']  
        with col3:
            line_fig = px.line(
                x=years,
                y=df['Lưu chuyển tiền thuần trong kỳ'],
                labels={'x': 'Năm', 'y': 'Lưu chuyển tiền thuần trong kỳ'},
                title='Lưu chuyển tiền thuần trong kỳ qua các năm'
            )

            line_fig.update_layout(xaxis_title='Năm', yaxis_title='Lưu chuyển tiền thuần')

            # Hiển thị biểu đồ trong cột col3
            st.plotly_chart(line_fig)   

        with col1:
            fig21 = go.Figure()

            for col, color in zip(['Tiền thu được từ thanh lý tài sản cố định', 'Tiền thu được các khoản đi vay'],
                                ['blue', 'green']):
                fig21.add_trace(go.Bar(x=df['Năm'],y=df[col],name=col.replace('_', ' ').capitalize(),marker_color=color))
            fig21.update_layout(
                title="Biểu đồ chồng-Hoạt động đầu tư",xaxis_title="Năm",yaxis_title="Tiền (VNĐ)",barmode='relative',  # Chế độ chồng, hỗ trợ giá trị âm
                autosize=True,height=300,margin=dict(l=0, r=0, t=40, b=0),legend=dict(orientation="h", yanchor="bottom", y=-0.9, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig21, use_container_width=True)

        with col2:
            fig22 = go.Figure()
            for col, color in zip(['Cổ tức đã trả', 'Tiền trả các khoản đi vay'],
                                            ['blue', 'green']):
                fig22.add_trace(go.Scatter(x=df['Năm'], y=df[col], name=col.replace('_', ' ').capitalize(),
                                                    mode='lines+markers', marker=dict(color=color, size=10)))

            fig22.update_layout(title="Biểu đồ đường hoạt động tài chính", xaxis_title="Năm", yaxis_title="Tiền (VNĐ)",
                                        autosize=True, height=300, margin=dict(l=0, r=0, t=40, b=0),
                                        legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5))

            st.plotly_chart(fig22, use_container_width=True)


