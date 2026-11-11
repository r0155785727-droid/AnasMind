import time
import streamlit as st
from google import genai
from google.genai import types

# 1. إعدادات الصفحة الأساسية
st.set_page_config(
    page_title="AnasMind",
    page_icon="logo.png",
    layout="wide"
)

# 2. تنسيق الواجهة وضبط اتجاه اللغة العربية (RTL)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0b0f19 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
    }
    .stChatMessage, .stMarkdown, .stTextInput {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
        transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# 3. القائمة الجانبية (الشعار + تسجيل الدخول بالإيميل + مسح المحادثة)
with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("🧠 **AnasMind**")

    st.markdown("اعمل زيه يا عبده 😉")
    st.info("تم تطوير وبرمجة AnasMind بواسطة المطور **أنس إبراهيم**.")

    if st.button("مسح المحادثة 🗑️", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")

    # نظام تسجيل الدخول بالبريد الإلكتروني
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""

    if not st.session_state.user_email:
        st.subheader("تسجيل الدخول 🔐")
        email_input = st.text_input("البريد الإلكتروني:", placeholder="name@example.com")

        if st.button("دخول 🚀", use_container_width=True):
            if "@" in email_input and "." in email_input:
                st.session_state.user_email = email_input.strip()
                st.rerun()
            else:
                st.error("⚠️ من فضلك أدخل بريداً إلكترونياً صحيحاً!")
    else:
        st.success(f"مسجل الدخول بـ:\n**{st.session_state.user_email}**")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_email = ""
            st.session_state.messages = []
            st.rerun()

# 4. ترويسة الصفحة الرئيسية
col1, col2 = st.columns([1, 8])
with col1:
    try:
        st.image("logo.png", width=85)
    except:
        st.title("🧠")
with col2:
    st.title("AnasMind")
    st.caption("🚀 تم التطوير بواسطة: أنس إبراهيم")

# 5. إعداد الاتصال بنموذج Gemini
API_KEY = st.secrets["GEMINI_API_KEY"]

SYSTEM_INSTRUCTION = """
أنت مساعد ذكي متطور اسمك AnasMind، تم تطويرك وبرمجتك بالكامل بواسطة المطور أنس إبراهيم.
تتحدث باللهجة المصرية بطريقة ذكية، ودودة، ومفيدة جداً، وإجاباتك سريعة ومباشرة.
إذا سألك أي شخص "من أنت؟" أو "من صنعك؟"، أجب بكل فخر أنك AnasMind وأن مطورك هو أنس إبراهيم.
"""

client = genai.Client(api_key=API_KEY)

# 6. تهيئة وعرض سجل المحادثة بالأيقونات المخصصة
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    icon = "🧑‍💻" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])

# 7. مربع الكتابة ودعم رفع الصور والملفات
prompt = st.chat_input(
    "ارغي يلا أو ارفع صورة...",
    accept_file=True,
    file_type=["jpg", "jpeg", "png", "webp", "pdf"]
)

if prompt:
    user_text = prompt.text
    uploaded_file = prompt.files[0] if prompt.files else None

    with st.chat_message("user", avatar="🧑‍💻"):
        if user_text:
            st.markdown(user_text)
        if uploaded_file:
            if uploaded_file.type.startswith("image/"):
                st.image(uploaded_file, width=250)
            else:
                st.info(f"📄 تم إرفاق ملف: {uploaded_file.name}")

    st.session_state.messages.append({
        "role": "user",
        "content": user_text if user_text else f"[مرفق: {uploaded_file.name}]"
    })

    contents = []
    if user_text:
        contents.append(user_text)
    if uploaded_file:
        contents.append(types.Part.from_bytes(
            data=uploaded_file.getvalue(),
            mime_type=uploaded_file.type
        ))

    # 8. إرسال الطلب وعرض الرد كلمة بكلمة مثل شات جي بي تي
    with st.chat_message("assistant", avatar="logo.png"):
        try:
            # جلب أفضل نموذج متاح تلقائياً من حسابك
            available_models = [
                m.name.replace("models/", "")
                for m in client.models.list()
                if "flash" in m.name.lower() and "lite" not in m.name.lower()
            ]
            selected_model = available_models[0] if available_models else "gemini-2.5-flash"

            response = client.models.generate_content(
                model=selected_model,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION
                )
            )

            def word_by_word_stream(text):
                for word in text.split(" "):
                    yield word + " "
                    time.sleep(0.03)

            full_reply = st.write_stream(word_by_word_stream(response.text))
            st.session_state.messages.append({"role": "assistant", "content": full_reply})

        except Exception as e:
            st.error(f"⚠️ تفاصيل الخطأ: {e}")
