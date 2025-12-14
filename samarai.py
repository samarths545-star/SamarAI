import streamlit as st
import requests

# ---------------- LOGIN SCREEN ----------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.set_page_config(page_title="SamarAI Login", layout="centered")
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
# ---------------- END LOGIN ----------------


# ---------------- APP CONFIG ----------------
st.set_page_config(page_title="SamarAI", layout="centered")
st.title("🧠 SamarAI")
# ---------------- END CONFIG ----------------


# ---------------- OPENROUTER CLIENT ----------------
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=st.secrets["OPENROUTER_API_KEY"]
)
# ---------------- END CLIENT ----------------


# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are SamarAI, an instruction-following AI assistant.

Your highest priority is to follow user instructions accurately and carefully.

RULES YOU MUST FOLLOW:
1. Treat user instructions as commands, not suggestions.
2. Ask clarifying questions if instructions are unclear.
3. Follow instructions step by step.
4. Do NOT hallucinate facts or sources.
5. If something is not possible, say so clearly.
6. Adapt tone, format, and depth exactly as instructed.
7. Be precise, structured, and honest at all times.

DEFAULT BEHAVIOR:
- Clear text only
- No special tokens
- No system tags
- Professional and calm
"""
# ---------------- END PROMPT ----------------


# ---------------- CHAT MEMORY ----------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

for msg in st.session_state.messages[1:]:
    st.chat_message(msg["role"]).write(msg["content"])
# ---------------- END MEMORY ----------------


# ---------------- CHAT INPUT & RESPONSE ----------------
user_input = st.chat_input("Talk to SamarAI...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # Get AI response
    response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "mistralai/mistral-7b-instruct",
        "messages": st.session_state.messages,
    },
)

reply = response.json()["choices"][0]["message"]["content"]

    # Clean unwanted model tokens
    for token in ["<s>", "</s>", "[OUT]", "[/OUT]"]:
        reply = reply.replace(token, "")

    reply = reply.strip()

    # Show assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": reply}
    )
    st.chat_message("assistant").write(reply)
# ---------------- END CHAT ----------------

