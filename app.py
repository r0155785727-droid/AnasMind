import json
import os
import time
import hashlib
from io import BytesIO
from PIL import Image
import streamlit as st
from google import genai
from google.genai import types

# 1. إعدادات الصفحة
st.set_page_config(
    page_title="AnasMind Pro",
    page_icon="logo.png",
    layout="wide"
)

# 2. تنسيق CSS احترافي واتجاه عربي (RTL)
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #090d16 0%, #111827 50%, #0f172a 100%);
        color: #f8fafc;
    }
    .stChatMessage, .stMarkdown, .stTextInput, .stTextArea {
        direction: rtl;
        text-align: right;
    }
    [data-testid="stChatInput"] > div:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.3) !important;
    }
</style>
""", unsafe_allow_html=True)

# 3. دوال مساعدة لحفظ المستخدمين والشات القديم بأمان
USERS_FILE = "users_db.json"
CHATS_FILE = "chats_db.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_json(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_json(filepath, data):
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# تهيئة الجلسة
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = str(int(time.time()))

# إعداد Gemini
API_KEY = st.secrets["GEMINI_API_KEY"]
client = genai.Client(api_key=API_KEY)

# ==========================================
# 4. القائمة الجانبية (تسجيل الدخول + الأقسام + الشات القديم)
# ==========================================
with st.sidebar:
    try:
        st.image("logo.png", width=130)
    except Exception:
        st.title("🧠 AnasMind")

    st.caption("🚀 تطوير: أنس إبراهيم")
    st.markdown("---")

    # --- خانة 4: تسجيل الدخول بالإيميل والباسورد وحفظهم ---
    st.subheader("🔐 الحساب")
    if not st.session_state.logged_in_user:
        auth_mode = st.radio("اختر:", ["تسجيل الدخول", "إنشاء حساب جديد"], horizontal=True, label_visibility="collapsed")
        email = st.text_input("البريد الإلكتروني", placeholder="name@example.com")
        password = st.text_input("كلمة المرور", type="password", placeholder="••••••••")

        if st.button("تأكيد 🚀", use_container_width=True):
            users = load_json(USERS_FILE)
            if not email or "@" not in email or len(password) < 4:
                st.error("⚠️ أدخل إيميلاً صحيحاً وباسورد (4 أحرف على الأقل).")
            elif auth_mode == "إنشاء حساب جديد":
                if email in users:
                    st.warning("⚠️ هذا الإيميل مسجل بالفعل، اختر تسجيل الدخول.")
                else:
                    users[email] = hash_password(password)
                    save_json(USERS_FILE, users)
                    st.session_state.logged_in_user = email
                    st.success("✅ تم إنشاء الحساب وتسجيل الدخول!")
                    st.rerun()
            else:
                if email in users and users[email] == hash_password(password):
                    st.session_state.logged_in_user = email
                    st.rerun()
                else:
                    st.error("❌ الإيميل أو كلمة المرور غير صحيحة.")
    else:
        st.success(f"مرحباً: **{st.session_state.logged_in_user}**")
        if st.button("تسجيل الخروج 🚪", use_container_width=True):
            st.session_state.logged_in_user = None
            st.session_state.messages = []
            st.session_state.current_chat_id = str(int(time.time()))
            st.rerun()

    st.markdown("---")

    # --- اختيار القسم (1: الدردشة | 2: التعلم | 3: إنشاء صور) ---
    st.subheader("🧭 الأقسام")
    selected_section = st.radio(
        "انتقل إلى:",
        ["💬 الدردشة", "📚 التعلم", "🎨 إنشاء صور"],
        label_visibility="collapsed"
    )

    st.markdown("---")

    # --- خانة 5 و 6: الشات القديم ومسح الشات ---
    st.subheader("🗂️ إدارة المحادثات")
    user_key = st.session_state.logged_in_user or "guest"
    all_chats = load_json(CHATS_FILE)
    user_chats = all_chats.get(user_key, {})

    if st.button("➕ محادثة جديدة", use_container_width=True):
        st.session_state.messages = []
        st.session_state.current_chat_id = str(int(time.time()))
        st.rerun()

    if user_chats:
        chat_titles = {cid: cdata["title"] for cid, cdata in user_chats.items()}
        selected_cid = st.selectbox(
            "الشات القديم:",
            options=list(chat_titles.keys()),
            format_func=lambda x: chat_titles[x],
            index=None,
            placeholder="اختر محادثة سابقة..."
        )
        if selected_cid and selected_cid != st.session_state.current_chat_id:
            st.session_state.current_chat_id = selected_cid
            st.session_state.messages = user_chats[selected_cid]["messages"]
            st.rerun()

    if st.button("🗑️ مسح الشات الحالي", use_container_width=True):
        st.session_state.messages = []
        if st.session_state.current_chat_id in user_chats:
            del all_chats[user_key][st.session_state.current_chat_id]
            save_json(CHATS_FILE, all_chats)
        st.rerun()

# ==========================================
# دالة مساعدة لتشغيل الدردشة والتعلم بسرعة وبدون أخطاء
# ==========================================
def run_chat_interface(title, subtitle, system_prompt, placeholder_text):
    st.title(title)
    st.caption(subtitle)

    for msg in st.session_state.messages:
        icon = "🧑‍💻" if msg["role"] == "user" else "logo.png"
        with st.chat_message(msg["role"], avatar=icon):
            st.markdown(msg["content"])

    if prompt := st.chat_input(placeholder_text):
        with st.chat_message("user", avatar="🧑‍💻"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant", avatar="logo.png"):
            reply_text = None
            for model_name in ["gemini-3.8-flash", "gemini-2.5-flash-lite"]:
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(system_instruction=system_prompt)
                    )
                    reply_text = response.text
                    break
                except Exception:
                    continue

            if reply_text:
                def word_stream(text):
                    for w in text.split(" "):
                        yield w + " "
                        time.sleep(0.025)

                full_reply = st.write_stream(word_stream(reply_text))
                st.session_state.messages.append({"role": "assistant", "content": full_reply})

                # حفظ المحادثة تلقائياً في الشات القديم
                all_c = load_json(CHATS_FILE)
                if user_key not in all_c:
                    all_c[user_key] = {}
                chat_title = st.session_state.messages["content"][:30] + "..."
                all_c[user_key][st.session_state.current_chat_id] = {
                    "title": chat_title,
                    "messages": st.session_state.messages
                }
                save_json(CHATS_FILE, all_c)
            else:
                st.warning("⚠️ الخادم مزدحم حالياً، جرب إرسال الرسالة مرة أخرى.")

# ==========================================
# 5. عرض المحتوى حسب القسم المختار
# ==========================================
if selected_section == "💬 الدردشة":
    SYS_CHAT = "أنت AnasMind، مساعد ذكي من تطوير أنس إبراهيم. تتحدث باللهجة المصرية بطريقة ذكية وسريعة ومفيدة."
    run_chat_interface("💬 دردشة AnasMind", "اسألني في أي موضوع وهجاوبك فوراً", SYS_CHAT, "اكتب رسالتك هنا...")

elif selected_section == "📚 التعلم":
    SYS_LEARN = """
    أنت معلم خبير ومساعد تعليمي في منصة AnasMind من تطوير أنس إبراهيم.
    مهمتك شرح الدروس والمفاهيم بأسلوب مبسط جداً ومنظم في نقاط، مع إعطاء أمثلة عملية وأسئلة اختبار قصيرة في نهاية الشرح للتأكد من فهم الطالب.
    """
    run_chat_interface("📚 ركن التعلم الذكي", "اشرح لي درساً، لخص كتاباً، أو اختبرني في مادة", SYS_LEARN, "اكتب اسم الدرس أو الموضوع اللي عايز تتعلمه...")

elif selected_section == "🎨 إنشاء صور":
    st.title("🎨 استوديو إنشاء الصور")
    st.caption("اكتب وصف الصورة التي تتخيلها وسأقوم برسمها لك بالذكاء الاصطناعي")

    img_prompt = st.text_area("وصف الصورة (يفضل كتابة تفاصيل دقيقة):", placeholder="مثال: شخصية أنمي بأسلوب سينمائي وإضاءة زرقاء...")
    if st.button("✨ إنشاء الصورة الآن", use_container_width=True):
        if not img_prompt.strip():
            st.warning("⚠️ اكتب وصف الصورة أولاً!")
        else:
            with st.spinner("🎨 جاري رسم الصورة..."):
                image_rendered = False

                # المحاولة الأولى: عبر نموذج Gemini الرسمي للصور
                for img_model in ["gemini-2.5-flash-image", "gemini-2.0-flash-preview-image-generation"]:
                    try:
                        response = client.models.generate_content(
                            model=img_model,
                            contents=f"Generate an image of: {img_prompt}",
                            config=types.GenerateContentConfig(
                                response_modalities=["IMAGE", "TEXT"]
                            )
                        )
                        for part in response.candidates.content.parts:
                            if part.inline_data:
                                image = Image.open(BytesIO(part.inline_data.data))
                                st.image(image, caption=img_prompt, use_container_width=True)

                                buf = BytesIO()
                                image.save(buf, format="PNG")
                                st.download_button(
                                    label="📥 تحميل الصورة",
                                    data=buf.getvalue(),
                                    file_name="AnasMind_Art.png",
                                    mime="image/png"
                                )
                                image_rendered = True
                                break
                        if image_rendered:
                            break
                    except Exception:
                        continue

                # المحاولة الثانية (البديل المجاني الفوري): إذا كان مفتاح Gemini المجاني لا يدعم الصور
                if not image_rendered:
                    import urllib.parse
                    import urllib.request

                    # ترجمة الوصف للإنجليزية عبر Gemini للحصول على أفضل نتيجة رسم
                    try:
                        trans = client.models.generate_content(
                            model="gemini-3.8-flash",
                            contents=f"Translate this image prompt to detailed English only without any extra text: {img_prompt}"
                        )
                        en_prompt = trans.text.strip()
                    except Exception:
                        en_prompt = img_prompt
                    clean_prompt = " ".join(en_prompt.split())
                    encoded_prompt = urllib.parse.quote(en_prompt)
                    image_url = f"https://pollinations.ai{encoded_prompt}?width=1024&height=1024&nologo=true"

                    try:
                        req = urllib.request.Request(image_url, headers={'User-Agent': 'Mozilla/5.0'})
                        with urllib.request.urlopen(req, timeout=30) as resp:
                            img_bytes = resp.read()
                            image = Image.open(BytesIO(img_bytes))
                            st.image(image, caption=img_prompt, use_container_width=True)
                            st.download_button(
                                label="📥 تحميل الصورة",
                                data=img_bytes,
                                file_name="AnasMind_Art.png",
                                mime="image/png"
                            )
                    except Exception as e:
                        st.error(f"⚠️ تعذر إنشاء الصورة حالياً، حاول مرة أخرى: {e}")
