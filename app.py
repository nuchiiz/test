import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro", layout="wide")

# CSS สำหรับความสวยงามและ High Contrast
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
            
        # 1. ตั้งค่าแผนงาน (Planned) - ปรับให้เป็นช่องว่าง (None) เพื่อให้กรอกเลขได้ทันที
        st.subheader("📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ปริมาณวัสดุที่ได้รับอนุมัติตามแผน", expanded=True):
            col_plan = st.columns(5)
            p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก"]
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i].number_input(f"{name}", min_value=0.0, value=None, placeholder="กรอกจำนวน...", key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # 2. เพิ่มรายการงาน - ปรับช่องปริมาณงานให้ว่าง
        st.subheader("➕ 2. รายการงานคอนกรีตและหิน")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกงานก่อสร้าง:", work_list)
        q_val = col_in2.number_input("ปริมาณงานที่ทำ:", min_value=0.0, value=None, placeholder="กรอกเลข...")
        
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True):
            if q_val is not None and q_val > 0:
                selected_row = df[df[0] == selected_work].iloc[0]
                m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10}
                temp_details = {}
                for m_name, idx in m_map.items():
                    try:
                        if idx < len(selected_row):
                            raw_val = str(selected_row[idx]).replace(',', '')
                            rate_val = float(raw_val)
                            if rate_val > 0: temp_details[m_name] = rate_val * q_val
                    except: continue
                st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": q_val, "รายละเอียด": temp_details})
                st.rerun()
            else:
                st.warning("⚠️ กรุณากรอกปริมาณงานก่อนกดเพิ่มรายการ")

        # 3. รายการบันทึกสะสม
        if st.session_state.calc_history:
            st.subheader("📋 3. รายการบันทึกสะสม")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']} หน่วย)", expanded=False):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.2f}**")
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # 4. สรุปผล
            st.divider()
            st.subheader("📊 4. สรุปผลและเปรียบเทียบแผน")
            totals = {k: 0.0 for k in p_names}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    for p_n in p_names:
                        if p_n in m_n: totals[p_n] += m_v

            m_cols = st.columns(len(p_names))
            for i, name in enumerate(p_names):
                m_cols[i].metric(label=name, value=f"{totals[name]:,.2f}")

            comp_rows = []
            for name in p_names:
                p_val = planned_values[name]
                a_val = totals[name]
                diff = p_val - a_val
                comp_rows.append({
                    "รายการวัสดุ": name,
                    "แผนงาน (Planned)": p_val,
                    "คำนวณจริง (Actual)": a_val,
                    "ส่วนต่าง (+เหลือ/-เกิน)": diff,
                    "สถานะ": "✅ ปกติ" if diff >= 0 else "⚠️ เกินแผน"
                })
            st.table(pd.DataFrame(comp_rows))

            # 5. Export
            st.subheader("📤 5. ส่งออกและเอกสารอ้างอิง")
            col_ex1, col_ex2 = st.columns(2)
            
            df_detailed = pd.DataFrame([
                {**{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน']}, **i['รายละเอียด']} 
                for i in st.session_state.calc_history
            ]).fillna(0)
            
            output_header = f"Project: {project_work_name}\nOffice: {office_name}\nDate: {calc_date}\n\n"
            csv_content = df_detailed.to_csv(index=False)
            full_output = output_header + "--- รายละเอียด ---\n" + csv_content
            
            col_ex1.download_button(
                label="📥 ดาวน์โหลดไฟล์สรุป (CSV)",
                data=full_output.encode('utf-8-sig'),
                file_name=f'Report_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )
            
            if col_ex2.button("🚫 ล้างข้อมูลทั้งหมด", use_container_width=True):
                st.session_state.calc_history = []
                st.rerun()

            # --- แก้ไขจุดที่มี SyntaxError (st.link_button) ---
            st.markdown("---")
            label_text = "🔗 หลักเกณฑ์ราคากลางชลประทาน (ฉบับที่ 5) และ ว1288 (ดอกเบี้ย 6%)"
            st.link_button(label_text, "https://drive.google.com/file/d/1tCep-NffAYB2QtDaPo7b2RwTuy7O_aw8/view", use_container_width=True)

    else:
        st.error("❌ ไม่พบไฟล์ CSV กรุณาตรวจสอบการอัปโหลดไฟล์")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
