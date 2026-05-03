from dotenv import load_dotenv
from groq import Groq
import streamlit as st
import os

load_dotenv()
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    api_key = os.getenv("GROQ_API_KEY")

client = Groq(api_key=api_key)

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
                response = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}]
                )
                progress.progress(100, text="Done!")
                progress.empty()
                response_text = response.choices[0].message.content
                if "FAKE" in response_text:
                    st.error("🔍 VERDICT: FAKE")
                elif "REAL" in response_text:
                    st.success("🔍 VERDICT: REAL")
                elif "MISLEADING" in response_text:
                    st.warning("🔍 VERDICT: MISLEADING")
                else:
                    st.info("🔍 VERDICT: UNVERIFIED")

                col1, col2 = st.columns(2)
                col3, col4 = st.columns(2)

                def extract(key):
                    for line in response_text.split("\n"):
                        if key in line:
                            return line.split(":", 1)[-1].strip()
                    return ""

                with col1:
                    st.markdown("**📊 CONFIDENCE LEVEL**")
                    st.write(extract("CONFIDENCE LEVEL"))

                with col2:
                    st.markdown("**📝 REASON**")
                    st.write(extract("REASON"))

                with col3:
                    st.markdown("**🚩 RED FLAGS**")
                    st.write(extract("RED FLAGS"))

                with col4:
                    st.markdown("**✅ SUGGESTION**")
                    st.write(extract("SUGGESTION"))
                            
            except Exception as e:
                progress.empty()
                if "429" in str(e) or "quota" in str(e).lower() or "ResourceExhausted" in str(e):
                    st.error("⏳ Too many requests — please wait a minute and try again!")
                else:
                    st.error(f"❌ Something went wrong: {str(e)}")
    else:
        st.error("Please Enter a text first.")