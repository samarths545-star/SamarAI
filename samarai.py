import streamlit as st
import requests

# ---------------- LOGIN ----------------
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


# ---------------- APP UI ----------------
st.set_page_config(page_title="SamarAI", layout="centered")
st.title("🧠 SamarAI")
# ---------------- END UI ----------------


# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are SamarAI, an instruction-following AI assistant.

Rules:
- Respond clearly in plain text
- No special tokens
- No system tags
- Follow user instructions accurately
- Be concise unless asked otherwise
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


# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Talk to SamarAI...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    try:
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
            timeout=30,
        )

        if response.status_code != 200:
            st.error(f"OpenRouter error: {response.text}")
            st.stop()

        reply = response.json()["choices"][0]["message"]["content"]

        # Clean unwanted tokens
        for token in ["<s>", "</s>", "[OUT]", "[/OUT]"]:
            reply = reply.replace(token, "")

        reply = reply.strip()

        st.session_state.messages.append(
            {"role": "assistant", "content": reply}
        )
        st.chat_message("assistant").write(reply)

    except Exception as e:
        st.error(f"Runtime error: {str(e)}")
# ---------------- END CHAT ----------------
