import streamlit as st
import pandas as pd
from datetime import datetime

# 1. ตั้งค่าหน้าจอ
st.set_page_config(page_title="ระบบควบคุมวัสดุ Pro", layout="wide")

# ปรับปรุง CSS ให้ High Contrast และอ่านง่ายที่สุด
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Sarabun:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Sarabun', sans-serif; }

    /* ส่วนตั้งค่าตามแผน (Planned) - ปรับสีพื้นหลังให้ข้อความเด่น */
    .stExpander {
        border: 2px solid #000000 !important;
        background-color: #f8f9fa !important;
        border-radius: 10px !important;
    }
    
    /* หัวข้อภายใน Expander ให้ดำเข้มอ่านง่าย */
    .stExpander label {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }

    /* ตกแต่ง Metric สรุปยอดรวม (High Contrast) */
    [data-testid="stMetricValue"] { font-size: 36px !important; font-weight: 800 !important; color: #000 !important; }
    [data-testid="stMetricLabel"] { font-size: 18px !important; font-weight: bold !important; color: #333 !important; }
    
    /* สีพื้นหลัง Metric แยกตามวัสดุ */
    div[data-testid="stMetric"]:nth-child(1) { background-color: #D1D5DB; border: 2px solid #333; } 
    div[data-testid="stMetric"]:nth-child(2) { background-color: #9CA3AF; border: 2px solid #333; } 
    div[data-testid="stMetric"]:nth-child(3) { background-color: #FDE68A; border: 2px solid #F59E0B; } 
    div[data-testid="stMetric"]:nth-child(4) { background-color: #A7F3D0; border: 2px solid #10B981; } 
    div[data-testid="stMetric"]:nth-child(5) { background-color: #BFDBFE; border: 2px solid #3B82F6; }

    /* ปรับช่อง Input ให้ใหญ่ชัดเจน */
    .stTextInput input, .stNumberInput input {
        font-size: 20px !important;
        font-weight: bold !important;
        border: 2px solid #000 !important;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    file_name = "เทสตาราง.csv"
    for enc in ['cp874', 'tis-620', 'utf-8-sig']:
        try:
            df = pd.read_csv(file_name, skiprows=2, header=None, encoding=enc, on_bad_lines='skip')
            return df
        except: continue
    return None

if 'calc_history' not in st.session_state:
    st.session_state.calc_history = []

st.title("🏗️ ตารางคำนวณอัตรางานคอนกรีตและหินต่าง ๆ ")

try:
    df = load_data()
    if df is not None:
        # --- ปรับเปลี่ยนชื่อช่องตามคำขอ ---
        col_p1, col_p2 = st.columns([1, 1])
        office_name = col_p1.text_input("🏢 สำนัก/โครงการ:", value="ระบุชื่อสำนักหรือโครงการ")
        project_work_name = col_p2.text_input("📄 ชื่องานโครงการ:", value="ระบุชื่องาน")
        
        calc_date = datetime.now().strftime("%d/%m/%Y")
        st.caption(f"วันที่บันทึกระบบ: {calc_date}")
            
        # ส่วนตั้งค่าแผนงาน
        st.subheader("📊 1. ตั้งค่าปริมาณตามแผน (Planned)")
        with st.expander("📝 คลิกเพื่อกรอกปริมาณวัสดุที่ได้รับอนุมัติ (ข้อความเด่นชัด)", expanded=True):
            st.markdown("**กรุณาระบุปริมาณวัสดุตามงบประมาณเพื่อเปรียบเทียบ**")
            col_plan = st.columns(5)
            p_names = ["หินใหญ่", "หินย่อย", "ทรายหยาบ", "ปูนซีเมนต์", "หินคลุก"]
            planned_values = {}
            for i, name in enumerate(p_names):
                planned_values[name] = col_plan[i].number_input(f"{name}", min_value=0.0, key=f"p_{i}")

        st.divider()

        # ส่วนเพิ่มรายการงาน
        st.subheader("➕ 2. เพิ่มรายการงานที่ทำจริง")
        col_in1, col_in2, col_in3 = st.columns([2, 1, 1])
        work_list = df[0].dropna().unique().tolist()
        selected_work = col_in1.selectbox("เลือกงานก่อสร้าง:", work_list)
        quantity = col_in2.number_input("ปริมาณงานที่ทำ:", min_value=0.1, value=1.0)
        
        if col_in3.button("➕ เพิ่มเข้าโครงการ"):
            selected_row = df[df[0] == selected_work].iloc[0]
            m_map = {"หินใหญ่": 2, "หินย่อย": 4, "ทรายหยาบ": 6, "ปูนซีเมนต์": 8, "หินคลุก": 10}
            temp_details = {}
            for m_name, idx in m_map.items():
                try:
                    if idx < len(selected_row):
                        rate_val = float(selected_row[idx])
                        if rate_val > 0: temp_details[m_name] = rate_val * quantity
                except: continue
            st.session_state.calc_history.append({"ประเภทงาน": selected_work, "ปริมาณงาน": quantity, "รายละเอียด": temp_details})
            st.rerun()

        if st.session_state.calc_history:
            st.subheader("📋 3. รายการบันทึกสะสม")
            for i, item in enumerate(st.session_state.calc_history):
                with st.expander(f"🔹 {item['ประเภทงาน']} ({item['ปริมาณงาน']} หน่วย)", expanded=False):
                    for m_n, m_v in item['รายละเอียด'].items():
                        st.write(f"- {m_n}: **{m_v:,.2f}**")
                    if st.button(f"🗑️ ลบรายการนี้", key=f"del_{i}"):
                        st.session_state.calc_history.pop(i)
                        st.rerun()

            # ส่วนสรุปและเปรียบเทียบ
            st.divider()
            st.subheader("📊 4. สรุปผลและเปรียบเทียบแผน")
            
            totals = {k: 0.0 for k in p_names}
            for item in st.session_state.calc_history:
                for m_n, m_v in item['รายละเอียด'].items():
                    for p_n in p_names:
                        if p_n in m_n: totals[p_n] += m_v

            # Metric สรุปยอด
            m_cols = st.columns(len(p_names))
            for i, name in enumerate(p_names):
                m_cols[i].metric(label=name, value=f"{totals[name]:,.2f}")

            # ตารางเปรียบเทียบ
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
                    "สถานะ": "✅ น้อยกว่า/เท่ากับแผน" if diff >= 0 else "⚠️ เกินแผน"
                })
            st.table(pd.DataFrame(comp_rows))

            # --- ส่วน EXPORT ข้อมูล ---
            st.subheader("📤 5. ส่งออกรายงาน")
            
            df_detailed = pd.DataFrame([
                {**{"งาน": i['ประเภทงาน'], "จำนวน": i['ปริมาณงาน']}, **i['รายละเอียด']} 
                for i in st.session_state.calc_history
            ]).fillna(0)
            
            df_comp = pd.DataFrame(comp_rows)
            
            # ปรับหัวรายงานในไฟล์ Export
            output_text = f"สำนัก/โครงการ: {office_name}\nชื่องานโครงการ: {project_work_name}\nวันที่บันทึก: {calc_date}\n\n"
            output_text += "--- รายละเอียดงานย่อย ---\n" + df_detailed.to_csv(index=False)
            output_text += "\n--- สรุปยอดรวมและแผนงาน ---\n" + df_comp.to_csv(index=False)
            
            col_ex1, col_ex2 = st.columns(2)
            col_ex1.download_button(
                label="📥 ดาวน์โหลดไฟล์สรุปทั้งหมด",
                data=output_text.encode('utf-8-sig'),
                file_name=f'Report_{project_work_name}.csv',
                mime='text/csv',
                use_container_width=True
            )
            if col_ex2.button("🚫 ล้างข้อมูลทั้งหมด"):
                st.session_state.calc_history = []
                st.rerun()
    else:
        st.error("❌ ไม่พบไฟล์ เทสตาราง.csv")
except Exception as e:
    st.error(f"⚠️ เกิดข้อผิดพลาด: {e}")
