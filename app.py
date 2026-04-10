import streamlit as st
import pandas as pd
import datetime
import os

# إعداد واجهة النظام
st.set_page_config(page_title="نظام أيوب الإداري", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛡️ نظام أيوب للحلول الإدارية والمالية")
st.write("نظام احترافي لإدارة الحسابات والموظفين")

# إدارة قاعدة البيانات
اسم_الملف = "data_finance.csv"
if not os.path.exists(اسم_الملف):
    df = pd.DataFrame(columns=["التاريخ", "التفاصيل", "النوع", "المبلغ"])
    df.to_csv(اسم_الملف, index=False, encoding='utf-8-sig')

# القائمة الجانبية
st.sidebar.title("القائمة الرئيسية")
الخيار = st.sidebar.radio("اختر القسم:", ["لوحة التحكم", "إضافة عملية مالية", "إدارة الموظفين"])

if الخيار == "لوحة التحكم":
    st.header("📊 ملخص الحالة المالية")
    بيانات = pd.read_csv(اسم_الملف)
    الوارد = بيانات[بيانات['النوع'] == 'وارد']['المبلغ'].sum()
    المصروف = بيانات[بيانات['النوع'] == 'مصروف']['المبلغ'].sum()
    الصافي = الوارد - المصروف
    
    ع1, ع2, ع3 = st.columns(3)
    ع1.metric("إجمالي الوارد", f"{الوارد:,} دينار")
    ع2.metric("إجمالي المصاريف", f"{المصروف:,} دينار")
    ع3.metric("صافي الربح", f"{الصافي:,} دينار")
    st.table(بيانات.tail(10))

elif الخيار == "إضافة عملية مالية":
    st.header("➕ تسجيل وارد أو مصروف جديد")
    with st.form("form_finance"):
        التفاصيل = st.text_input("وصف العملية")
        المبلغ = st.number_input("المبلغ", min_value=0)
        النوع = st.selectbox("نوع العملية", ["وارد", "مصروف"])
        إرسال = st.form_submit_button("حفظ")
        if إرسال:
            بيانات = pd.read_csv(اسم_الملف)
            جديد = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), "التفاصيل": التفاصيل, "النوع": النوع, "المبلغ": المبلغ}
            بيانات = pd.concat([بيانات, pd.DataFrame([جديد])], ignore_index=True)
            بيانات.to_csv(اسم_الملف, index=False, encoding='utf-8-sig')
            st.success("تم الحفظ!")

elif الخيار == "إدارة الموظفين":
    st.header("👥 سجل الموظفين")
    موظفين = pd.DataFrame({
        "الاسم": ["أيوب هاني", "موظف 1", "موظف 2"],
        "الراتب": ["1,500,000", "800,000", "700,000"],
        "الحالة": ["مدير", "محاسب", "مندوب"]
    })
    st.table(موظفين)
