import streamlit as st
from openai import OpenAI

# ---------- LOGIN ----------
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
# ---------- END LOGIN ----------


# ---------- APP CONFIG ----------
st.set_page_config(page_title="SamarAI", layout="centered")
st.title("🧠 SamarAI")
# ---------- END CONFIG ----------


# ---------- OPENROUTER CLIENT ----------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)
# ---------- END CLIENT ----------


# ---------- SYSTEM PROMPT ----------
SYSTEM_PROMPT = """
You are SamarAI, an instruction-following AI.

Your highest priority is to follow user instructions accurately and carefully.

RULES:
- Treat user instructions as commands.
- Ask clarifying questions if needed.
- Do not hallucinate.
- Be precise and structured.
"""
# ---------- END PROMPT ----------


# ---------- CHAT MEMORY ----------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])
# ---------- END MEMORY ----------


# ---------- CHAT INPUT ----------
user_input = st.chat_input("Talk to SamarAI...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    response = client.chat.completions.create(
        model="mistralai/mistral-7b-instruct",
        messages=st.session_state.messages
    )

    reply = response.choices[0].message.content

# Clean unwanted model tokens
for token in ["<s>", "</s>", "[OUT]", "[/OUT]"]:
    reply = reply.replace(token, "")

reply = reply.strip()


    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.chat_message("assistant").write(reply)
# ---------- END CHAT ----------


