import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS สำหรับปรับกล่องข้อความให้มีขอบ ขนาดมาตรฐาน และระดับที่ตรงกันเป๊ะ
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

    /* 1. จัดระดับให้ Column ทุกอันวางฐาน (Bottom) ตรงกัน */
    [data-testid="column"] {
        display: flex;
        align-items: flex-end; /* บังคับให้วัตถุชิดขอบล่างของคอลัมน์ */
    }

    /* 2. ปรับขนาดกล่องข้อความและขอบ (Input, Selectbox, Number) */
    /* ล็อกความสูงไว้ที่ 45px เพื่อความสม่ำเสมอ */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        height: 45px !important; 
        font-size: 16px !important;
        font-weight: bold !important;
        border: 2px solid #007bff !important; /* เปลี่ยนเป็นสีฟ้าเพื่อให้ขอบชัดเจน */
        border-radius: 8px !important;
        background-color: white !important;
    }

    /* 3. ปรับขนาดและระดับของปุ่มให้เท่ากับกล่องข้อความ */
    div.stButton > button {
        height: 45px !important; /* สูงเท่ากับช่องกรอก */
        width: 100%;
        border-radius: 8px !important;
        font-weight: bold !important;
        display: flex;
        align-items: center;
        justify-content: center;
        border: 2px solid #007bff !important;
    }
    
    /* ปุ่มแบบ Primary (เพิ่มรายการ) */
    div.stButton > button[kind="primary"] {
        background-color: #007bff !important;
        color: white !important;
        border: none !important;
    }

    /* 4. ตกแต่งหัวข้อและตาราง */
    h1, h2, h3, h5 { text-align: left !important; color: #1f1f2e; }
    .stTable { width: 100%; border: 1px solid #ddd; border-radius: 10px; overflow: hidden; }
    
    /* ปรับแต่ง Label ด้านบนให้มีระยะห่างที่พอดี */
    label p {
        margin-bottom: 6px !important;
        font-weight: 700 !important;
        color: #333;
    }

    /* Metrics กึ่งกลาง */
    [data-testid="stMetricValue"] { font-weight: bold; font-size: 24px; text-align: center; }
    [data-testid="stMetricLabel"] { text-align: center; width: 100%; }
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

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

# --- ส่วนหัวข้อ ---
st.markdown("<h1>🏗️ ระบบควบคุมวัสดุชลประทาน (V.2)</h1>", unsafe_allow_html=True)
st.markdown("<h5>อ้างอิงประกาศกรมบัญชีกลาง ฉบับปรับปรุง ปี 2565</h5>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        # ข้อมูลโครงการ
        col_p1, col_p2 = st.columns([1, 1])
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="กรอกชื่อหน่วยงาน...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="กรอกชื่อโครงการ...")
        
        st.caption(f"📅 อัปเดตล่าสุด: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
            
        p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก", "เหล็กเส้นเสริมคอนกรีต", "ลวดผูกเหล็กเสริม"]

        # 1. แผนงาน
        st.markdown("### 📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุตามแผนงานที่ได้รับอนุมัติ", expanded=True):
            col_plan = st.columns(len(p_names)) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i].number_input(f"{name}", min_value=0.0, step=0.01, key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # 2. รายการงานก่อสร้าง (จุดที่จัดระดับกล่องให้ตรงกัน)
        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        col_in1, col_in2, col_in3 = st.columns([3, 1.2, 0.8]) 
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        q_val = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.0, step=0.01, key="work_qty")
        
        # ปุ่ม "เพิ่มรายการ"
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True, type="primary"):
            if q_val > 0:
                selected_row = df[df[0] == selected_work].iloc[0]
                m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10, "เหล็กเส้นเสริมคอนกรีต": 12, "ลวดผูกเหล็กเสริม": 14}
                temp_details = {}
                for m_name, idx in m_map.items():
                    if idx < len(selected_row):
                        try:
                            val_str = str(selected_row[idx]).replace(',', '').replace('-', '').strip()
                            if val_str and val_str != "nan":
                                temp_details[m_name] = float(val_str) * q_val
                        except: continue
                st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": q_val, "รายละเอียด": temp_details})
                st.rerun()

        # 3. รายการสะสม
        if st.session_state.calc_history:
            st.markdown("### 📋 3. รายการที่บันทึกไว้")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']:,} หน่วย)"):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.3f}**")
                    if st.button(f"🗑️ ลบรายการ", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i); st.rerun()

            # 4. สรุปผล
            st.divider()
            st.markdown("### 📊 4. สรุปผลและเปรียบเทียบแผนงาน")
            
            totals = {k: sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history) for k in p_names}
            
            # Metric Display
            m_cols = st.columns(len(p_names))
            for i, name in enumerate(p_names):
                m_cols[i].metric(label=name, value=f"{totals[name]:,.2f}")

            # ตารางสรุป
            df_comp = pd.DataFrame([{
                "รายการวัสดุ": name,
                "แผนงาน (Planned)": planned_values[name],
                "คำนวณจริง (Actual)": totals[name],
                "ส่วนต่าง (+เหลือ/-เกิน)": planned_values[name] - totals[name],
                "สถานะ": "✅ ปกติ" if (planned_values[name] - totals[name]) >= 0 else "⚠️ เกินกว่าแผน"
            } for name in p_names])

            st.table(df_comp.style.format({
                "แผนงาน (Planned)": "{:,.2f}", "คำนวณจริง (Actual)": "{:,.2f}", "ส่วนต่าง (+เหลือ/-เกิน)": "{:,.2f}"
            }))

            # 5. ส่งออกเอกสาร (ระดับปุ่มเท่ากัน)
            st.markdown("### 📤 5. ส่งออกเอกสาร")
            c_ex1, c_ex2 = st.columns([1, 1])
            
            csv_data = pd.DataFrame([{"งาน": i['ประเภทงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history]).to_csv(index=False).encode('utf-8-sig')
            c_ex1.download_button("📥 ดาวน์โหลด CSV", csv_data, f'Summary_{datetime.now().strftime("%Y%m%d")}.csv', "text/csv", use_container_width=True)
            
            if c_ex2.button("🚫 ล้างข้อมูลทั้งหมด", use_container_width=True):
                st.session_state.calc_history = []; st.rerun()

    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล CSV กรุณาตรวจสอบการเชื่อมต่อข้อมูล")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
