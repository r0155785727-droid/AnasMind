import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AnasMind", page_icon="logo.png", layout="centered")
st.markdown("""
<style>
.stApp {
    background: radial-gradient(circle at top, #131c31 0%, #090d16 55%, #05070c 100%) !important;
    color: #ffffff !important;
}

[data-testid="stHeader"] {
    background: rgba(0, 0, 0, 0) !important;
}

[data-testid="stBottom"] > div {
    background: transparent !important;
}

@keyframes ai-glow {
    0% {
        border-color: #00d2ff;
        box-shadow: 0 0 18px rgba(0, 210, 255, 0.8), 0 0 30px rgba(58, 123, 213, 0.4);
    }
    33% {
        border-color: #9d50bb;
        box-shadow: 0 0 18px rgba(157, 80, 187, 0.8), 0 0 30px rgba(110, 72, 170, 0.4);
    }
    66% {
        border-color: #ff007f;
        box-shadow: 0 0 18px rgba(255, 0, 127, 0.8), 0 0 30px rgba(255, 85, 163, 0.4);
    }
    100% {
        border-color: #00d2ff;
        box-shadow: 0 0 18px rgba(0, 210, 255, 0.8), 0 0 30px rgba(58, 123, 213, 0.4);
    }
}

[data-testid="stChatInput"] > div {
    border: 2px solid #00d2ff !important;
    border-radius: 16px !important;
    animation: ai-glow 4s infinite linear !important;
    transition: transform 0.2s ease !important;
}

[data-testid="stChatInput"] > div:focus-within {
    animation-duration: 2s !important;
    transform: scale(1.01) !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("🧠 **AnasMind**")
    st.markdown("المطور ANAS في خدمتك")
    st.info("تم تطوير وبرمجة AnasMind بواسطة المطور **أنس إبراهيم**.")
    if st.button("مسح المحادثة 🗑️"):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")

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
                st.error("ا😶لبريد لا خاطىء للاسف")
    else:
        st.success(f"مسجل الدخول بـ:\n**{st.session_state.user_email}**")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.user_email = ""
            st.session_state.messages = []
            st.rerun()

col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image("logo.png", width=85)
    except:
        st.title("🧠")
with col2:
    st.title("AnasMind")
    st.caption("تم التطوير بواسطة: أنس إبراهيم 🚀")

API_KEY = st.secrets["GEMINI_API_KEY"]

SYSTEM_INSTRUCTION = """
أنت مساعد ذكي متطور اسمك AnasMind، تم تطويرك وبرمجتك بالكامل بواسطة المطور أنس إبراهيم.
تتحدث باللهجة المصرية بطريقة ذكية، ودودة، ومفيدة جداً، وإجاباتك سريعة ومباشرة.
إذا سألك أي شخص "من أنت؟" أو "من صنعك؟"، أجب بكل فخر أنك AnasMind وأن مطورك هو أنس إبراهيم.
"""

client = genai.Client(api_key=API_KEY, http_options={'api_version': 'v1alpha'})

if "messages" not in st.session_state:
    st.session_state.messages = []
    # لعرض سجل المحادثة بالأيقونات الجديدة
for message in st.session_state.messages:
    icon = "👦" if message["role"] == "user" else "logo.png"
    with st.chat_message(message["role"], avatar=icon):
        st.markdown(message["content"])


if prompt := st.chat_input("ارغي يلا..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        status_box = st.status("⚡ جاري تجهيز الرد بسرعة...", expanded=False)
        message_placeholder = st.empty()
        full_response = ""
        
        chat_history = [
            types.Content(
                role="user" if m["role"] == "user" else "model",
                parts=[types.Part.from_text(text=m["content"])]
            )
            for m in st.session_state.messages
        ]
        
        models_to_try = ["gemini-3.5-flash-lite", "gemini-3.8-flash"]
        success = False
        last_error = ""
        
        for model_name in models_to_try:
            try:
                response_stream = client.models.generate_content_stream(
                    model=model_name,
                    contents=chat_history,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_INSTRUCTION,
                    )
                )
                for chunk in response_stream:
                    if chunk.text:
                        full_response += chunk.text
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                status_box.update(label="✅ تم الرد", state="complete", expanded=False)
                st.session_state.messages.append({"role": "assistant", "content": full_response})
                success = True
                break
            except Exception as e:
                last_error = str(e)
                continue
        
        if not success:
            status_box.update(label="❌ حدث خطأ", state="error", expanded=True)
            st.error(f"السيرفرات مشغولة حالياً: {last_error}")
            
