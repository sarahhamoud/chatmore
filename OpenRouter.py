import streamlit as st
from openai import OpenAI
from io import BytesIO
from datetime import datetime
from docx import Document

# =========================
# Page config
# =========================
st.set_page_config(
    page_title="Smart AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# CSS (Clean + NO empty rectangles + topbar + toolbar)
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

/* Remove Streamlit default separators/extra lines */
hr, [data-testid="stDivider"]{display:none !important;}

/* Remove default “gray blocks” look */
[data-testid="stToolbar"]{display:none !important;}         /* يخفي شريط ستريم لت الافتراضي */
[data-testid="stStatusWidget"]{display:none !important;}
[data-testid="stDecoration"]{display:none !important;}

/* Layout spacing (so topbar doesn't block view) */
.block-container{
  max-width: 980px;
  padding-top: 6.2rem;    /* مساحة للشريط العلوي */
  padding-bottom: 2.0rem;
}

/* =========================
   TOPBAR (fixed, not blocking)
========================= */
.app-topbar{
  position: fixed;
  top: 10px;
  left: 50%;
  transform: translateX(-50%);
  width: min(980px, calc(100% - 18px));
  z-index: 9999;
  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  border-radius: 20px;
  padding: 12px 14px;
  box-shadow: 0 16px 34px rgba(0,0,0,.18);
}

/* Brand text */
.app-title{
  color:#fff;
  font-weight: 1000;
  font-size: 22px;
  margin:0;
  line-height:1.2;
  text-shadow: 0 2px 7px rgba(0,0,0,.25);
}
.app-sub{
  color:#fff7ed;
  font-weight: 800;
  font-size: 15px;
  margin: 2px 0 0 0;
  opacity: .95;
}

/* =========================
   Toolbar (radio horizontal) styled as pills
========================= */
div[role="radiogroup"]{
  display:flex !important;
  gap: 10px !important;
  flex-wrap: wrap;
  justify-content: flex-start;
  margin-top: 10px;
}

/* Hide radio dot */
div[role="radiogroup"] label > div:first-child{
  display:none !important;
}

/* Each pill */
div[role="radiogroup"] label{
  background: rgba(255,255,255,.88);
  border: 1px solid rgba(15,23,42,.12);
  border-radius: 14px;
  padding: 10px 14px;
  font-weight: 1000;
  font-size: 17px;
  box-shadow: 0 10px 20px rgba(2,6,23,.06);
  cursor: pointer;
}

/* Selected pill (Streamlit adds aria-checked on input; style via label:has) */
div[role="radiogroup"] label:has(input:checked){
  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  border: none;
  color:#0f172a;
}

/* =========================
   Cards + Gradient border (NO empty rectangles)
========================= */
.grad-border{
  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  padding: 3px;
  border-radius: 22px;
  margin-bottom: 14px;
  box-shadow: 0 14px 30px rgba(20,184,166,.22);
}
.grad-inner{
  background:#fff;
  border-radius: 20px;
  padding: 16px;
}

/* Input */
textarea, input, [data-baseweb="select"] > div{
  border-radius: 16px !important;
  border: 1px solid rgba(0,0,0,.14) !important;
  font-size: 18px !important;
  background:#fff !important;
}
label{
  font-size: 18px !important;
  font-weight: 1000 !important;
}

/* Button */
.stButton > button{
  width: 100%;
  border-radius: 16px;
  padding: .95rem 1rem;
  font-weight: 1000;
  font-size: 18px;
  border: none;
  background: linear-gradient(135deg,#fb923c,#facc15);
  color:#0f172a;
  box-shadow: 0 12px 24px rgba(251,146,60,.30);
}

/* Chat bubbles */
.bubble{
  background:#f8fafc;
  border:1px solid rgba(15,23,42,.08);
  border-radius: 16px;
  padding: 10px 12px;
  margin: 8px 0;
  font-size: 17px;
  line-height: 2.0;
}
.bubble-user{
  background:#f0fdfa;
  border-color: rgba(20,184,166,.40);
}
.bubble-ass{
  background:#fff7ed;
  border-color: rgba(251,146,60,.40);
}

/* Result */
.result{
  background:#f0fdfa;
  border: 1px solid rgba(20,184,166,.60);
  border-radius: 18px;
  padding: 14px;
  font-size: 18px;
  line-height: 2.1;
}

/* Mobile tweaks */
@media (max-width:520px){
  .block-container{padding-top: 6.8rem;}
  .app-title{font-size: 20px;}
  .app-sub{font-size: 14px;}
  div[role="radiogroup"] label{font-size:16px; padding: 9px 12px;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# Topbar (Name + Toolbar)
# =========================
st.markdown("""
<div class="app-topbar">
  <p class="app-title"> Smart AI Assistant</p>
  <p class="app-sub">Sarah Hamoud Hussien</p>
</div>
""", unsafe_allow_html=True)

# =========================
# Secrets
# =========================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL_DEFAULT", "openai/gpt-3.5-turbo")

if not OPENROUTER_API_KEY:
    st.error("ضعي OPENROUTER_API_KEY داخل Secrets في Streamlit Cloud.")
    st.stop()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# =========================
# State
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""
if "page" not in st.session_state:
    st.session_state.page = " دردشة"

# =========================
# Helpers
# =========================
def ask_llm(messages):
    return client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=700
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
# TOOLBAR (clear)
# =========================
st.session_state.page = st.radio(
    "",
    [" دردشة", " أدوات", " تنزيل", " إعدادات"],
    horizontal=True,
    label_visibility="collapsed"
)

# =========================
# PAGES
# =========================
page = st.session_state.page

if page == " دردشة":
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    st.markdown("### المحادثة")

    if not st.session_state.chat:
        st.info("ابدئي بسؤال…")

    for m in st.session_state.chat[-20:]:
        who = "أنتِ" if m["role"] == "user" else "المساعد"
        bubble_class = "bubble bubble-user" if m["role"] == "user" else "bubble bubble-ass"
        st.markdown(f"<div class='{bubble_class}'><b>{who}:</b><br>{m['content']}</div>", unsafe_allow_html=True)

    st.markdown('</div></div>', unsafe_allow_html=True)

    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    user_msg = st.text_area("اكتبي رسالتك:", height=140, placeholder="اسألي أي شيء…")
    send = st.button("إرسال")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if send:
        if not user_msg.strip():
            st.warning("رجاءً اكتبي رسالة أولاً.")
        else:
            st.session_state.chat.append({"role": "user", "content": user_msg.strip(), "ts": datetime.now().isoformat()})

            with st.spinner("جاري الرد..."):
                resp = ask_llm([
                    {"role": "system", "content": "أنت مساعد عربي محترف، واضح ومنظم."},
                    *[{"role": x["role"], "content": x["content"]} for x in st.session_state.chat[-10:]]
                ])
                answer = resp.choices[0].message.content.strip()
                st.session_state.chat.append({"role": "assistant", "content": answer, "ts": datetime.now().isoformat()})
                st.session_state.last_result = answer
                st.rerun()

elif page == " أدوات":
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    st.markdown("### أدوات NLP")

    task = st.selectbox("اختاري المهمة:", ["تلخيص", "إعادة صياغة", "ترجمة EN↔AR", "تحليل مشاعر"])
    user_text = st.text_area("أدخلي النص هنا:", height=200, placeholder="الصقي نص/خبر/مقال هنا...")
    run = st.button("تنفيذ")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if run:
        if not user_text.strip():
            st.warning("رجاءً أدخلي نص أولاً.")
        else:
            if task == "تلخيص":
                prompt = f"لخّص النص التالي بالعربية بشكل واضح ومنظم (نقاط + خلاصة):\n\n{user_text}"
            elif task == "إعادة صياغة":
                prompt = f"أعد صياغة النص التالي بالعربية بأسلوب احترافي مع الحفاظ على المعنى:\n\n{user_text}"
            elif task == "ترجمة EN↔AR":
                prompt = f"ترجم النص التالي (إنجليزي↔عربي) مع الحفاظ على السياق:\n\n{user_text}"
            else:
                prompt = f"حلل المشاعر في النص التالي (إيجابي/سلبي/محايد) واذكر السبب:\n\n{user_text}"

            with st.spinner("جاري المعالجة..."):
                resp = ask_llm([
                    {"role": "system", "content": "أنت مساعد عربي محترف. كن واضحاً ومنظماً."},
                    {"role": "user", "content": prompt}
                ])
                result = resp.choices[0].message.content.strip()
                st.session_state.last_result = result

            st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
            st.markdown("### النتيجة")
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

elif page == " تنزيل":
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    st.markdown("### تنزيل آخر نتيجة")

    if not st.session_state.last_result:
        st.info("لا توجد نتيجة بعد. استخدمي الدردشة أو الأدوات أولاً.")
    else:
        st.markdown(f"<div class='result'>{st.session_state.last_result}</div>", unsafe_allow_html=True)
        docx = make_docx("Smart AI Assistant — Result", st.session_state.last_result)
        st.download_button(
            " تحميل Word",
            data=docx,
            file_name="result.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True
        )

    st.markdown('</div></div>', unsafe_allow_html=True)

else:  # Settings
    st.markdown('<div class="grad-border"><div class="grad-inner">', unsafe_allow_html=True)
    st.markdown("### إعدادات")
    if st.button(" مسح المحادثة", use_container_width=True):
        st.session_state.chat = []
        st.session_state.last_result = ""
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
