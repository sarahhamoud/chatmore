import streamlit as st
from openai import OpenAI
from io import BytesIO
from datetime import datetime
from docx import Document
import os

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Smart AI Assistant",
    page_icon=" ",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CSS (Clean + Big + Colorful)
# =========================
st.markdown("""
<style>

/* RTL + Font */
html, body, [data-testid="stAppViewContainer"]{
    direction: RTL;
    text-align: right;
    font-family: "Tajawal","Cairo","Tahoma","Arial",sans-serif;
}

/* Background */
[data-testid="stAppViewContainer"]{
    background: linear-gradient(180deg,#f0fdfa 0%,#fffbeb 55%,#fff7ed 100%);
    color:#0f172a;
}

/* Remove blank boxes & dividers */
hr, [data-testid="stDivider"]{display:none !important;}
[data-testid="stVerticalBlock"] > div:empty{display:none !important;}

/* Container */
.block-container{
    max-width: 950px;
    padding-top: 1rem;
    padding-bottom: 2.5rem;
}

/* Tabs */
button[data-baseweb="tab"]{
    font-size: 19px !important;
    font-weight: 1000 !important;
    padding: 12px 16px !important;
}
button[data-baseweb="tab"][aria-selected="true"]{
    background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c) !important;
    border-radius: 14px !important;
    color:#0f172a !important;
}
[data-baseweb="tab-list"]{
    background: rgba(255,255,255,.7);
    border-radius: 18px;
    padding: 6px;
    border: 1px solid rgba(0,0,0,.08);
}

/* Gradient border box */
.grad-border{
    background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
    padding: 3px;
    border-radius: 22px;
    margin-bottom: 16px;
    box-shadow: 0 14px 30px rgba(20,184,166,.25);
}
.grad-inner{
    background: #ffffff;
    border-radius: 20px;
    padding: 18px;
}

/* Inputs */
textarea, input, [data-baseweb="select"] > div{
    font-size: 18px !important;
    border-radius: 16px !important;
    border: 1px solid rgba(0,0,0,.15) !important;
}

/* Labels */
label{
    font-size: 18px !important;
    font-weight: 1000 !important;
}

/* Buttons */
.stButton > button{
    width:100%;
    font-size: 18px;
    font-weight: 1000;
    padding: 0.95rem;
    border-radius: 16px;
    background: linear-gradient(135deg,#fb923c,#facc15);
    color:#0f172a;
    border:none;
    box-shadow: 0 10px 22px rgba(251,146,60,.35);
}

/* Result */
.result{
    background:#f0fdfa;
    border: 1px solid rgba(20,184,166,.6);
    border-radius: 18px;
    padding: 16px;
    font-size: 18px;
    line-height: 2.1;
}

/* Mobile */
@media (max-width:520px){
    button[data-baseweb="tab"]{font-size:17px !important;}
}

</style>
""", unsafe_allow_html=True)

# =========================
# Secrets
# =========================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL_DEFAULT", "openai/gpt-3.5-turbo")

if not OPENROUTER_API_KEY:
    st.error("ضعي OPENROUTER_API_KEY داخل Secrets")
    st.stop()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY
)

# =========================
# Session state
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# =========================
# Helpers
# =========================
def ask_llm(messages):
    return client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=700,
    )

def make_docx(title, content):
    doc = Document()
    doc.add_heading(title, 1)
    for p in content.split("\n"):
        doc.add_paragraph(p)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

# =========================
# Tabs
# =========================
tab_chat, tab_tools, tab_export, tab_settings = st.tabs(
    [" دردشة", " أدوات", " تنزيل", " إعدادات"]
)

# =========================
# Chat
# =========================
with tab_chat:
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    st.markdown("###  المحادثة")

    for msg in st.session_state.chat[-20:]:
        who = "أنتِ" if msg["role"] == "user" else "المساعد"
        st.markdown(f"**{who}:** {msg['content']}")

    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    user_msg = st.text_area("اكتبي رسالتك:", height=130)
    send = st.button("إرسال")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if send and user_msg.strip():
        st.session_state.chat.append({"role":"user","content":user_msg})
        with st.spinner("جاري الرد..."):
            resp = ask_llm([
                {"role":"system","content":"أنت مساعد عربي محترف وواضح."},
                *st.session_state.chat[-10:]
            ])
            answer = resp.choices[0].message.content.strip()
            st.session_state.chat.append({"role":"assistant","content":answer})
            st.session_state.last_result = answer
            st.rerun()

# =========================
# Tools
# =========================
with tab_tools:
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    task = st.selectbox("اختاري المهمة:", ["تلخيص","إعادة صياغة","ترجمة EN↔AR","تحليل مشاعر"])
    text = st.text_area("النص:", height=180)
    run = st.button("تنفيذ")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if run and text.strip():
        prompt = f"{task}:\n{text}"
        resp = ask_llm([
            {"role":"system","content":"أنت مساعد عربي محترف."},
            {"role":"user","content":prompt}
        ])
        result = resp.choices[0].message.content.strip()
        st.session_state.last_result = result

        st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
        st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)

# =========================
# Export
# =========================
with tab_export:
    if st.session_state.last_result:
        docx = make_docx("Smart AI Assistant", st.session_state.last_result)
        st.download_button(
            " تحميل Word",
            data=docx,
            file_name="result.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )
    else:
        st.info("لا توجد نتيجة بعد")

# =========================
# Settings
# =========================
with tab_settings:
    if st.button(" مسح المحادثة", use_container_width=True):
        st.session_state.chat = []
        st.session_state.last_result = ""
        st.rerun()

