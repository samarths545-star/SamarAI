import streamlit as st
import requests
import datetime
from zoneinfo import ZoneInfo

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
You are SamarAI, an AI assistant.

STRICT RULES:
- Never guess real-time facts.
- Use internet search only when explicitly needed.
- Use provided web results as the ONLY source when present.
- Never say you do not have internet access.
- Answer clearly in plain text.
- Be precise, factual, and calm.
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
    question = user_input.lower()

    # Show user message
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.chat_message("user").write(user_input)

    # -------- INTELLIGENT ROUTING --------

    # 1️⃣ Time questions → system clock (NO internet)
    is_time_question = any(
        phrase in question
        for phrase in ["current time", "what time", "time in"]
    )

    if is_time_question:
        try:
            if "new york" in question:
                now = datetime.datetime.now(ZoneInfo("America/New_York"))
                reply = f"The current time in New York is {now.strftime('%I:%M %p')} (Eastern Time)."
            else:
                reply = "Please specify the city or timezone."

            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
            st.chat_message("assistant").write(reply)
            st.stop()

        except Exception as e:
            st.error(str(e))
            st.stop()

    # 2️⃣ Price / news questions → internet search
    is_price_or_news = any(
        word in question
        for word in ["latest", "news", "price", "bitcoin", "stock", "update"]
    )

    web_context = ""
    if is_price_or_news:
        web_context = internet_search(user_input)

    # -------- AI RESPONSE --------
    try:
        messages = st.session_state.messages.copy()

        # FORCE use of web results when present
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
