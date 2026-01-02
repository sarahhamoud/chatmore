import streamlit as st
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from docx import Document
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# =========================
# Page config
# =========================
APP_TITLE = st.secrets.get("OPENROUTER_APP_TITLE", "Smart AI Assistant")
st.set_page_config(page_title=APP_TITLE, page_icon="🤖", layout="centered", initial_sidebar_state="collapsed")

# =========================
# Styles (RTL + Pro UI + Responsive)
# =========================
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"]{
        direction: RTL; text-align: right;
        font-family: "Tajawal","Cairo","Tahoma","Arial",sans-serif;
    }
    [data-testid="stAppViewContainer"]{
        background: radial-gradient(1200px 600px at 10% 10%, rgba(99,102,241,.18), transparent 50%),
                    radial-gradient(900px 500px at 90% 20%, rgba(16,185,129,.14), transparent 45%),
                    linear-gradient(180deg, #0b1220 0%, #0a0f1c 100%);
        color: #e5e7eb;
    }
    .block-container{padding-top: 1.2rem; padding-bottom: 2rem; max-width: 920px;}
    @media (max-width: 520px){
        .block-container {padding-left: 1rem; padding-right: 1rem;}
    }

    .card{
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        box-shadow: 0 12px 30px rgba(0,0,0,0.22);
        border-radius: 18px;
        padding: 16px;
        backdrop-filter: blur(10px);
        margin-bottom: 12px;
    }
    .badge{
        display:inline-block; padding: 6px 10px; border-radius: 999px;
        background: rgba(99,102,241,0.20);
        border: 1px solid rgba(99,102,241,0.35);
        font-size: 12px; color: #c7d2fe;
    }
    .stButton > button{
        width: 100%;
        border-radius: 14px;
        padding: 0.75rem 1rem;
        font-weight: 800;
        border: 1px solid rgba(255,255,255,0.18);
        background: linear-gradient(135deg, rgba(99,102,241,0.95), rgba(16,185,129,0.92));
        color: white;
    }
    textarea, input, [data-baseweb="select"] > div{
        border-radius: 14px !important;
        background: rgba(255,255,255,0.06) !important;
        border: 1px solid rgba(255,255,255,0.14) !important;
        color: #e5e7eb !important;
    }
    label {color:#e5e7eb !important; font-weight: 700;}

    /* Chat bubbles */
    .chat-wrap{margin-top: 8px;}
    .bubble{
        padding: 12px 12px;
        border-radius: 16px;
        margin: 8px 0;
        line-height: 1.85;
        border: 1px solid rgba(255,255,255,0.12);
        white-space: pre-wrap;
        word-break: break-word;
    }
    .user{
        background: rgba(99,102,241,0.18);
        border-color: rgba(99,102,241,0.35);
    }
    .bot{
        background: rgba(16,185,129,0.14);
        border-color: rgba(16,185,129,0.28);
    }
    .meta{
        opacity: .85;
        font-size: 12px;
        margin-top: 4px;
    }

    .result{
        background: rgba(17,24,39,0.65);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 16px;
        padding: 12px;
        white-space: pre-wrap;
        line-height: 1.9;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Secrets / Client (safe)
# =========================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
MODEL_DEFAULT = st.secrets.get("OPENROUTER_MODEL_DEFAULT", "openai/gpt-3.5-turbo")

if not OPENROUTER_API_KEY:
    st.error("⚠️ لم يتم العثور على OPENROUTER_API_KEY داخل Secrets. ضعيه في Streamlit Cloud → Settings → Secrets.")
    st.stop()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# =========================
# Helpers: clipboard, export
# =========================
def clipboard_button(text: str, label: str = "📋 نسخ"):
    """Copy-to-clipboard using a tiny HTML/JS snippet."""
    safe = text.replace("\\", "\\\\").replace("`", "\\`")
    st.components.v1.html(
        f"""
        <div style="display:flex; gap:10px;">
            <button
              style="
                width:100%;
                border-radius:14px;
                padding:12px 14px;
                font-weight:800;
                border:1px solid rgba(255,255,255,0.18);
                background:rgba(255,255,255,0.06);
                color:#e5e7eb;
                cursor:pointer;
              "
              onclick="navigator.clipboard.writeText(`{safe}`); this.innerText='✅ تم النسخ'; setTimeout(()=>this.innerText='{label}',1500);"
            >{label}</button>
        </div>
        """,
        height=60
    )

def make_docx(title: str, content: str) -> BytesIO:
    doc = Document()
    doc.add_heading(title, level=1)
    for para in content.split("\n"):
        doc.add_paragraph(para)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def make_pdf(title: str, content: str) -> BytesIO:
    """
    PDF بسيط. ملاحظة: دعم العربية في PDF يحتاج خط عربي.
    إذا ما توفر خط عربي، راح يطلع PDF لكن احتمال العربي ما يظهر مضبوط في بعض البيئات.
    """
    bio = BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    width, height = A4

    # Try register Arabic font if exists (optional)
    # You can add a font file later to repo and enable it.
    # Example: put "fonts/Amiri-Regular.ttf" then uncomment below:
    # pdfmetrics.registerFont(TTFont("Amiri", "fonts/Amiri-Regular.ttf"))
    # c.setFont("Amiri", 14)

    c.setFont("Helvetica", 14)
    y = height - 60
    c.drawString(40, y, title[:90])
    y -= 28
    c.setFont("Helvetica", 11)

    # Wrap lines
    max_chars = 95
    lines = []
    for line in content.split("\n"):
        line = line.strip()
        if not line:
            lines.append("")
            continue
        while len(line) > max_chars:
            lines.append(line[:max_chars])
            line = line[max_chars:]
        lines.append(line)

    for line in lines:
        if y < 60:
            c.showPage()
            c.setFont("Helvetica", 11)
            y = height - 60
        c.drawString(40, y, line[:120])
        y -= 16

    c.save()
    bio.seek(0)
    return bio

def build_prompt(task_name: str, text: str) -> str:
    if task_name == "تلخيص":
        return f"لخّص النص التالي بالعربية بشكل واضح ومنظم (نقاط + خلاصة):\n\n{text}"
    if task_name == "إعادة صياغة":
        return f"أعد صياغة النص التالي بالعربية بأسلوب احترافي وسلس مع الحفاظ على المعنى:\n\n{text}"
    if task_name == "ترجمة EN↔AR":
        return f"ترجم النص التالي (إنجليزي↔عربي) مع الحفاظ على المعنى والسياق وبأسلوب طبيعي:\n\n{text}"
    if task_name == "تحليل مشاعر":
        return f"حلل المشاعر في النص التالي (إيجابي/سلبي/محايد) واذكر السبب باختصار:\n\n{text}"
    return text

# =========================
# Session state
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []  # list of dicts: {role, content, ts}
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# =========================
# Header
# =========================
c1, c2 = st.columns([1, 3], vertical_alignment="center")
with c1:
    st.image(
        "https://raw.githubusercontent.com/streamlit/example-app-chatbot/main/icon.png",
        use_container_width=True
    )
with c2:
    st.markdown(f"## 🤖 {APP_TITLE}")
    st.markdown("<span class='badge'>Chatbot + تلخيص + صياغة + ترجمة + مشاعر + تحميل PDF/Word</span>", unsafe_allow_html=True)

# =========================
# Sidebar settings
# =========================
with st.sidebar:
    st.markdown("### ⚙️ إعدادات")
    model = st.selectbox(
        "النموذج (OpenRouter):",
        [
            MODEL_DEFAULT,
            "openai/gpt-4o-mini",
            "openai/gpt-4.1-mini",
            "anthropic/claude-3.5-sonnet",
            "google/gemini-1.5-pro",
            "meta-llama/llama-3.1-70b-instruct",
        ],
        index=0
    )
    temperature = st.slider("🎛️ الإبداع", 0.0, 1.0, 0.2, 0.1)
    max_tokens = st.slider("🔢 طول الرد", 200, 1800, 600, 50)

    if st.button("🧹 مسح المحادثة"):
        st.session_state.chat = []
        st.session_state.last_result = ""
        st.rerun()

# =========================
# Main: Chat + Tools
# =========================
st.markdown("<div class='card'>", unsafe_allow_html=True)

mode = st.radio("اختاري الوضع:", ["💬 Chatbot محادثة", "🧠 أدوات NLP"], horizontal=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---------- CHATBOT MODE ----------
if mode == "💬 Chatbot محادثة":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 💬 المحادثة")

    # Render chat
    st.markdown("<div class='chat-wrap'>", unsafe_allow_html=True)
    for msg in st.session_state.chat[-30:]:
        role = msg["role"]
        cls = "user" if role == "user" else "bot"
        who = "أنتِ" if role == "user" else "المساعد"
        st.markdown(
            f"""
            <div class="bubble {cls}">
                {msg["content"]}
                <div class="meta">{who} • {msg["ts"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("</div>", unsafe_allow_html=True)

    user_msg = st.text_area("✍️ اكتب/ي رسالتك:", height=120, placeholder="اسأليني أي شيء…")
    send = st.button("🚀 إرسال")

    st.markdown("</div>", unsafe_allow_html=True)

    if send:
        if not user_msg.strip():
            st.warning("رجاءً اكتبي رسالة أولاً ✍️")
        else:
            st.session_state.chat.append({"role": "user", "content": user_msg.strip(), "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})

            with st.spinner("⏳ جاري الرد..."):
                try:
                    messages = [{"role": "system", "content": "أنت مساعد عربي محترف، واضح ومختصر ومفيد."}]
                    # Include last context (limited)
                    for m in st.session_state.chat[-12:]:
                        messages.append({"role": m["role"], "content": m["content"]})

                    resp = client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    answer = resp.choices[0].message.content.strip()
                    st.session_state.chat.append({"role": "assistant", "content": answer, "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    st.session_state.last_result = answer
                    st.rerun()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

    # Actions for last result
    if st.session_state.last_result:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("### 🧾 آخر رد")
        st.markdown(f"<div class='result'>{st.session_state.last_result}</div>", unsafe_allow_html=True)

        colA, colB, colC = st.columns(3)
        with colA:
            clipboard_button(st.session_state.last_result, "📋 نسخ الرد")
        with colB:
            pdf_bytes = make_pdf("Smart AI Assistant — Result", st.session_state.last_result)
            st.download_button("⬇️ تحميل PDF", data=pdf_bytes, file_name="result.pdf", mime="application/pdf", use_container_width=True)
        with colC:
            docx_bytes = make_docx("Smart AI Assistant — Result", st.session_state.last_result)
            st.download_button("⬇️ تحميل Word", data=docx_bytes, file_name="result.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ---------- NLP TOOLS MODE ----------
else:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### 🧠 أدوات NLP")

    task = st.selectbox("اختاري المهمة:", ["تلخيص", "إعادة صياغة", "ترجمة EN↔AR", "تحليل مشاعر"])
    user_text = st.text_area("📄 أدخلي النص هنا:", height=180, placeholder="الصقي نص/خبر/مقال هنا...")
    run = st.button("🚀 تنفيذ المهمة")

    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not user_text.strip():
            st.warning("رجاءً أدخلي نص أولاً ✍️")
        else:
            prompt = build_prompt(task, user_text.strip())

            with st.spinner("⏳ جاري المعالجة..."):
                try:
                    resp = client.chat.completions.create(
                        model=model,
                        messages=[
                            {"role": "system", "content": "أنت مساعد عربي محترف. كن واضحاً ومنظماً."},
                            {"role": "user", "content": prompt},
                        ],
                        temperature=temperature,
                        max_tokens=max_tokens,
                    )
                    result = resp.choices[0].message.content.strip()
                    st.session_state.last_result = result

                    st.markdown("<div class='card'>", unsafe_allow_html=True)
                    st.markdown("### ✅ النتيجة")
                    st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)

                    colA, colB, colC = st.columns(3)
                    with colA:
                        clipboard_button(result, "📋 نسخ النتيجة")
                    with colB:
                        pdf_bytes = make_pdf("Smart AI Assistant — Result", result)
                        st.download_button("⬇️ تحميل PDF", data=pdf_bytes, file_name="result.pdf", mime="application/pdf", use_container_width=True)
                    with colC:
                        docx_bytes = make_docx("Smart AI Assistant — Result", result)
                        st.download_button("⬇️ تحميل Word", data=docx_bytes, file_name="result.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

st.markdown("---")
st.caption("💡 ملاحظة: إذا تريدين PDF عربي مضبوط 100%، أضيف لك خط عربي داخل المشروع (Amiri) ونفعّله بالكود.")
