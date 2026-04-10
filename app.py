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
    .stButton>button { width: 100%; border-radius: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- وظائف إدارة البيانات ---
def load_data(file_name, columns):
    if not os.path.exists(file_name):
        pd.DataFrame(columns=columns).to_csv(file_name, index=False, encoding='utf-8-sig')
    df = pd.read_csv(file_name)
    # التأكد من وجود كافة الأعمدة المطلوبة لتجنب KeyError
    for col in columns:
        if col not in df.columns:
            df[col] = "" 
    return df

# تحميل البيانات
df_fin = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
df_emp = load_data("data_employees.csv", ["الاسم الثلاثي", "المنصب", "تاريخ المباشرة", "الراتب الأساسي", "الخصومات"])

# --- القائمة الجانبية ---
st.sidebar.title("🛡️ القائمة الرئيسية")
menu = st.sidebar.radio("انتقل إلى:", ["📊 لوحة التحكم", "💵 الحسابات اليومية", "👥 إدارة الموظفين"])

# --- 1. لوحة التحكم ---
if menu == "📊 لوحة التحكم":
    st.header("📊 ملخص الحالة المالية")
    وارد = pd.to_numeric(df_fin[df_fin['النوع'] == 'وارد']['المبلغ']).sum()
    مصروف = pd.to_numeric(df_fin[df_fin['النوع'] == 'مصروف']['المبلغ']).sum()
    صافي = وارد - مصروف
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوارد", f"{وارد:,} د.ع")
    c2.metric("إجمالي المصاريف", f"{مصروف:,} د.ع")
    c3.metric("صافي الربح", f"{صافي:,} د.ع")
    
    st.write("---")
    st.subheader("📝 سجل العمليات الأخيرة")
    st.dataframe(df_fin.tail(10), use_container_width=True)
    
    if st.sidebar.button("⚠️ تصفير كافة الحسابات"):
        pd.DataFrame(columns=["التاريخ", "التفاصيل", "النوع", "المبلغ"]).to_csv("data_finance.csv", index=False)
        st.rerun()

# --- 2. الحسابات اليومية ---
elif menu == "💵 الحسابات اليومية":
    st.header("💵 تسجيل حركة مالية")
    with st.form("fin_form"):
        desc = st.text_input("وصف العملية")
        amount = st.number_input("المبلغ", min_value=0)
        t_type = st.selectbox("النوع", ["وارد", "مصروف"])
        if st.form_submit_button("حفظ"):
            new_row = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), "التفاصيل": desc, "النوع": t_type, "المبلغ": amount}
            df_fin = pd.concat([df_fin, pd.DataFrame([new_row])], ignore_index=True)
            df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
            st.success("تم الحفظ!")
            st.rerun()

# --- 3. إدارة الموظفين ---
elif menu == "👥 إدارة الموظفين":
    st.header("👥 سجل الكادر الوظيفي")
    
    if not df_emp.empty:
        for index, row in df_emp.iterrows():
            col_info, col_pay, col_del = st.columns([3, 1, 1])
            col_info.write(f"👤 **{row['الاسم الثلاثي']}** | {row['المنصب']} | راتب: {row['الراتب الأساسي']:,}")
            
            if col_pay.button("صرف راتب", key=f"pay_{index}"):
                صافي_الراتب = int(row['الراتب الأساسي']) - int(row['الخصومات'] if row['الخصومات'] else 0)
                pay_data = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), 
                            "التفاصيل": f"راتب: {row['الاسم الثلاثي']}", "النوع": "مصروف", "المبلغ": صافي_الراتب}
                df_fin = pd.concat([df_fin, pd.DataFrame([pay_data])], ignore_index=True)
                df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                st.success(f"تم صرف {صافي_الراتب:,} د.ع")
            
            if col_del.button("حذف", key=f"del_{index}"):
                df_emp = df_emp.drop(index)
                df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
                st.rerun()
    
    st.write("---")
    st.subheader("➕ إضافة موظف جديد")
    with st.form("add_emp"):
        name = st.text_input("الاسم الثلاثي")
        job = st.text_input("المنصب")
        salary = st.number_input("الراتب الشهري", min_value=0)
        disc = st.number_input("الخصومات", min_value=0)
        if st.form_submit_button("إضافة"):
            new_emp = {"الاسم الثلاثي": name, "المنصب": job, "تاريخ المباشرة": str(datetime.date.today()), 
                       "الراتب الأساسي": salary, "الخصومات": disc}
            df_emp = pd.concat([df_emp, pd.DataFrame([new_emp])], ignore_index=True)
            df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
            st.rerun()
