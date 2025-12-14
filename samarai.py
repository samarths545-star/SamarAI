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
You are SamarAI, an AI assistant with internet access.

MANDATORY RULES:
- If internet search results are provided, you MUST use them.
- Never say you do not have internet access.
- Never give generic or outdated answers when web data is present.
- Answer clearly in plain text.
- Be factual, direct, and concise.
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


# ---------------- INTERNET SEARCH (TAVILY) ----------------
def internet_search(query):
    response = requests.post(
        "https://api.tavily.com/search",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "api_key": st.secrets["TAVILY_API_KEY"],
            "query": query,
            "search_depth": "basic",
            "max_results": 5,
        },
        timeout=30,
    )

    data = response.json()

    results_text = ""
    for item in data.get("results", []):
        results_text += f"- {item.get('title')}: {item.get('content')}\n"

    return results_text
# ---------------- END SEARCH ----------------


# ---------------- CHAT INPUT ----------------
user_input = st.chat_input("Ask SamarAI anything...")

if user_input:
    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # Decide if internet search is needed
    needs_internet = any(
        word in user_input.lower()
        for word in [
            "latest", "current", "today", "now",
            "news", "price", "time", "update"
        ]
    )

    web_context = ""
    if needs_internet:
        web_context = internet_search(user_input)

    try:
        # FORCE usage of web results
        messages = st.session_state.messages.copy()

        if web_context:
            messages.append({
                "role": "user",
                "content": (
                    "The following information was retrieved from the internet "
                    "and is current. You MUST use it to answer the question.\n\n"
                    f"{web_context}"
                )
            })

        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY']}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/mistral-7b-instruct",
                "messages": messages,
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
