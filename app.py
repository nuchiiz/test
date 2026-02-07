import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS สำหรับ UI: หัวข้อชิดซ้าย / ตารางและเนื้อหาในตารางอยู่ตรงกลาง
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    /* ส่วนประกอบทั่วไป */
    .stExpander { border: 2px solid #000000 !important; background-color: #f8f9fa !important; border-radius: 10px !important; }
    .stTextInput input, .stNumberInput input { font-size: 18px !important; font-weight: bold !important; border: 2px solid #000 !important; }
    
    /* 1. ปรับหัวข้อและข้อความทั่วไปให้ชิดซ้าย (Left Align) */
    h1, h2, h3, h5, .stMarkdown p, .stCaption { 
        text-align: left !important; 
    }
    
    /* 2. ปรับ Metrics ให้กึ่งกลางเพื่อความสวยงาม */
    [data-testid="stMetricValue"], [data-testid="stMetricLabel"] {
        text-align: center;
        justify-content: center;
    }
    [data-testid="stMetric"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    
    /* 3. จัดการตาราง (Table) */
    .stTable td, .stTable th {
        text-align: center !important;
        vertical-align: middle !important;
    }
    .stTable { 
        width: 100%;
        margin-left: auto;
        margin-right: auto;
    }
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

# --- หัวข้อ ---
st.markdown("<h1>🏗️ ระบบควบคุมวัสดุชลประทาน (V.2)</h1>", unsafe_allow_html=True)
st.markdown("<h5>อ้างอิงประกาศกรมบัญชีกลาง ฉบับปรับปรุง ปี 2565</h5>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        # ข้อมูลโครงการ
        col_p1, col_p2 = st.columns([1, 1])
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="พิมพ์ชื่อสำนัก...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="พิมพ์ชื่อโครงการ...")
        
        calc_date = datetime.now().strftime("%d/%m/%Y")
        st.caption(f"วันที่บันทึกระบบ: {calc_date}")
            
        p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก", "เหล็กเส้นเสริมคอนกรีต", "ลวดผูกเหล็กเสริม"]

        # 1. แผนงาน (ปรับปรุงช่องกรอกให้เป็นค่าว่าง)
        st.markdown("### 📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุที่ได้รับอนุมัติ", expanded=True):
            col_plan = st.columns(len(p_names)) 
            planned_values = {}
            for i, name in enumerate(p_names):
                # ใช้ value=None และ placeholder เพื่อให้เป็นช่องว่างพร้อมพิมพ์
                val = col_plan[i].number_input(f"{name}", min_value=0.0, value=None, placeholder="กรอกแผน...", key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # 2. รายการงาน (ปรับปรุงช่องกรอกปริมาณงาน)
        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        # ปรับเป็นค่าว่างเช่นกัน
        q_val = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.0, value=None, placeholder="กรอกปริมาณงาน...", key="work_qty")
        
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True):
            if q_val is not None and q_val > 0:
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

            m_cols = st.columns(4) 
            for i, name in enumerate(p_names):
                m_cols[i % 4].metric(label=name, value=f"{totals[name]:,.2f}")

            df_comp = pd.DataFrame([{
                "รายการวัสดุ": name,
                "แผนงาน (Planned)": planned_values[name],
                "คำนวณจริง (Actual)": totals[name],
                "ส่วนต่าง (+เหลือ/-เกิน)": planned_values[name] - totals[name],
                "สถานะ": "✅ น้อยกว่าหรือเท่ากับแผน" if (planned_values[name] - totals[name]) >= 0 else "⚠️ เกินกว่าแผน"
            } for name in p_names])

            def style_center(v):
                color = 'red' if isinstance(v, (int, float)) and v < 0 else ('green' if isinstance(v, (int, float)) and v > 0 else 'black')
                return f'color: {color}; font-weight: bold; text-align: center;'

            st.table(df_comp.style.format({
                "แผนงาน (Planned)": "{:,.2f}", "คำนวณจริง (Actual)": "{:,.2f}", "ส่วนต่าง (+เหลือ/-เกิน)": "{:,.2f}"
            }).set_properties(**{'text-align': 'center'}).applymap(style_center, subset=["ส่วนต่าง (+เหลือ/-เกิน)"]))

            # 5. Export
            st.markdown("### 📤 5. ส่งออกเอกสาร")
            c_ex1, c_ex2 = st.columns(2)
            csv_data = pd.DataFrame([{"งาน": i['ประเภทงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history]).to_csv(index=False).encode('utf-8-sig')
            c_ex1.download_button("📥 ดาวน์โหลด CSV", csv_data, f'Summary_{datetime.now().strftime("%Y%m%d")}.csv', "text/csv", use_container_width=True)
            if c_ex2.button("🚫 ล้างข้อมูล", use_container_width=True):
                st.session_state.calc_history = []; st.rerun()

            st.divider()
            st.link_button("🔗 เปิดเอกสารอ้างอิงหลักเกณฑ์ราคากลาง ฉบับปรับปรุง วันที่ 2 สิงหาคม 2565", "https://drive.google.com/file/d/1tCep-NffAYB2QtDaPo7b2RwTuy7O_aw8/view", use_container_width=True)

    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล CSV ในระบบ")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
