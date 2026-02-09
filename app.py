import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: ปรับพื้นหลังขาว และ "จัดตารางให้กึ่งกลาง"
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Sarabun', sans-serif; 
        background-color: #ffffff !important; 
    }
    
    /* จัดระดับ Alignment ของช่องกรอก */
    [data-testid="column"] { display: flex; align-items: flex-end; }

    /* กล่องข้อความ: พื้นสีเทา ขอบดำ */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
    }

    /* --- ส่วนสำคัญ: จัดตัวอักษรในตารางให้กึ่งกลาง --- */
    .stTable { 
        width: 100%; 
        border: 1px solid #000;
    }
    .stTable th {
        text-align: center !important;
        background-color: #f2f2f2 !important;
        font-weight: bold !important;
    }
    .stTable td {
        text-align: center !important;
        vertical-align: middle !important;
    }
    /* -------------------------------------- */

    div.stButton > button {
        width: 100%; height: 3.0rem; border-radius: 8px !important;
        background-color: #007bff; color: white; border: 1px solid #000;
    }
    .stExpander { border: 2px solid #000000 !important; background-color: #ffffff !important; border-radius: 10px !important; }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold !important; color: #000 !important; text-align: center; }
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

def to_excel(df_detailed, df_summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
        df_detailed.to_excel(writer, sheet_name='รายการงานย่อย', index=False)
    return output.getvalue()

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.markdown("<h1>🏗️ ระบบคำนวณวัสดุสะสม</h1>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        col_p1, col_p2 = st.columns(2)
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="ระบุหน่วยงาน...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="ระบุชื่องาน...")
        
        p_names = ["หินใหญ่(ลบ.ม.)", "หินย่อย(ลบ.ม.)", "ทรายหยาบ(ลบ.ม.)", "ปูนซีเมนต์(ถุง)", "หินคลุก(ลบ.ม.)", "เหล็กเส้น(ตัน)", "ลวดผูกเหล็ก(กก.)"]

        st.markdown("### 📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุตามแผนงาน", expanded=True):
            col_plan = st.columns(4) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i % 4].number_input(f"{name}", min_value=0.0, format="%.2f", key=f"p_{i}")
                planned_values[name] = round(val, 2)

        st.divider()

        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        col_in1, col_in2, col_in3 = st.columns([2.5, 1, 1]) 
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        q_val = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.0, format="%.2f", key="work_qty")
        
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True):
            if q_val > 0:
                selected_row = df[df[0] == selected_work].iloc[0]
                m_idx_map = {p_names[0]: 2, p_names[1]: 4, p_names[2]: 6, p_names[3]: 8, p_names[4]: 10, p_names[5]: 12, p_names[6]: 14}
                temp_details = {}
                for m_name, idx in m_idx_map.items():
                    if idx < len(selected_row):
                        try:
                            val_str = str(selected_row[idx]).replace(',', '').strip()
                            if val_str and val_str != "nan":
                                temp_details[m_name] = round(float(val_str) * q_val, 2)
                        except: continue
                st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": round(q_val, 2), "รายละเอียด": temp_details})
                st.rerun()

        if st.session_state.calc_history:
            st.markdown("### 📊 3. สรุปยอดรวมวัสดุสะสม")
            totals = {k: round(sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history), 2) for k in p_names}
            
            # ตารางสรุปแบบจัดกึ่งกลาง
            df_comp = pd.DataFrame([{
                "รายการวัสดุ": name,
                "แผนงาน (Planned)": f"{planned_values[name]:,.2f}",
                "คำนวณจริง (Actual)": f"{totals[name]:,.2f}",
                "ส่วนต่าง (+เหลือ/-เกิน)": f"{(planned_values[name] - totals[name]):,.2f}",
                "สถานะ": "✅ ปกติ" if (planned_values[name] - totals[name]) >= 0 else "⚠️ เกินแผน"
            } for name in p_names])
            
            # แสดงตาราง (CSS จะจัดการให้กึ่งกลางอัตโนมัติ)
            st.table(df_comp)

            # ส่วน Export
            df_detailed_ex = pd.DataFrame([{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history])
            excel_data = to_excel(df_detailed_ex, df_comp)
            
            st.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel (.xlsx)",
                data=excel_data,
                file_name=f'Summary_Report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            if st.button("🚫 ล้างข้อมูลทั้งหมด", use_container_width=True):
                st.session_state.calc_history = []; st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล CSV")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
