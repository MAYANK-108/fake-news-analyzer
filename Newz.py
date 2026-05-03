from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st
import os

load_dotenv()
try:
    api_key = st.secrets["API_KEY"]
except:
    api_key = os.getenv("API_KEY")

genai.configure(api_key=api_key)

generation_config = {"temperature": 0.9, "top_p": 1, "top_k": 1, "max_output_tokens": 2048 }
model = genai.GenerativeModel("gemini-2.0-flash-lite", generation_config=generation_config)

st.title("Fake News Analyzer")
st.text("Paste any news headline, paragraph or article to verify its authenticity")

news = st.text_area("Enter Here")

if st.button("Analyze"):
    if news:
        with st.spinner("Analyzing..."):
            prompt = f"""
You are a professional fact-checker and news analyst.
Analyze the following news/text and respond ONLY in this format:

🔍 VERDICT: [REAL / FAKE / MISLEADING / UNVERIFIED]
📊 CONFIDENCE LEVEL: [0-100%]
📝 REASON: [2-3 lines explaining why]
🚩 RED FLAGS: [List any suspicious claims, missing sources, emotional language]
✅ SUGGESTION: [What should the reader do — verify from where?]

News to analyze:
{news}
"""
            progress = st.progress(0, text="Analyzing news...")
            progress.progress(25, text="Reading article...")
            progress.progress(50, text="Checking facts...")
            progress.progress(75, text="Generating verdict...")
            try:
                response = model.generate_content([prompt])
                progress.progress(100, text="Done!")
                progress.empty()
                response_text = response.text
                if "FAKE" in response_text:
                    st.error("🔍 VERDICT: FAKE")
                elif "REAL" in response_text:
                    st.success("🔍 VERDICT: REAL")
                elif "MISLEADING" in response_text:
                    st.warning("🔍 VERDICT: MISLEADING")
                else:
                    st.info("🔍 VERDICT: UNVERIFIED")
                sections = {
                    "📊 CONFIDENCE LEVEL": "CONFIDENCE LEVEL",
                    "📝 REASON": "REASON",
                    "🚩 RED FLAGS": "RED FLAGS",
                    "✅ SUGGESTION": "SUGGESTION"
                }
                for label, key in sections.items():
                    for line in response_text.split("\n"):
                        if key in line:
                            st.markdown(f"**{label}**")
                            st.write(line.split(":", 1)[-1].strip())
                            st.divider()
            except Exception as e:
                progress.empty()
                if "429" in str(e) or "quota" in str(e).lower() or "ResourceExhausted" in str(e):
                    st.error("⏳ Too many requests — please wait a minute and try again!")
                else:
                    st.error(f"❌ Something went wrong: {str(e)}")
    else:
        st.error("Please Enter a text first.")