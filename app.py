import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro", layout="wide")

# ปรับปรุง CSS ให้สวยงามและอ่านง่าย
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    .stExpander { border: 2px solid #000000 !important; background-color: #eceff1 !important; border-radius: 10px !important; }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: 800 !important; color: #000 !important; }
    .stTextInput input, .stNumberInput input { font-size: 18px !important; font-weight: bold !important; border: 2px solid #000 !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "ตารางคำนวณอัตราราคางานคอนกรีตและหิน-กรมบัญชีกลาง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except: continue
    return None

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ตารางคำนวณอัตรางานคอนกรีตและหิน")
st.markdown("##### ตามหลักเกณฑ์การคำนวณราคากลางงานก่อสร้างชลประทาน ฉบับปรับปรุง 2565")

try:
    df = load_data()
    if df is not None:
        # --- ข้อมูลโครงการ ---
        col_p1, col_p2 = st.columns([1, 1])
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="พิมพ์ชื่อสำนักหรือโครงการ...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="พิมพ์ชื่อโครงการ...")
        
        calc_date = datetime.now().strftime("%d/%m/%Y")
        st.caption(f"วันที่บันทึกระบบ: {calc_date}")
            
        # 1. ตั้งค่าแผนงาน (Planned)
        st.subheader("📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ปริมาณวัสดุที่ได้รับอนุมัติตามแผน", expanded=True):
            col_plan = st.columns(
