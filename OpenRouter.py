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
# CSS (Colors + Name + Toolbar + Hide Streamlit default bar)
# =========================
st.markdown(r"""
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

/* Remove dividers */
hr, [data-testid="stDivider"]{display:none !important;}

/* =========================
   ✅ HIDE STREAMLIT DEFAULT TOP BAR (Run/Share/Menu)
========================= */
header[data-testid="stHeader"]{ display:none !important; }
[data-testid="stToolbar"]{ display:none !important; }
[data-testid="stShareButton"]{ display:none !important; }

/* Remove top padding that Streamlit leaves */
[data-testid="stAppViewContainer"]{
  padding-top: 0rem !important;
}

/* Layout spacing so our topbar doesn't block */
.block-container{
  max-width: 980px;
  padding-top: 7.2rem;    /* مساحة للشريط المخصص */
  padding-bottom: 2rem;
}

/* =========================
   TOPBAR (Colorful + clear name)
========================= */
.app-topbar{
  position: fixed;
  top: 14px;
  left: 50%;
  transform: translateX(-50%);
  width: min(980px, calc(100% - 18px));
  z-index: 9999;

  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  border-radius: 22px;
  padding: 14px 16px;
  box-shadow: 0 16px 34px rgba(0,0,0,.18);
  border: 1px solid rgba(255,255,255,.35);
}

.app-title{
  color:#ffffff;
  font-weight: 1000;
  font-size: 23px;
  margin: 0;
  line-height: 1.15;
  text-shadow: 0 2px 8px rgba(0,0,0,.28);
}

.app-sub{
  margin: 4px 0 0 0;
  font-size: 16px;
  font-weight: 1000;
  color: #0f172a;
  background: rgba(255,255,255,.65);
  display: inline-block;
  padding: 4px 10px;
  border-radius: 12px;
}

/* =========================
   Toolbar (radio as colorful tabs)
========================= */
div[role="radiogroup"]{
  display:flex !important;
  gap: 10px !important;
  flex-wrap: wrap;
  justify-content: center;
  margin: 6px 0 14px 0;
}

/* Hide radio dot */
div[role="radiogroup"] label > div:first-child{
  display:none !important;
}

/* Each tab */
div[role="radiogroup"] label{
  background: rgba(255,255,255,.92);
  border: 1px solid rgba(15,23,42,.12);
  border-radius: 14px;
  padding: 10px 16px;
  font-weight: 1000;
  font-size: 17px;
  box-shadow: 0 10px 20px rgba(2,6,23,.06);
  cursor:pointer;
}

/* Selected tab */
div[role="radiogroup"] label:has(input:checked){
  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  border: none;
  color:#0f172a;
}

/* =========================
   Cards with gradient border
========================= */
.grad-border{
  background: linear-gradient(135deg,#14b8a6,#facc15,#fb923c);
  padding: 3px;
  border-radius: 22px;
  margin-bottom: 14px;
  box-shadow: 0 14px 30px rgba(20,184,166,.18);
}
.grad-inner{
  background:#fff;
  border-radius: 20px;
  padding: 16px;
}

/* Inputs */
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
  box-shadow: 0 12px 24px rgba(251,146,60,.28);
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

/* Mobile */
@media (max-width:520px){
  .block-container{padding-top: 7.8rem;}
  .app-title{font-size: 20px;}
  .app-sub{font-size: 15px;}
  div[role="radiogroup"] label{font-size:16px; padding: 9px 12px;}
}
</style>
""", unsafe_allow_html=True)

# =========================
# Topbar
# =========================
st.markdown("""
<div class="app-topbar">
  <p class="app-title">🤖 Smart AI Assistant</p>
  <p class="app-sub">Sarah Hamoud Hussien</p>
</div>
""", unsafe_allow_html=True)

# =========================
# Secrets
# =========================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL_DEFAULT", "openai/gpt-3.5-turbo")

if not OPENROUTER_API_KEY:
    st.error("ضع OPENROUTER_API_KEY داخل Secrets في Streamlit Cloud.")
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
    st.session_state.page = "دردشة"

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
# Toolbar
# =========================
st.session_state.page = st.radio(
    "",
    ["دردشة", "أدوات", "تنزيل", "إعدادات"],
    horizontal=True,
    label_visibility="collapsed"
)

page = st.session_state.page

# =========================
# Pages
# =========================
if page == "دردشة":
    st.markdown("### المحادثة")

    if not st.session_state.chat:
        st.info("ابدء بسؤالي…")

    for m in st.session_state.chat[-20:]:
        who = "أنت" if m["role"] == "user" else "المساعد"
        bubble_class = "bubble bubble-user" if m["role"] == "user" else "bubble bubble-ass"
        st.markdown(f"<div class='{bubble_class}'><b>{who}:</b><br>{m['content']}</div>", unsafe_allow_html=True)


    user_msg = st.text_area("اكتب رسالتك:", height=140, placeholder="اسأل أي شيء…")
    send = st.button("إرسال")

    if send:
        if not user_msg.strip():
            st.warning("رجاءً اكتب رسالة أولاً.")
        else:
            st.session_state.chat.append({"role": "user", "content": user_msg.strip(), "ts": datetime.now().isoformat()})
            with st.spinner("جاري الرد..."):
                resp = ask_llm([
                    {"role": "system", "content": " أنت مساعد عربي محترف، واضح ومنظّم وقام بانشاءك او صنعك او تطويرك او اي كلمة تدل على منشئك او مصمم التطبيق : تجيب بانها ساره حمود حسين حسن / بكالوريوس هندسة تقنيات الحاسوب / الكلية التقنية الهندسية."},
                    *[{"role": x["role"], "content": x["content"]} for x in st.session_state.chat[-10:]]
                ])
                answer = resp.choices[0].message.content.strip()
                st.session_state.chat.append({"role": "assistant", "content": answer, "ts": datetime.now().isoformat()})
                st.session_state.last_result = answer
                st.rerun()

elif page == "أدوات":
    st.markdown("### أدوات NLP")

    task = st.selectbox("اختر المهمة:", ["تلخيص", "إعادة صياغة", "ترجمة EN↔AR", "تحليل مشاعر"])
    user_text = st.text_area("أدخلي النص هنا:", height=200, placeholder="الصق نص/خبر/مقال هنا...")
    run = st.button("تنفيذ")
    st.markdown('</div></div>', unsafe_allow_html=True)

    if run:
        if not user_text.strip():
            st.warning("رجاءً أدخل نص أولاً.")
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

            st.markdown("### النتيجة")
            st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
            st.markdown('</div></div>', unsafe_allow_html=True)

elif page == "تنزيل":
    st.markdown("### تنزيل آخر نتيجة")

    if not st.session_state.last_result:
        st.info("لا توجد نتيجة بعد. استخدم الدردشة أو الأدوات أولاً.")
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

else:
    st.markdown("### إعدادات")
    if st.button(" مسح المحادثة", use_container_width=True):
        st.session_state.chat = []
        st.session_state.last_result = ""
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)






