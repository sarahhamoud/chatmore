import streamlit as st
from openai import OpenAI
import os

st.set_page_config(page_title=" Smart AI Assistant", layout="centered")
st.markdown(
    """
    <style>
    body, .stTextArea, .stTextInput, .stMarkdown, .stSelectbox, .stButton, .stText {
        direction: RTL;
        text-align: right;
        font-family: 'Tahoma', 'Arial', sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)


OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "YOUR_API_KEY")
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key='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',
)


st.title(" Smart AI Assistant — مساعد لغوي ذكي")
st.markdown(
    """
    هذا التطبيق يتيح لك تجربة مهام **معالجة اللغة الطبيعية (NLP)** عبر واجهة واحدة:

    -  **تلخيص النصوص**  
    -  **إعادة الصياغة**  
    -  **الترجمة EN ↔ AR**  
    -  **تحليل المشاعر**  

    *(مدعوم بواسطة OpenRouter API ونموذج gpt-3.5-turbo)*  
    """
)

task = st.selectbox(
    "اختر المهمة:",
    ["تلخيص", "إعادة صياغة", "ترجمة EN↔AR", "تحليل مشاعر"]
)

user_text = st.text_area(" أدخل النص هنا:", height=200)

if st.button(" تشغيل"):
    if not user_text.strip():
        st.warning("الرجاء إدخال نص أولاً")
    else:
        prompt_map = {
            "تلخيص": f"لخص النص التالي بالعربية:\n\n{user_text}",
            "إعادة صياغة": f"أعد صياغة النص التالي بالعربية:\n\n{user_text}",
            "ترجمة EN↔AR": f"ترجم النص التالي من الإنجليزية إلى العربية مع الحفاظ على المعنى والسياق، واحتفظ بالأسلوب الطبيعي:\n\n{user_text}",
            "تحليل مشاعر": f"حلل المشاعر في النص التالي (إيجابي/سلبي/محايد):\n\n{user_text}",
        }

        with st.spinner(" جاري المعالجة..."):
            try:
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt_map[task]}],
                )
                result = response.choices[0].message.content
                st.success(" النتيجة:")
                st.write(result)
            except Exception as e:
                st.error(f"حدث خطأ أثناء الاتصال بالنموذج: {e}")

st.markdown("---")
st.info(" نصيحة: جرّب نسخ نصوص من الأخبار أو مقالات طويلة لاختبار التلخيص!")
