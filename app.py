import streamlit as st
import pandas as pd
import datetime
import os

# --- إعدادات الصفحة ---
st.set_page_config(page_title="نظام أيوب الإداري", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    .stMetric { background-color: #1e1e1e; border: 1px solid #FFD700; border-radius: 10px; padding: 15px; }
    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف تنظيف وإدارة البيانات ---
# هذا الجزء هو المسؤول عن مسح الملفات القديمة إذا كانت تسبب مشاكل
def safe_load(file_name, columns):
    try:
        if os.path.exists(file_name):
            df = pd.read_csv(file_name)
            # إذا كانت الأعمدة مختلفة عن المطلوب، نحذف الملف ونبدأ من جديد
            if list(df.columns) != columns:
                os.remove(file_name)
                df = pd.DataFrame(columns=columns)
        else:
            df = pd.DataFrame(columns=columns)
    except:
        df = pd.DataFrame(columns=columns)
    
    if df.empty:
        df = pd.DataFrame(columns=columns)
    return df

# تعريف الأعمدة بدقة
FIN_COLS = ["التاريخ", "التفاصيل", "النوع", "المبلغ"]
EMP_COLS = ["الاسم الثلاثي", "المنصب", "تاريخ المباشرة", "الراتب", "الخصومات"]

# تحميل البيانات النظيفة
df_fin = safe_load("data_finance.csv", FIN_COLS)
df_emp = safe_load("data_employees.csv", EMP_COLS)

# --- القائمة الجانبية ---
st.sidebar.title("🛡️ نظام أيوب الذكي")
menu = st.sidebar.radio("القائمة:", ["📊 لوحة التحكم", "💵 الحسابات اليومية", "👥 إدارة الموظفين"])

# زر التصفير الجذري (يمسح كل شيء إذا حدث خطأ)
if st.sidebar.button("🚨 تصفير النظام بالكامل"):
    if os.path.exists("data_finance.csv"): os.remove("data_finance.csv")
    if os.path.exists("data_employees.csv"): os.remove("data_employees.csv")
    st.rerun()

# --- 1. لوحة التحكم ---
if menu == "📊 لوحة التحكم":
    st.header("📊 ملخص الحالة المالية")
    
    # حسابات دقيقة
    if not df_fin.empty:
        df_fin['المبلغ'] = pd.to_numeric(df_fin['المبلغ'], errors='coerce').fillna(0)
        وارد = df_fin[df_fin['النوع'] == 'وارد']['المبلغ'].sum()
        مصروف = df_fin[df_fin['النوع'] == 'مصروف']['المبلغ'].sum()
        صافي = وارد - مصروف
    else:
        وارد, مصروف, صافي = 0, 0, 0

    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوارد", f"{وارد:,} د.ع")
    c2.metric("إجمالي المصاريف", f"{مصروف:,} د.ع")
    c3.metric("صافي الربح", f"{صافي:,} د.ع")
    
    st.write("---")
    st.subheader("📝 سجل العمليات الأخيرة")
    st.dataframe(df_fin.tail(10), use_container_width=True)

# --- 2. الحسابات اليومية ---
elif menu == "💵 الحسابات اليومية":
    st.header("💵 تسجيل حركة مالية")
    with st.form("fin_form", clear_on_submit=True):
        desc = st.text_input("وصف العملية (مثال: مبيعات الصباح)")
        amount = st.number_input("المبلغ بالدينار", min_value=0)
        t_type = st.selectbox("النوع", ["وارد", "مصروف"])
        if st.form_submit_button("حفظ"):
            if desc:
                # تسجيل التاريخ بشكل بسيط وسلس
                now = datetime.datetime.now().strftime("%Y-%m-%d")
                new_row = pd.DataFrame([[now, desc, t_type, amount]], columns=FIN_COLS)
                df_fin = pd.concat([df_fin, new_row], ignore_index=True)
                df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                st.success("تم الحفظ!")
                st.rerun()

# --- 3. إدارة الموظفين ---
elif menu == "👥 إدارة الموظفين":
    st.header("👥 سجل الكادر الوظيفي")
    
    if not df_emp.empty:
        for index, row in df_emp.iterrows():
            with st.container():
                c_inf, c_py, c_dl = st.columns([3, 1, 1])
                c_inf.write(f"👤 **{row['الاسم الثلاثي']}** | {row['المنصب']} | راتب: {int(row['الراتب']):,}")
                
                if c_py.button("صرف راتب", key=f"p_{index}"):
                    safi = int(row['الراتب']) - int(row['الخصومات'])
                    pay_row = pd.DataFrame([[datetime.datetime.now().strftime("%Y-%m-%d"), f"راتب: {row['الاسم الثلاثي']}", "مصروف", safi]], columns=FIN_COLS)
                    df_fin = pd.concat([df_fin, pay_row], ignore_index=True)
                    df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                    st.success("تم الخصم من المالية")
                
                if c_dl.button("حذف", key=f"d_{index}"):
                    df_emp = df_emp.drop(index)
                    df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
                    st.rerun()
                st.write("---")
    
    st.subheader("➕ إضافة موظف جديد")
    with st.form("add_emp"):
        n = st.text_input("الاسم الثلاثي")
        j = st.text_input("المنصب")
        s = st.number_input("الراتب", min_value=0)
        d = st.number_input("الخصومات", min_value=0)
        if st.form_submit_button("إضافة"):
            if n:
                new_e = pd.DataFrame([[n, j, str(datetime.date.today()), s, d]], columns=EMP_COLS)
                df_emp = pd.concat([df_emp, new_e], ignore_index=True)
                df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
                st.rerun()
