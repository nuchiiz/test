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
    
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
    }
    
    ::placeholder { color: #aaaaaa !important; opacity: 1; }

    .stTable { width: 100%; border: 1px solid #000; }
    .stTable th { text-align: center !important; background-color: #f2f2f2 !important; border: 1px solid #000 !important; }
    .stTable td { text-align: center !important; vertical-align: middle !important; border: 1px solid #ddd !important; }

    div.stButton > button {
        width: 100%; height: 3.0rem; border-radius: 8px !important;
        background-color: #007bff; color: white; border: 1px solid #000; font-weight: bold;
    }
    
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
        except:
            continue
    return None

def to_excel(df_detailed, df_summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
        df_detailed.to_excel(writer, sheet_name='รายการงานย่อย', index=False)
    return output.getvalue()

# บรรทัดที่ 72: แก้ไขโครงสร้าง Session State
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.markdown("<h1>🏗️ ตารางคำนวณอัตราราคางานคอนกรีตและหิน</h1>", unsafe_allow_html=True)

st.markdown("""
    <div class="ref-box">
        📖 <b>เอกสารอ้างอิง:</b> 
        <a href="https://drive.google.com/file/d/1ibHbb81wjwqaDa3ab-VsDDwR-qvUx5FM/view" target="_blank" style="text-decoration: none; color: #007bff; font-weight: bold;">
            หลักเกณฑ์การคำนวณราคากลางงานก่อสร้างชลประทาน (ตุลาคม 2560)
        </a>
        <br><small><i>*อ้างอิงตามบัญชีท้ายหลักเกณฑ์ฯ หน้า 217 "ตารางคำนวณอัตราราคางานคอนกรีตและหิน งานก่อสร้างชลประทาน"</i></small>
    </div>
""", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        col_p1, col_p2 = st.columns(2)
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="ระบุหน่วยงาน...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="ระบุชื่องาน...")
        
        p_names = ["หินใหญ่(ลบ.ม.)", "หินย่อย(ลบ.ม.)", "ทรายหยาบ(ลบ.ม.)", "ปูนซีเมนต์(ถุง)", "หินคลุก(ลบ.ม.)", "เหล็กเส้น(ตัน)", "ลวดผูกเหล็ก(กก.)"]

        st.markdown("### 📊 1. ปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุที่ได้รับอนุมัติ (คลิกเพื่อกรอก)", expanded=True):
            col_plan = st.columns(4) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i % 4].number_input(
                    f"{name}", min_value=0.0, value=None, placeholder="0.00", format="%.2f", key=f"p_{i}"
                )
                planned_values[name] = round(val, 2) if val is not None else 0.0

        st.divider()

        st.markdown("### ➕ 2. รายการงานก่อสร้าง (Actual)")
        col_in1, col_in2, col_in3 = st.columns([2.5, 1, 1]) 
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        q_val_input = col_in2.number_input(
            "ปริมาณงานที่ทำจริง:", min_value=0.0, value=None, placeholder="0.00", format="%.2f", key="work_qty"
        )
        q_val = q_val_input if q_val_input is not None else 0.0
        
        if col_in3.button("➕ เพิ่มรายการ", use_container_width=True):
            if q_val > 0:
                selected_row = df[df[0] == selected_work].iloc[0]
                m_idx_map = {p_names[0]: 2, p_names[1]: 4, p_names[2]: 6, p_names[3]: 8, p_names[4]: 10, p_names[5]: 12, p_names[6]: 14}
                temp_details = {}
                unit_ratios = {}
                for m_name, idx in m_idx_map.items():
                    if idx < len(selected_row):
                        try:
                            val_str = str(selected_row[idx]).replace(',', '').strip()
                            if val_str and val_str not in ["nan", "-"]:
                                ratio = float(val_str)
                                unit_ratios[m_name] = ratio
                                temp_details[m_name] = round(ratio * q_val, 2)
                        except:
                            continue
                st.session_state.calc_history.append({
                    "ประเภทงาน": selected_work, "ปริมาณงาน": round(q_val, 2), 
                    "เกณฑ์ต่อหน่วย": unit_ratios, "รายละเอียด": temp_details
                })
                st.rerun()

        if st.session_state.calc_history:
            st.markdown("### 📋 3. รายละเอียดการคำนวณแต่ละรายการ")
            for i, item in enumerate(st.session_state.calc_history):
                ratios = item.get('เกณฑ์ต่อหน่วย', {})
                with st.expander(f"🔹 {item['ประเภทงาน']} (จำนวน {item['ปริมาณงาน']:,} หน่วย)"):
                    if ratios:
                        calc_table = []
                        for m_n in p_names:
                            if m_n in ratios:
                                calc_table.append({
                                    "รายการวัสดุ": m_n,
                                    "เกณฑ์ต่อหน่วย (A)": f"{ratios[m_n]:,.3f}",
                                    "ปริมาณงานจริง (B)": f"{item['ปริมาณงาน']:,.2f}",
                                    "รวมวัสดุที่ต้องใช้ (A x B)": f"{item['รายละเอียด'].get(m_n, 0):,.2f}"
                                })
                        st.table(pd.DataFrame(calc_table))
                    
                    if st.button(f"🗑️ ลบรายการ", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            st.divider()
            
            st.markdown("### 📊 4. สรุปยอดรวมวัสดุสะสมเปรียบเทียบแผนงาน")
            totals = {k: round(sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history), 2) for k in p_names}
            
            df_comp = pd.DataFrame([{
                "รายการวัสดุ": name,
                "แผนงาน (Planned)": f"{planned_values[name]:,.2f}",
                "คำนวณจริง (Actual)": f"{totals[name]:,.2f}",
                "ส่วนต่าง (+เหลือ/-เกิน)": f"{(planned_values[name] - totals[name]):,.2f}",
                "สถานะ": "✅ ปกติ" if (planned_values[name] - totals[name]) >= 0 else "⚠️ เกินแผน"
            } for name in p_names])
            st.table(df_comp)

            col_dl1, col_dl2 = st.columns(2)
            df_detailed_ex = pd.DataFrame([{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history])
            excel_data = to_excel(df_detailed_ex, df_comp)
            
            col_dl1.download_button(label="📥 ดาวน์โหลดไฟล์ Excel", data=excel_data, file_name=f'Report_{datetime.now().strftime("%Y%m%d")}.xlsx', use_container_width=True)
            if col_dl2.button("🚫 ล้างข้อมูลทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ CSV")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
