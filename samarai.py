import streamlit as st

# ---------- LOGIN SCREEN ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔐 SamarAI Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if (
            username == st.secrets["APP_USERNAME"]
            and password == st.secrets["APP_PASSWORD"]
        ):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.stop()
# ---------- END LOGIN SCREEN ----------
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="SamarAI", layout="centered")

st.title("🧠 SamarAI")

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)

SYSTEM_PROMPT = """
You are SamarAI — a universal, multi-purpose AI assistant.

You can:
- Answer general knowledge questions
- Do deep reasoning
- Help with legal, business, and technical topics
- Write, summarize, explain, and analyze content

Rules:
- If you do not know something, say so clearly.
- Do not hallucinate facts.
- Be structured and accurate.
- Adapt tone based on the task.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])

user_input = st.chat_input("Ask SamarAI anything...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.chat_message("user").write(user_input)

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message.content
    st.session_state.messages.append({"role": "assistant", "content": reply})
    st.chat_message("assistant").write(reply)

