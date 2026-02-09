import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: ตกแต่ง UI ทั้งหมด
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Sarabun', sans-serif; 
        background-color: #ffffff !important; 
    }
    [data-testid="column"] { display: flex; align-items: flex-end; }
    
    /* ปรับแต่งช่องกรอกข้อมูล */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
    }
    
    /* ปรับสี Placeholder ให้จาง (0.00) */
    ::placeholder { color: #aaaaaa !important; opacity: 1; }

    /* จัดตารางให้กึ่งกลาง */
    .stTable { width: 100%; border: 1px solid #000; }
    .stTable th { text-align: center !important; background-color: #f2f2f2 !important; border: 1px solid #000 !important; }
    .stTable td { text-align: center !important; vertical-align: middle !important; border: 1px solid #ddd !important; }

    /* ปุ่มกดหลัก */
    div.stButton > button {
        width: 100%; height: 3.0rem; border-radius: 8px !important;
        background-color: #007bff; color: white; border: 1px solid #000; font-weight: bold;
    }
    
    /* กล่องเอกสารอ้างอิง */
    .ref-box {
        background-color: #e9ecef; 
        padding: 15px; 
        border-radius: 8px; 
        border-left: 6px solid #007bff; 
        margin-bottom: 25px;
    }
    
    .stExpander { border: 2px solid #000000 !important; background-color: #ffffff !important; border-radius: 10px !important; }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "ตารางคำนวณอัตราราคางานคอนกรีตและหิน-กรมบัญชีกลาง3.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip', low_memory=False)
            return df
        except: continue
    return None

def to_excel(df_detailed, df_summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
        df_detailed.to_excel(writer, sheet_name='รายการงานย่อย', index=False)
    return output.getvalue()

if 'calc_history' not in st.session_state:
