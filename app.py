import streamlit as st
import pandas as pd
import datetime
import os

st.set_page_config(page_title="نظام أيوب الإداري المتكامل", layout="wide")

# تصميم احترافي
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Cairo', sans-serif; text-align: right; direction: rtl; }
    [data-testid="stMetric"] { background-color: #1e1e1e; border: 1px solid #FFD700; border-radius: 10px; padding: 10px; }
    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }
    .stButton>button { width: 100%; border-radius: 5px; background-color: #FFD700; color: black; }
    </style>
    """, unsafe_allow_html=True)

def load_data(file_name, columns):
    if not os.path.exists(file_name):
        pd.DataFrame(columns=columns).to_csv(file_name, index=False, encoding='utf-8-sig')
    return pd.read_csv(file_name)

# القائمة الجانبية
menu = st.sidebar.radio("انتقل إلى:", ["📊 لوحة التحكم العامة", "💵 السجل المالي", "👥 إدارة شؤون الموظفين"])

# --- قسم الحسابات ---
if menu == "📊 لوحة التحكم العامة":
    st.header("📈 ملخص الأداء المالي")
    df_fin = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
    وارد = df_fin[df_fin['النوع'] == 'وارد']['المبلغ'].sum()
    مصروف = df_fin[df_fin['النوع'] == 'مصروف']['المبلغ'].sum()
    صافي = وارد - مصروف
    
    c1, c2, c3 = st.columns(3)
    c1.metric("إجمالي الوارد", f"{وارد:,} د.ع")
    c2.metric("إجمالي المصاريف", f"{مصروف:,} د.ع")
    c3.metric("الربح الصافي", f"{صافي:,} د.ع")
    
    st.write("---")
    st.subheader("📋 آخر التحركات المالية")
    st.dataframe(df_fin.tail(10), use_container_width=True)

elif menu == "💵 السجل المالي":
    st.header("💰 تسجيل حركة مالية")
    df_fin = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])
    with st.form("fin_form"):
        desc = st.text_input("وصف العملية (مبيعات، إيجار، قرطاسية...)")
        amount = st.number_input("المبلغ", min_value=0)
        t_type = st.selectbox("النوع", ["وارد", "مصروف"])
        if st.form_submit_button("حفظ العملية"):
            new_row = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "التفاصيل": desc, "النوع": t_type, "المبلغ": amount}
            df_fin = pd.concat([df_fin, pd.DataFrame([new_row])], ignore_index=True)
            df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
            st.success("تم التسجيل بنجاح")
            st.rerun()

# --- قسم الموظفين المتطور ---
elif menu == "👥 إدارة شؤون الموظفين":
    st.header("📋 سجل الكادر الوظيفي")
    df_emp = load_data("data_employees.csv", ["الاسم الثلاثي", "المنصب", "تاريخ المباشرة", "الراتب الأساسي", "الخصومات"])
    df_fin = load_data("data_finance.csv", ["التاريخ", "التفاصيل", "النوع", "المبلغ"])

    if not df_emp.empty:
        for index, row in df_emp.iterrows():
            with st.expander(f"👤 {row['الاسم الثلاثي']} - {row['المنصب']}"):
                col1, col2 = st.columns(2)
                col1.write(f"📅 تاريخ المباشرة: {row['تاريخ المباشرة']}")
                col1.write(f"💰 الراتب: {row['الراتب الأساسي']:,} د.ع")
                col2.write(f"📉 الخصومات الحالية: {row['الخصومات']:,} د.ع")
                
                # عملية صرف الراتب تلقائياً
                if st.button(f"صرف راتب {row['الاسم الثلاثي']}", key=f"pay_{index}"):
                    صافي_الراتب = row['الراتب الأساسي'] - row['الخصومات']
                    # إضافة العملية للمالية كمصروف
                    pay_row = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), 
                               "التفاصيل": f"راتب الموظف: {row['الاسم الثلاثي']}", 
                               "النوع": "مصروف", "المبلغ": صافي_الراتب}
                    df_fin = pd.concat([df_fin, pd.DataFrame([pay_row])], ignore_index=True)
                    df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                    st.success(f"تم خصم {صافي_الراتب:,} من الميزانية بنجاح")
                
                if st.button("حذف الموظف نهائياً", key=f"del_{index}"):
                    df_emp = df_emp.drop(index)
                    df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
                    st.rerun()

    st.write("---")
    st.subheader("➕ إضافة موظف جديد")
    with st.form("add_emp_form"):
        name = st.text_input("الاسم الثلاثي")
        job = st.text_input("المنصب")
        start_date = st.date_input("تاريخ المباشرة")
        salary = st.number_input("الراتب الأساسي", min_value=0)
        discount = st.number_input("الخصومات (إن وجدت)", min_value=0)
        if st.form_submit_button("إضافة الموظف"):
            new_emp = {"الاسم الثلاثي": name, "المنصب": job, "تاريخ المباشرة": str(start_date), "الراتب الأساسي": salary, "الخصومات": discount}
            df_emp = pd.concat([df_emp, pd.DataFrame([new_emp])], ignore_index=True)
            df_emp.to_csv("data_employees.csv", index=False, encoding='utf-8-sig')
            st.success(f"تمت إضافة الموظف {name}")
            st.rerun()
