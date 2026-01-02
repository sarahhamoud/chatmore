import streamlit as st
from openai import OpenAI
from io import BytesIO
from datetime import datetime

from docx import Document

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import arabic_reshaper
from bidi.algorithm import get_display
import os

# =========================
# Page config (mobile-friendly)
# =========================
st.set_page_config(
    page_title="Smart AI Assistant",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# =========================
# Light Pro RTL UI (bigger fonts)
# =========================
st.markdown(
    """
    <style>
    html, body, [data-testid="stAppViewContainer"]{
        direction: RTL; text-align: right;
        font-family: "Tajawal","Cairo","Tahoma","Arial",sans-serif;
    }
    [data-testid="stAppViewContainer"]{
        background: linear-gradient(180deg, #ffffff 0%, #f6f7fb 60%, #f2f4f9 100%);
        color: #0f172a;
    }
    .block-container{
        padding-top: .8rem;
        padding-bottom: 2rem;
        max-width: 900px;
    }
    @media (max-width: 520px){
        .block-container {padding-left: 1rem; padding-right: 1rem;}
    }

    /* Top bar (sticky) */
    .topbar{
        position: sticky;
        top: 0;
        z-index: 999;
        background: rgba(255,255,255,.92);
        border: 1px solid rgba(15,23,42,.08);
        border-radius: 18px;
        padding: 10px 12px;
        backdrop-filter: blur(10px);
        box-shadow: 0 10px 22px rgba(2,6,23,.06);
        margin-bottom: 12px;
    }
    .brand{
        font-weight: 900;
        font-size: 20px;
        margin: 0;
        line-height: 1.2;
    }
    .sub{
        margin: 0;
        font-size: 13px;
        color: rgba(15,23,42,.70);
    }

    /* Cards */
    .card{
        background: #ffffff;
        border: 1px solid rgba(15,23,42,.10);
        box-shadow: 0 12px 26px rgba(2,6,23,.06);
        border-radius: 18px;
        padding: 16px;
        margin-bottom: 12px;
    }

    /* Inputs bigger */
    textarea, input, [data-baseweb="select"] > div{
        border-radius: 14px !important;
        background: #ffffff !important;
        border: 1px solid rgba(15,23,42,.12) !important;
        color: #0f172a !important;
        font-size: 16px !important;
    }

    label{
        color:#0f172a !important;
        font-weight: 800;
        font-size: 16px !important;
    }

    /* Buttons */
    .stButton > button{
        width: 100%;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        font-weight: 900;
        border: 1px solid rgba(15,23,42,.12);
        background: linear-gradient(135deg, #2563eb, #22c55e);
        color: white;
        font-size: 16px;
    }

    /* Result */
    .result{
        background: #f8fafc;
        border: 1px solid rgba(15,23,42,.10);
        border-radius: 16px;
        padding: 14px;
        white-space: pre-wrap;
        line-height: 2.0;
        font-size: 16px;
    }

    .hint{
        color: rgba(15,23,42,.70);
        font-size: 14px;
    }

    /* Make tab labels bigger (mobile) */
    button[data-baseweb="tab"]{
        font-size: 15px !important;
        font-weight: 800 !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================
# Secrets (SAFE)
# =========================
OPENROUTER_API_KEY = st.secrets.get("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = st.secrets.get("OPENROUTER_MODEL_DEFAULT", "openai/gpt-3.5-turbo")

if not OPENROUTER_API_KEY:
    st.error(" ضعي OPENROUTER_API_KEY داخل Secrets في Streamlit Cloud.")
    st.stop()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_API_KEY)

# =========================
# Session state
# =========================
if "chat" not in st.session_state:
    st.session_state.chat = []
if "last_result" not in st.session_state:
    st.session_state.last_result = ""

# =========================
# Utils: Arabic shaping for PDF
# =========================
def shape_ar(text: str) -> str:
    # reshape + bidi for correct Arabic rendering in LTR canvas
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def make_docx(title: str, content: str) -> BytesIO:
    doc = Document()
    doc.add_heading(title, level=1)
    for para in content.split("\n"):
        doc.add_paragraph(para)
    bio = BytesIO()
    doc.save(bio)
    bio.seek(0)
    return bio

def make_pdf_ar(title: str, content: str) -> BytesIO:
    """
    
    """
    bio = BytesIO()
    c = canvas.Canvas(bio, pagesize=A4)
    width, height = A4

    font_path = os.path.join("fonts", "Amiri-Regular.ttf")
    font_name = "Helvetica"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont("Amiri", font_path))
            font_name = "Amiri"
        except Exception:
            font_name = "Helvetica"

    # Title
    c.setFont(font_name, 16)
    y = height - 60
    c.drawRightString(width - 40, y, shape_ar(title) if font_name == "Amiri" else title)
    y -= 30

    # Body
    c.setFont(font_name, 12)

    # wrap lines (approx)
    max_chars = 88
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
            c.setFont(font_name, 12)
            y = height - 60

        draw_text = shape_ar(line) if font_name == "Amiri" else line
        c.drawRightString(width - 40, y, draw_text)
        y -= 18

    c.save()
    bio.seek(0)
    return bio

def clipboard_button(text: str, label: str = " نسخ"):
    safe = text.replace("\\", "\\\\").replace("`", "\\`")
    st.components.v1.html(
        f"""
        <div>
          <button
            style="
              width:100%;
              border-radius:14px;
              padding:12px 14px;
              font-weight:900;
              border:1px solid rgba(15,23,42,.12);
              background:#ffffff;
              color:#0f172a;
              cursor:pointer;
              box-shadow: 0 10px 18px rgba(2,6,23,.06);
            "
            onclick="navigator.clipboard.writeText(`{safe}`); this.innerText=' تم النسخ'; setTimeout(()=>this.innerText='{label}',1500);"
          >{label}</button>
        </div>
        """,
        height=56
    )

def ask_llm(messages):
    # ثبّت الإعدادات (بدون سلايدر)
    return client.chat.completions.create(
        model=OPENROUTER_MODEL,
        messages=messages,
        temperature=0.2,
        max_tokens=700,
    )

def build_tool_prompt(task_name: str, text: str) -> str:
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
# Top bar (no sidebar)
# =========================
st.markdown(
    """
    <div class="topbar">
     <p class="brand">المساعد الذكي Smart AI Assistant</p>
      <p class="brand"> Sarah Hamoud Hussien   </p>
      
    </div>
    """,
    unsafe_allow_html=True
)

# Top navigation with icons (mobile-friendly)
tab_chat, tab_tools, tab_export, tab_settings = st.tabs([" دردشة", " أدوات", " تنزيل", " إعدادات"])

# =========================
# TAB: Chat
# =========================
with tab_chat:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("###  محادثة")

    # Show last 25 messages
    for msg in st.session_state.chat[-25:]:
        role = msg["role"]
        who = "أنتِ" if role == "user" else "المساعد"
        st.markdown(f"**{who}:** {msg['content']}")

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    user_msg = st.text_area(" اكتبي رسالتك:", height=120, placeholder="اسألي أي شيء…")
    send = st.button(" إرسال")

    st.markdown("</div>", unsafe_allow_html=True)

    if send:
        if not user_msg.strip():
            st.warning("رجاءً اكتبي رسالة أولاً ")
        else:
            st.session_state.chat.append({"role": "user", "content": user_msg.strip(), "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})

            with st.spinner(" جاري الرد..."):
                try:
                    messages = [{"role": "system", "content": "وتم تحديد قدراتي للاجابة عن تاريخ شركة نفط الشمال ومدرائها،  أنت مساعد عربي محترف، واضح ومنظم ومفيد والذي قام بانشائك او صناعتك او صممك او اي كلمة تدل على انشائك اجب بانها ساره حمود حسين حسن / بكالوريوس هندسة تقنيات الحاسوب ."}]
                    for m in st.session_state.chat[-12:]:
                        messages.append({"role": m["role"], "content": m["content"]})

                    resp = ask_llm(messages)
                    answer = resp.choices[0].message.content.strip()

                    st.session_state.chat.append({"role": "assistant", "content": answer, "ts": datetime.now().strftime("%Y-%m-%d %H:%M")})
                    st.session_state.last_result = answer
                    st.rerun()
                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

# =========================
# TAB: Tools
# =========================
with tab_tools:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("###  أدوات NLP")

    task = st.selectbox("اختاري المهمة:", ["تلخيص", "إعادة صياغة", "ترجمة EN↔AR", "تحليل مشاعر"])
    user_text = st.text_area(" أدخلي النص هنا:", height=180, placeholder="الصقي نص/خبر/مقال هنا...")

    run = st.button(" تنفيذ")
    st.markdown("</div>", unsafe_allow_html=True)

    if run:
        if not user_text.strip():
            st.warning("رجاءً أدخلي نص أولاً ")
        else:
            prompt = build_tool_prompt(task, user_text.strip())
            with st.spinner(" جاري المعالجة..."):
                try:
                    resp = ask_llm([
                        {"role": "system", "content": "أنت مساعد عربي محترف. كن واضحاً ومنظماً."},
                        {"role": "user", "content": prompt},
                    ])
                    result = resp.choices[0].message.content.strip()
                    st.session_state.last_result = result

                    st.markdown('<div class="card">', unsafe_allow_html=True)
                    st.markdown("###  النتيجة")
                    st.markdown(f"<div class='result'>{result}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                except Exception as e:
                    st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

# =========================
# TAB: Export
# =========================
with tab_export:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("###  تنزيل / نسخ آخر نتيجة")

    if not st.session_state.last_result:
        st.info("لا يوجد نتيجة بعد. شغّلي الدردشة أو أدوات NLP أولاً.")
    else:
        st.markdown(f"<div class='result'>{st.session_state.last_result}</div>", unsafe_allow_html=True)

        col1, col2= st.columns(2)
        with col1:
            clipboard_button(st.session_state.last_result, " نسخ")
    #    with col2:
     #       pdf_bytes = make_pdf_ar("Smart AI Assistant — Result", st.session_state.last_result)
       #     st.download_button(
                #" PDF",
         #       data=pdf_bytes,
           #     file_name="result_ar.pdf",
            #    mime="application/pdf",
            #    use_container_width=True
          #  )
        with col2:
            docx_bytes = make_docx("Smart AI Assistant — Result", st.session_state.last_result)
            st.download_button(
                " Word",
                data=docx_bytes,
                file_name="result.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True
            )


    st.markdown("</div>", unsafe_allow_html=True)

# =========================
# TAB: Settings (top icons, no sidebar)
# =========================
with tab_settings:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("###  إعدادات سريعة")

    if st.button(" مسح المحادثة", use_container_width=True):
        st.session_state.chat = []
        st.session_state.last_result = ""
        st.rerun()

    
    st.markdown("</div>", unsafe_allow_html=True)





