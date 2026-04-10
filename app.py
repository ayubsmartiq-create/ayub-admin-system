import streamlit as st
import pandas as pd
import datetime
import os

# --- 1. إعدادات الصفحة وتحسين الموبايل ---
st.set_page_config(page_title="نظام أيوب الإداري", layout="wide")

# تصميم CSS متطور يدعم الموبايل والحاسبة
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Cairo', sans-serif;
        text-align: right;
        direction: rtl;
    }
    
    /* تحسين شكل البطاقات المالية للموبايل */
    [data-testid="stMetric"] {
        background-color: #1e1e1e;
        border: 1px solid #FFD700;
        border-radius: 10px;
        padding: 10px;
        margin-bottom: 10px;
    }

    .stApp { background-color: #121212; }
    h1, h2, h3, p, span, label { color: #FFD700 !important; }

    /* ضبط الجداول لتكون قابلة للتمرير في الموبايل */
    .stTable {
        overflow-x: auto;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. عنوان النظام ---
st.title("🛡️ نظام أيوب الذكي")
st.write("إدارة مالية وإدارية متكاملة")

# --- 3. قاعدة البيانات ---
اسم_الملف = "data_finance.csv"
if not os.path.exists(اسم_الملف):
    df = pd.DataFrame(columns=["التاريخ", "التفاصيل", "النوع", "المبلغ"])
    df.to_csv(اسم_الملف, index=False, encoding='utf-8-sig')

# --- 4. القائمة الجانبية (Sidebar) ---
with st.sidebar:
    st.header("القائمة")
    الخيار = st.radio("انتقل إلى:", ["لوحة التحكم", "إضافة عملية", "سجل الموظفين"])
    st.write("---")
    st.write("مبرمج النظام: أيوب هاني")

# --- 5. الأقسام ---
if الخيار == "لوحة التحكم":
    st.header("📊 ملخص الحالة المالية")
    بيانات = pd.read_csv(اسم_الملف)
    
    الوارد = بيانات[بيانات['النوع'] == 'وارد']['المبلغ'].sum()
    المصروف = بيانات[بيانات['النوع'] == 'مصروف']['المبلغ'].sum()
    الصافي = الوارد - المصروف
    
    # استخدام أعمدة تترتب تلقائياً حسب حجم الشاشة
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1: st.metric("إجمالي الوارد", f"{الوارد:,}")
    with col2: st.metric("إجمالي المصاريف", f"{المصروف:,}")
    with col3: st.metric("صافي الربح", f"{الصافي:,}")
    
    st.write("---")
    st.subheader("📝 آخر العمليات")
    # عرض الجدول بشكل يتناسب مع الموبايل
    st.dataframe(بيانات.tail(10), use_container_width=True)

elif الخيار == "إضافة عملية":
    st.header("➕ تسجيل جديد")
    with st.form("finance_form"):
        التفاصيل = st.text_input("وصف العملية")
        المبلغ = st.number_input("المبلغ (دينار)", min_value=0, step=250)
        النوع = st.selectbox("النوع", ["وارد", "مصروف"])
        إرسال = st.form_submit_button("حفظ العملية")
        
        if إرسال and التفاصيل:
            بيانات = pd.read_csv(اسم_الملف)
            جديد = {"التاريخ": datetime.datetime.now().strftime("%Y-%m-%d"), 
                    "التفاصيل": التفاصيل, "النوع": النوع, "المبلغ": المبلغ}
            بيانات = pd.concat([بيانات, pd.DataFrame([جديد])], ignore_index=True)
            بيانات.to_csv(اسم_الملف, index=False, encoding='utf-8-sig')
            st.success("تم التحديث!")
            st.rerun()

elif الخيار == "سجل الموظفين":
    st.header("👥 إدارة الكادر")
    موظفين = pd.DataFrame({
        "الاسم": ["أيوب هاني", "علي جاسم", "محمد حسن"],
        "المنصب": ["مدير النظام", "محاسب", "مندوب"],
        "الراتب": ["1,500,000", "900,000", "700,000"]
    })
    st.table(موظفين)
