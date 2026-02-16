import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: ตกแต่ง UI และปรับขนาดปุ่ม
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
    }

    div.stButton > button {
        width: 100%; height: 3.0rem; border-radius: 8px !important;
        background-color: #007bff; color: white; border: 1px solid #000; font-weight: bold;
    }
    
    div.stButton > button[kind="secondary"] {
        background-color: #dc3545; color: white; border: 1px solid #000;
    }

    .ref-box {
        background-color: #e9ecef; padding: 15px; border-radius: 8px; 
        border-left: 6px solid #007bff; margin-bottom: 25px;
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

def to_excel(df_detailed, df_summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
        df_detailed.to_excel(writer, sheet_name='รายการงานย่อย', index=False)
    return output.getvalue()

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.markdown("<h1>🏗️ ตารางคำนวณอัตราราคางานคอนกรีตและหิน</h1>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        col_p1, col_p2 = st.columns(2)
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="ระบุหน่วยงาน...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="ระบุชื่องาน...")
        
        p_names = ["หินใหญ่(ลบ.ม.)", "หินย่อย(ลบ.ม.)", "ทรายหยาบ(ลบ.ม.)", "ปูนซีเมนต์(ถุง)", "หินคลุก(ลบ.ม.)", "เหล็กเส้นเสริมคอนกรีต(ตัน)", "ลวดผูกเหล็ก(กก.)"]

        st.markdown("### 📊 1. ปริมาณตามแผนจัดซื้อจัดจ้าง")
        with st.expander("📝 ระบุปริมาณวัสดุที่ได้รับอนุมัติ", expanded=True):
            col_plan = st.columns(4) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i % 4].number_input(f"{name}", min_value=0.0, value=0.0, format="%.2f", key=f"p_{i}")
                # ป้องกัน Error โดยใช้ 'or 0.0' เผื่อค่าหลุดเป็น None
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        col_in1, col_in2, col_in3 = st.columns([2.5, 1, 1]) 
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        q_val_input = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.0, value=0.0, format="%.2f", key="work_qty")
        q_val = q_val_input if q_val_input is not None else 0.0
        
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True):
            if q_val > 0:
                selected_row = df[df[0] == selected_work].iloc[0]
                m_idx_map = {p_names[0]: 2, p_names[1]: 4, p_names[2]: 6, p_names[3]: 8, p_names[4]: 10, p_names[5]: 12, p_names[6]: 14}
                temp_details = {}
                unit_ratios = {}
                for m_name, idx in m_idx_map.items():
                    try:
                        val_str = str(selected_row[idx]).replace(',', '').strip()
                        if val_str and val_str not in ["nan", "-"]:
                            ratio = float(val_str)
                            unit_ratios[m_name] = ratio
                            temp_details[m_name] = ratio * q_val
                    except: continue
                st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": q_val, "เกณฑ์ต่อหน่วย": unit_ratios, "รายละเอียด": temp_details})
                st.rerun()

        if st.session_state.calc_history:
            st.markdown("### 📋 3. รายละเอียดการคำนวณ")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} (จำนวน {item['ปริมาณงาน']:,} หน่วย)"):
                    calc_table = [{"รายการวัสดุ": m, "เกณฑ์ต่อหน่วย (A)": f"{item['เกณฑ์ต่อหน่วย'][m]:,.3f}", "ปริมาณงานจริง (B)": f"{item['ปริมาณงาน']:,.2f}", "รวมวัสดุที่ต้องใช้": f"{item['รายละเอียด'][m]:,.2f}"} for m in item['เกณฑ์ต่อหน่วย']]
                    st.table(pd.DataFrame(calc_table))
                    if st.button(f"🗑️ ลบรายการ", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            st.divider()
            st.markdown("### 📊 4. สรุปยอดรวมวัสดุสะสม")
            totals = {k: sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history) for k in p_names}
            
            df_comp_data = []
            for name in p_names:
                # แก้ไขจุดเสี่ยง Error: ลบค่า None ด้วยการใช้ or 0.0
                plan_val = planned_values.get(name) if planned_values.get(name) is not None else 0.0
                actual_val = totals.get(name, 0.0)
                diff = plan_val - actual_val  # จะไม่เกิด Error แล้วเพราะทั้งคู่เป็น float
                
                df_comp_data.append({
                    "รายการวัสดุ": name,
                    "แผนงาน (Planned)": f"{plan_val:,.2f}",
                    "คำนวณจริง (Actual)": f"{actual_val:,.2f}",
                    "ส่วนต่าง (+เหลือ/-เกิน)": f"{diff:,.2f}",
                    "สถานะ": "✅ ปกติ" if diff >= 0 else "⚠️ เกินกว่าแผน"
                })
            
            st.table(pd.DataFrame(df_comp_data))

            col_dl1, col_dl2 = st.columns(2)
            with col_dl1:
                df_detailed_ex = pd.DataFrame([{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history])
                excel_data = to_excel(df_detailed_ex, pd.DataFrame(df_comp_data))
                st.download_button(label="📥 ดาวน์โหลดไฟล์ Excel", data=excel_data, file_name=f'Report_{datetime.now().strftime("%Y%m%d")}.xlsx', use_container_width=True)
            with col_dl2:
                if st.button("🚫 ล้างข้อมูลทั้งหมด", use_container_width=True):
                    st.session_state.calc_history = []
                    st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ CSV")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
