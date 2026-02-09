import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: ปรับพื้นหลังขาว กล่องเทาขอบดำ และตัวหนังสือเด่นชัด
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { 
        font-family: 'Sarabun', sans-serif; 
        background-color: #ffffff !important; 
    }
    
    /* จัดระดับ Alignment ของ Input และ ปุ่ม */
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

    /* ตกแต่งตารางและส่วนสรุป */
    .stTable { background-color: #ffffff; border: 1px solid #000; }
    .stExpander { border: 2px solid #000000 !important; background-color: #ffffff !important; border-radius: 10px !important; }
    [data-testid="stMetricValue"] { font-size: 32px !important; font-weight: bold !important; color: #000 !important; }
    </style>
""", unsafe_allow_html=True)

# ฟังก์ชันโหลดข้อมูล (แก้ไข Syntax ที่บรรทัด 51 เดิม)
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

# ฟังก์ชันสำหรับสร้างไฟล์ Excel
def to_excel(df_detailed, df_summary):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_detailed.to_excel(writer, sheet_name='รายการงานย่อย', index=False)
        df_summary.to_excel(writer, sheet_name='สรุปภาพรวม', index=False)
    return output.getvalue()

# เริ่มต้น Session State
if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

# --- ส่วนการแสดงผลหลัก ---
st.markdown("<h1>🏗️ การคำนวณอัตราราคางานคอนกรีตและหิน</h1>", unsafe_allow_html=True)

try:
    df = load_data()
    if df is not None:
        # ช่องกรอกข้อมูลโครงการ
        col_p1, col_p2 = st.columns(2)
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", placeholder="ระบุหน่วยงาน...")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", placeholder="ระบุชื่องาน...")
        
        st.caption(f"วันที่บันทึกระบบ: {datetime.now().strftime('%d/%m/%Y')}")
        
        p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก", "เหล็กเส้นเสริมคอนกรีต", "ลวดผูกเหล็กเสริม"]

        # 1. ส่วนตั้งค่าแผน
        st.markdown("### 📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 ระบุปริมาณวัสดุที่ได้รับอนุมัติ", expanded=True):
            col_plan = st.columns(4) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i % 4].number_input(f"{name}", min_value=0.0, value=None, placeholder="0.0", key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # 2. ส่วนเพิ่มรายการงาน
        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        col_in1, col_in2, col_in3 = st.columns([2.5, 1, 1]) 
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกประเภทงาน:", work_list)
        q_val = col_in2.number_input("ปริมาณงานที่ทำจริง:", min_value=0.0, value=None, placeholder="จำนวน...", key="work_qty")
        
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
                        except:
                            continue
                st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": q_val, "รายละเอียด": temp_details})
                st.rerun()

        # 3. สรุปผลและรายการสะสม
        if st.session_state.calc_history:
            st.markdown("### 📋 3. รายการที่บันทึกไว้")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']:,} หน่วย)"):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.3f}**")
                    if st.button(f"🗑️ ลบรายการ", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            st.divider()
            st.markdown("### 📊 4. สรุปยอดรวมวัสดุสะสม")
            totals = {k: sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history) for k in p_names}
            
            m_cols = st.columns(4) 
            for i, name in enumerate(p_names):
                m_cols[i % 4].metric(label=name, value=f"{totals[name]:,.3f}")

            df_comp = pd.DataFrame([{
                "รายการวัสดุ": name,
                "แผนงาน (Planned)": planned_values[name],
                "คำนวณจริง (Actual)": totals[name],
                "ส่วนต่าง (+เหลือ/-เกิน)": planned_values[name] - totals[name],
                "สถานะ": "✅ น้อยกว่าหรือเท่ากลับแผน" if (planned_values[name] - totals[name]) >= 0 else "⚠️ เกินกว่าแผน"
            } for name in p_names])
            st.table(df_comp)

            # 4. ปุ่มดาวน์โหลด Excel
            st.markdown("### 📤 5. ส่งออกรายงาน")
            df_detailed = pd.DataFrame([{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history])
            excel_data = to_excel(df_detailed, df_comp)
            
            c_ex1, c_ex2 = st.columns(2)
            c_ex1.download_button(
                label="📥 ดาวน์โหลดไฟล์ Excel (.xlsx)",
                data=excel_data,
                file_name=f'Report_{datetime.now().strftime("%Y%m%d")}.xlsx',
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            if c_ex2.button("🚫 ล้างข้อมูลทั้งหมด", use_container_width=True):
                st.session_state.calc_history = []
                st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ข้อมูล CSV ในระบบ")

except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
