import streamlit as st
from google import genai
from google.genai import types

st.set_page_config(page_title="AnasMind", page_icon="logo.png", layout="centered")

with st.sidebar:
    try:
        st.image("logo.png", width=150)
    except:
        st.write("🧠 **AnasMind**")
    st.markdown("### عن المنصة")
    st.info("تم تطوير وبرمجة AnasMind بواسطة المطور **أنس إبراهيم**.")
    if st.button("مسح المحادثة 🗑️"):
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

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("اسأل AnasMind أي شيء..."):
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
