import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: พื้นหลังขาว, กล่องเทาขอบดำ, ปรับฟอนต์
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Sarabun', sans-serif; 
        background-color: #ffffff !important; 
    }
    
    /* จัดการ Alignment */
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

    /* ปุ่มกด */
    div.stButton > button {
        width: 100%;
        height: 3.0rem;
        border-radius: 8px !important;
        background-color: #007bff;
        color: white;
        border: 1px solid #000;
    }

    /* ตกแต่งตารางและส่วนอื่นๆ */
    .stTable { background-color: #ffffff; border: 1px solid #000; }
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

# ฟังก์ชัน Export Excel
def to_excel(df_detailed, df_summary, office, project):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_detailed.to_excel(writer, sheet_name='รายการงาน', index=False)
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
    return output.getvalue()

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.markdown("<h1>🏗️ การคำนวณอัตราราคางานคอนกรีตและหิน</h1>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        col_p1, col_p2 = st.columns(2)
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="ระบุชื่อสำนัก...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="ระบุชื่องาน...")
        
        st.caption(f"วันที่บันทึกระบบ: {datetime.now().strftime('%d/%m/%Y')}")
        
        p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก", "เหล็กเส้นเสริมคอนกรีต", "ลวดผูกเหล็กเสริม"]

        # 1. แผนงาน
        st.markdown("### 📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุที่ได้รับอนุมัติ", expanded=True):
            col_plan = st.columns(len(p_names)) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i].number_input(f"{name}", min_value=0.0, value=None, placeholder="0.0", key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # 2. ราย
