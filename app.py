import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="نظام أيوب الإداري", layout="wide")

# تصميم محسّن للموبايل والحاسبة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    [data-testid="stMetric"] { background-color: #1e1e1e; border: 1px solid #FFD700; border-radius: 10px; padding: 10px; }
    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

# إدارة ملفات البيانات
def load_data(file_name, columns):
    if not os.path.exists(file_name):
        pd.DataFrame(columns=columns).to_csv(file_name, index=False, encoding='utf-8-sig')
    return pd.read_csv(file_name)

finance_df = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
employees_df = load_data("data_employees.csv", ["الاسم", "المنصب", "الراتب"])

st.title("🛡️ نظام أيوب الذكي للحلول الإدارية")

menu = st.sidebar.radio("القائمة:", ["📊 لوحة التحكم", "💵 الحسابات اليومية", "👥 إدارة الموظفين"])

if menu == "📊 لوحة التحكم":
    st.header("ملخص الحالة المالية")
    وارد = finance_df[finance_df['النوع'] == 'وارد']['المبلغ'].sum()
    مصروف = finance_df[finance_df['النوع'] == 'مصروف']['المبلغ'].sum()
    صافي = وارد - مصروف
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوارد", f"{وارد:,}")
    c2.metric("إجمالي المصاريف", f"{مصروف:,}")
    c3.metric("صافي الربح الحقيقي", f"{صافي:,}")
    st.write("---")
    st.subheader("آخر 5 عمليات مسجلة")
    st.table(finance_df.tail(5))

elif menu == "💵 الحسابات اليومية":
    st.header("تسجيل عملية مالية")
    with st.form("fin_form"):
        desc = st.text_input("وصف العملية (مثلاً: مبيعات، ماء، كهرباء)")
        amount = st.number_input("المبلغ", min_value=0)
        t_type = st.selectbox("النوع", ["وارد", "مصروف"])
        submit = st.form_submit_button("حفظ")
        if submit and desc:
            new_row = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), "التفاصيل": desc, "النوع": t_type, "المبلغ": amount}
            finance_df = pd.concat([finance_df, pd.DataFrame([new_row])], ignore_index=True)
            finance_df.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
            st.success("تم الحفظ بنجاح")
            st.rerun()

elif menu == "👥 إدارة الموظفين":
    st.header("سجل الموظفين")
    # عرض الجدول الحالي
    st.dataframe(employees_df, use_container_width=True)
    
    st.write("---")
    st.subheader("إضافة موظف جديد")
    with st.form("emp_form"):
        name = st.text_input("اسم الموظف")
        job = st.text_input("المنصب")
        salary = st.text_input("الراتب")
        add_emp = st.form_submit_button("إضافة الموظف للسجل")
        if add_emp and name:
            new_emp = {"الاسم": name, "المنصب": job, "الراتب": salary}
            employees_df = pd.concat([employees_df, pd.DataFrame([new_emp])], ignore_index=True)
            employees_df.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
            st.success(f"تمت إضافة {name} بنجاح")
            st.rerun()
