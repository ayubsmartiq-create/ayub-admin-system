import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="نظام أيوب الإداري", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    [data-testid="stMetric"] { background-color: #1e1e1e; border: 1px solid #FFD700; border-radius: 10px; padding: 10px; }
    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

def load_data(file_name, columns):
    if not os.path.exists(file_name):
        pd.DataFrame(columns=columns).to_csv(file_name, index=False, encoding='utf-8-sig')
    return pd.read_csv(file_name)

st.title("🛡️ نظام أيوب الذكي")

menu = st.sidebar.radio("القائمة:", ["📊 لوحة التحكم", "💵 الحسابات اليومية", "👥 إدارة الموظفين"])

if menu == "📊 لوحة التحكم":
    st.header("ملخص الحالة المالية")
    finance_df = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
    وارد = finance_df[finance_df['النوع'] == 'وارد']['المبلغ'].sum()
    مصروف = finance_df[finance_df['النوع'] == 'مصروف']['المبلغ'].sum()
    صافي = وارد - مصروف
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوارد", f"{وارد:,}")
    c2.metric("إجمالي المصاريف", f"{مصروف:,}")
    c3.metric("صافي الربح", f"{صافي:,}")
    
    st.write("---")
    st.subheader("إدارة العمليات (حذف أو عرض)")
    if not finance_df.empty:
        for index, row in finance_df.iterrows():
            col_text, col_btn = st.columns([4, 1])
            col_text.write(f"📌 {row['التاريخ']} | {row['التفاصيل']} | {row['النوع']} | {row['المبلغ']:,} دينار")
            if col_btn.button("حذف", key=f"fin_{index}"):
                finance_df = finance_df.drop(index)
                finance_df.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                st.rerun()
    else:
        st.info("لا توجد عمليات مسجلة حالياً")

elif menu == "💵 الحسابات اليومية":
    st.header("تسجيل عملية مالية")
    with st.form("fin_form"):
        desc = st.text_input("وصف العملية")
        amount = st.number_input("المبلغ", min_value=0)
        t_type = st.selectbox("النوع", ["وارد", "مصروف"])
        submit = st.form_submit_button("حفظ")
        if submit and desc:
            finance_df = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
            new_row = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), "التفاصيل": desc, "النوع": t_type, "المبلغ": amount}
            finance_df = pd.concat([finance_df, pd.DataFrame([new_row])], ignore_index=True)
            finance_df.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
            st.success("تم الحفظ")
            st.rerun()

elif menu == "👥 إدارة الموظفين":
    st.header("سجل الموظفين")
    employees_df = load_data("data_employees.csv", ["الاسم", "المنصب", "الراتب"])
    
    if not employees_df.empty:
        for index, row in employees_df.iterrows():
            col_e_text, col_e_btn = st.columns([4, 1])
            col_e_text.write(f"👤 {row['الاسم']} - {row['المنصب']} ({row['الراتب']})")
            if col_e_btn.button("حذف", key=f"emp_{index}"):
                employees_df = employees_df.drop(index)
                employees_df.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
                st.rerun()
    
    st.write("---")
    with st.form("emp_form"):
        name = st.text_input("اسم الموظف")
        job = st.text_input("المنصب")
        salary = st.text_input("الراتب")
        if st.form_submit_button("إضافة"):
            new_emp = {"الاسم": name, "المنصب": job, "الراتب": salary}
            employees_df = pd.concat([employees_df, pd.DataFrame([new_emp])], ignore_index=True)
            employees_df.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
            st.rerun()
