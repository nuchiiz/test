import streamlit as st
import pandas as pd
from datetime import datetime
import io

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro V.2", layout="wide")

# CSS: ปรับแต่ง UI ทั้งหมด
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }
    
    /* ปรับความสูงมาตรฐานให้ Input และ Selectbox */
    div[data-testid="stSelectbox"] > div[data-baseweb="select"] > div,
    div[data-testid="stNumberInput"] input {
        height: 45px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        background-color: #f2f2f2 !important; 
        border: 2px solid #000000 !important; 
        border-radius: 8px !important;
    }

    /* สไตล์ปุ่มทั่วไป */
    div.stButton > button, div.stDownloadButton > button {
        height: 45px !important;
        border-radius: 8px !important;
        background-color: #33691e; 
        color: white; 
        border: 1px solid #000; 
        font-weight: bold;
        transition: 0.3s;
    }

    /* จัดระเบียบปุ่ม "เพิ่มรายการ" (ส่วนที่ 2) */
    .add-btn-container div.stButton > button {
        margin-top: 28px !important; /* ดันลงมาให้ตรงกับช่องที่มี Label */
        width: auto !important;
    }

    /* จัดระเบียบปุ่มตอนท้าย (ส่วนที่ 4) ให้กึ่งกลางและหดตามตัวอักษร */
    .center-btn-group {
        display: flex;
        justify-content: center;
        gap: 15px;
        margin-top: 20px;
    }
    .center-btn-group div.stButton > button, 
    .center-btn-group div.stDownloadButton > button {
        width: auto !important;
        min-width: 200px !important;
        padding: 0 30px !important;
    }

    /* ปุ่มสีฟ้า */
    div.stButton > button[kind="secondary"] {
        background-color: #039be5 !important;
        color: white !important;
    }

    div.stButton > button:hover {
        border-color: #007bff;
        color: #007bff;
        background-color: white;
    }
    
    .stTable { width: 100%; border: 1px solid #000; }
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
        
        p_names = ["หินใหญ่(ลบ.ม.)", "หินย่อย(ลบ.ม.)", "ทรายหยาบ(ลบ.ม.)", "ปูนซีเมนต์(ถุง)", "หินคลุก(ลบ.ม.)", "เหล็กเส้นเสริมคอนกรีต(ตัน)", "ลวดผูกเหล็ก(กก.)"]

        st.markdown("### 📊 1. ปริมาณตามแผนจัดซื้อจัดจ้าง")
        with st.expander("📝 ระบุปริมาณวัสดุตามแผน", expanded=True):
            col_plan = st.columns(4) 
            planned_values = {}
            for i, name in enumerate(p_names):
                val = col_plan[i % 4].number_input(f"{name}", min_value=0.0, value=0.0, format="%.2f", key=f"p_{i}")
                planned_values[name] = val if val is not None else 0.0

        st.divider()

        # --- ส่วนที่ 2: เพิ่มรายการ (ปรับขนาดให้เท่ากันและระนาบเดียวกัน) ---
        st.markdown("### ➕ 2. รายการงานก่อสร้าง")
        work_list = df[0].dropna().unique().tolist()
        
        # ใช้ container ครอบเพื่อให้ CSS ทำงานเฉพาะจุด
        st.markdown('<div class="add-btn-container">', unsafe_allow_html=True)
        col_in1, col_in2, col_in3 = st.columns([2.5, 1, 1]) 
        
        with col_in1:
            selected_work = st.selectbox("เลือกประเภทงาน:", work_list)
        with col_in2:
            q_val_input = st.number_input("ปริมาณงานจริง:", min_value=0.0, value=0.0, format="%.2f", key="work_qty")
            q_val = q_val_input if q_val_input is not None else 0.0
        with col_in3:
            add_btn = st.button("➕ เพิ่มรายการ", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if add_btn and q_val > 0:
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
                        temp_details[m_name] = round(ratio * q_val, 2)
                except: continue
            st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": q_val, "เกณฑ์ต่อหน่วย": unit_ratios, "รายละเอียด": temp_details})
            st.rerun()

        if st.session_state.calc_history:
            st.divider()
            st.markdown("### 📋 3. รายละเอียดการคำนวณ")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']:,} หน่วย)"):
                    calc_table = [{"วัสดุ": m, "รวมที่ต้องใช้": f"{item['รายละเอียด'][m]:,.2f}"} for m in item['เกณฑ์ต่อหน่วย']]
                    st.table(pd.DataFrame(calc_table))
                    if st.button(f"🗑️ ลบรายการ", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            st.divider()
            st.markdown("### 📊 4. สรุปยอดรวมวัสดุสะสม")
            totals = {k: sum(item['รายละเอียด'].get(k, 0.0) for item in st.session_state.calc_history) for k in p_names}
            
            df_comp_data = []
            for name in p_names:
                p_v = planned_values.get(name, 0.0)
                a_v = totals.get(name, 0.0)
                diff = p_v - a_v
                df_comp_data.append({
                    "รายการวัสดุ": name,
                    "แผนงาน": f"{p_v:,.2f}",
                    "ใช้จริง": f"{a_v:,.2f}",
                    "ส่วนต่าง": f"{diff:,.2f}",
                    "สถานะ": "✅ น้อยกว่าหรือเท่ากับแผน" if diff >= 0 else "⚠️ เกินแผน"
                })
            st.table(pd.DataFrame(df_comp_data))

           # --- ส่วนท้าย: ปุ่มดาวน์โหลดและล้างข้อมูล (กึ่งกลางและติดกัน) ---
            st.markdown('<div class="center-btn-container">', unsafe_allow_html=True)
            c_left, c_btn1, c_btn2, c_right = st.columns([1, 1, 1, 1])
            
            with c_btn1:
                df_detailed_ex = pd.DataFrame([{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน'], **i['รายละเอียด']} for i in st.session_state.calc_history])
                excel_data = to_excel(df_detailed_ex, pd.DataFrame(df_comp_data))
                st.download_button(label="📥 ดาวน์โหลดไฟล์ Excel", data=excel_data, file_name=f'Report_{datetime.now().strftime("%Y%m%d")}.xlsx')
            
            with c_btn2:
                if st.button("🚫 ล้างข้อมูลทั้งหมด"):
                    st.session_state.calc_history = []
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.error("❌ ไม่พบไฟล์ CSV")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {str(e)}")
