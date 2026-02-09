import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: พื้นหลังขาว, กล่องเทาขอบดำ, ปรับฟอนต์ให้เด่นชัด
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Sarabun', sans-serif; 
        background-color: #ffffff !important; 
    }
    
    /* จัดการ Alignment ให้ปุ่มและช่องกรอกขนานกัน */
    [data-testid="column"] { display: flex; align-items: flex-end; }

    /* กล่องข้อความ: พื้นสีเทา ขอบดำ */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
        color: #000000 !important;
    }

    /* ปุ่มกดหลัก */
    div.stButton > button {
        width: 100%;
        height: 3.0rem;
        border-radius: 8px !important;
        background-color: #007bff;
        color: white;
        border: 1px solid #000;
        font-weight: bold;
    }

    /* ตกแต่งตารางและส่วนขยาย */
    .stTable { background-color: #ffffff; border: 1px solid #000; }
    .stExpander { border: 2px solid #000000 !important; background-color: #ffffff !important; border-radius: 10px !important; }
    
    /* ปรับตัวเลข Metric */
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold !important; color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

@st.
