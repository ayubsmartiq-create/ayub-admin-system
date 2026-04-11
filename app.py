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
# --- كود التصحيح الملحق (أضفه في النهاية) ---
st.write("---")
st.subheader("🛠️ أدوات التحكم المتقدمة")

with st.expander("إدارة سجل العمليات (حذف وإصلاح)"):
    # إصلاح مشكلة التاريخ والربح برمجياً في الذاكرة
    df_fin['المبلغ'] = pd.to_numeric(df_fin['المبلغ'], errors='coerce').fillna(0)
    
    if not df_fin.empty:
        st.write("اختر العملية التي تريد حذفها:")
        for index, row in df_fin.iterrows():
            col_rec, col_del = st.columns([4, 1])
            # عرض التاريخ بشكل صحيح حتى لو كان مسجلاً خطأ
            display_date = row['التاريخ'] if row['التاريخ'] != "0" else datetime.date.today()
            col_rec.write(f"📌 {display_date} | {row['التفاصيل']} | {int(row['المبلغ']):,}")
            
            if col_del.button("❌ حذف", key=f"fix_del_{index}"):
                df_fin = df_fin.drop(index)
                df_fin.to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                st.success("تم الحذف بنجاح!")
                st.rerun()
    else:
        st.info("السجل فارغ حالياً.")

with st.expander("📝 ملاحظة المبرمج"):
    st.info("يا أيوب، مشكلة ظهور التاريخ 0 كانت بسبب بيانات قديمة. الكود أعلاه سيسمح لك بحذف تلك العمليات 'الخربة' لكي تعود الحسابات صحيحة وتظهر في لوحة التحكم.")
# --- كود إدارة المخازن الكبيرة (أضفه في نهاية الملف تماماً) ---
st.write("---")
st.header("📦 إدارة المخازن والمنتجات (نظام البحث السريع)")

# وظيفة تحميل المخزن
def load_stock_pro():
    if not os.path.exists("data_stock.csv"):
        pd.DataFrame(columns=["المنتج", "الكمية", "السعر"]).to_csv("data_stock.csv", index=False, encoding='utf-8-sig')
    return pd.read_csv("data_stock.csv")

df_stock = load_stock_pro()

# تبويبات لتنظيم العمل
tab_sale, tab_add, tab_view = st.tabs(["🛒 بيع سريع (بحث)", "➕ إضافة بضاعة جديدة", "📊 جرد المخزن الكلي"])

with tab_add:
    st.subheader("تسجيل بضاعة جديدة في النظام")
    with st.form("add_stock_pro_form", clear_on_submit=True):
        p_name = st.text_input("اسم المنتج (مثلاً: شامبو عبوة كبيرة)")
        p_qty = st.number_input("الكمية المتوفرة حالياً", min_value=0, step=1)
        p_price = st.number_input("سعر البيع المفرد (دينار)", min_value=0, step=250)
        if st.form_submit_button("إضافة للمخزن ✅"):
            if p_name:
                new_p = pd.DataFrame([[p_name, p_qty, p_price]], columns=["المنتج", "الكمية", "السعر"])
                df_stock = pd.concat([df_stock, new_p], ignore_index=True)
                df_stock.to_csv("data_stock.csv", index=False, encoding='utf-8-sig')
                st.success(f"تم تسجيل {p_name} بنجاح!")
                st.rerun()

with tab_sale:
    st.subheader("عملية بيع سريعة")
    if not df_stock.empty:
        # ميزة البحث الذكي - تكتب اسم المنتج ويظهر لك فوراً
        search_query = st.selectbox("ابحث عن المنتج بالاسم:", df_stock["المنتج"], index=None, placeholder="اكتب اسم المنتج هنا...")
        
        if search_query:
            # جلب معلومات المنتج المختار
            product_data = df_stock[df_stock["المنتج"] == search_query].iloc[0]
            st.info(f"الكمية المتوفرة: {product_data['الكمية']} | السعر: {int(product_data['السعر']):,} د.ع")
            
            with st.form("confirm_sale"):
                qty_to_sell = st.number_input("الكمية المباعة", min_value=1, max_value=int(product_data['الكمية']), value=1)
                if st.form_submit_button("إتمام عملية البيع 💰"):
                    # 1. تحديث كمية المخزن
                    df_stock.loc[df_stock["المنتج"] == search_query, "الكمية"] -= qty_to_sell
                    df_stock.to_csv("data_stock.csv", index=False, encoding='utf-8-sig')
                    
                    # 2. تسجيل الوارد المالي تلقائياً
                    total_p = product_data['السعر'] * qty_to_sell
                    now_date = datetime.datetime.now().strftime("%Y-%m-%d")
                    new_f = pd.DataFrame([[now_date, f"بيع: {search_query} (عدد {qty_to_sell})", "وارد", total_p]], columns=FIN_COLS)
                    
                    # قراءة الحسابات الحالية وإضافة البيعة لها
                    df_fin_current = pd.read_csv("data_finance.csv")
                    pd.concat([df_fin_current, new_f], ignore_index=True).to_csv("data_finance.csv", index=False, encoding='utf-8-sig')
                    
                    st.success(f"تم البيع بنجاح! السعر الإجمالي: {total_p:,} د.ع")
                    st.rerun()
    else:
        st.warning("المخزن فارغ تماماً، ابدأ بإضافة بضاعة.")

with tab_view:
    st.subheader("جرد المنتجات وحالة المخازن")
    if not df_stock.empty:
        # تمييز المنتجات التي أوشكت على النفاد
        def highlight_low_stock(s):
            return ['background-color: #ff4b4b' if s.الكمية < 5 else '' for _ in s]
        
        st.write("المنتجات الملونة بالأحمر أوشكت على النفاذ (أقل من 5 قطع):")
        st.dataframe(df_stock.style.apply(highlight_low_stock, axis=1), use_container_width=True)
        
        if st.button("🗑️ حذف منتج من القائمة"):
            st.warning("لحذف منتج، يرجى القيام بذلك يدوياً من ملف CSV حالياً لضمان سلامة البيانات.")
    else:
        st.info("لا توجد بضاعة لعرضها.")
# =================================================
# كود الوصل بنظام "المزامنة التلقائية" - مكتبة أيوب الذكية
# =================================================

st.write("---")
st.subheader("🧾 نظام إصدار الوصلات الفوري")

# وظيفة لحفظ آخر عملية بيع في ملف مؤقت لكي يراها الكود في الأسفل
def sync_last_sale():
    # هذا الجزء يحاول صيد المتغيرات من الكود الذي كتبته أنت في الأعلى
    # سنبحث عن (المبلغ، اسم المنتج، الكمية)
    try:
        # نحن نفترض أن متغيراتك اسمها (selection, q_sold, total_amount) أو (choice, qty, total)
        current_item = locals().get('selection') or locals().get('choice') or "منتج"
        current_qty = locals().get('q_sold') or locals().get('qty') or 1
        current_total = locals().get('total_amount') or locals().get('total') or 0
        
        if current_total > 0:
            with open("temp_receipt.txt", "w", encoding="utf-8") as f:
                f.write(f"{current_item}|{current_qty}|{current_total}")
    except:
        pass

sync_last_sale()

# قراءة البيانات وعرض الوصل
if os.path.exists("temp_receipt.txt"):
    with open("temp_receipt.txt", "r", encoding="utf-8") as f:
        data = f.read().split("|")
        
    p_name = data[0]
    p_qty = data[1]
    p_total = data[2]
    
    now_full = datetime.datetime.now()
    v_date = now_full.strftime("%Y-%m-%d")
    v_time = now_full.strftime("%H:%M:%S")

    receipt_html = f"""
    <div style="background: white; color: black; padding: 25px; border: 2px solid #000; border-style: double; width: 280px; margin: auto; font-family: 'Cairo', sans-serif; direction: rtl; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
        <h2 style="margin: 0;">مكتبة أيوب الذكية</h2>
        <p style="font-size: 11px; margin: 5px 0;">وصل مبيعات الكتروني</p>
        <hr>
        <div style="font-size: 11px; display: flex; justify-content: space-between;">
            <span><b>التاريخ:</b> {v_date}</span>
            <span><b>الوقت:</b> {v_time}</span>
        </div>
        <table style="width: 100%; border-collapse: collapse; font-size: 14px; margin-top: 15px; text-align: right;">
            <tr style="border-bottom: 2px solid #000;">
                <th>المادة</th> <th>العدد</th> <th>السعر</th>
            </tr>
            <tr>
                <td style="padding: 10px 0;">{p_name}</td>
                <td style="text-align: center;">{p_qty}</td>
                <td style="text-align: left;">{int(float(p_total)):,}</td>
            </tr>
        </table>
        <div style="border-top: 2px solid #000; margin-top: 15px; padding-top: 10px; font-weight: bold; font-size: 16px; display: flex; justify-content: space-between;">
            <span>المجموع:</span>
            <span>{int(float(p_total)):,} د.ع</span>
        </div>
        <button onclick="window.print()" style="width: 100%; padding: 12px; background: black; color: #FFD700; border: none; border-radius: 8px; cursor: pointer; font-weight: bold; font-family: 'Cairo'; margin-top: 15px;">🖨️ طباعة الوصل الآن</button>
    </div>
    """
    st.components.v1.html(receipt_html, height=520)
    
    if st.button("🗑️ مسح الوصل الحالي"):
        os.remove("temp_receipt.txt")
        st.rerun()
else:
    st.info("💡 يا أيوب، النظام بانتظار عملية بيع. إذا بعت ولم يظهر شيء، فهذا يعني أن أسماء المتغيرات في كودك تختلف عن كودي.")
