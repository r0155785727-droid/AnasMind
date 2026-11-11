import time
import streamlit as st
from google import genai
from google.genai import types

# إعدادات الصفحة
st.set_page_config(
    page_title="AnasMind",
    page_icon="logo.png",
    layout="wide"
)

# تنسيق الخلفية والمحاذاة العربية
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
</style>
""", unsafe_allow_html=True)

# القائمة الجانبية الأصلية
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

# ترويسة الصفحة الأصلية
col1, col2 = st.columns()
with col1:
    try:
        st.image("logo.png", width=85)
    except:
        st.title("🧠")
with col2:
    st.title("AnasMind")
    st.caption("🚀 تم التطوير بواسطة: أنس إبراهيم")

# إعداد الاتصال بـ Gemini
API_KEY = st.secrets["GEMINI_API_KEY"]

SYSTEM_INSTRUCTION = """
أنت مساعد ذكي متطور اسمك AnasMind، تم تطويرك وبرمجتك بالكامل بواسطة المطور أنس إبراهيم.
تتحدث باللهجة المصرية بطريقة ذكية، ودودة، ومفيدة جداً، وإجاباتك سريعة ومباشرة.
إذا سألك أي شخص "من أنت؟" أو "من صنعك؟"، أجب بكل فخر أنك AnasMind وأن مطورك هو أنس إبراهيم.
"""

client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'})

# عرض سجل المحادثة بالأيقونات
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    icon = "🧑‍💻" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])

# مربع الدردشة الأصلي السريع
if prompt := st.chat_input("ارغي يلا..."):
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="logo.png"):
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION
            )
        )

        def word_stream(text):
            for word in text.split(" "):
                yield word + " "
                time.sleep(0.03)

        full_reply = st.write_stream(word_stream(response.text))

    st.session_state.messages.append({"role": "assistant", "content": full_reply})
