
import streamlit as st
def page2():
    st.title("Second page")

pg = st.navigation([
    st.Page("overview.py", title="1. Tổng quan "),
    st.Page("fundamental_analysis.py", title="2. Phân tích cơ bản"),
    st.Page("technical_analysis.py", title="3. Phân tích kỹ thuật"),
])
pg.run()