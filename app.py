import streamlit as st
from google import genai

# Muonekano wa ukurasa
st.set_page_config(page_title="HITECH AI", page_icon="🤖")
st.title("🤖 HITECH AI WANGU")

# Kuchukua API Key kwa usalama kutoka mfumo wa Streamlit
api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Tafadhali weka GEMINI_API_KEY kwenye mfumo wa Streamlit.")
    st.stop()

client = genai.Client(api_key=api_key)

# Kuhifadhi kumbukumbu ya majadiliano (Memory)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Kuonyesha majadiliano yaliyopita
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Sehemu ya mtumiaji kuandika ujumbe
if prompt := st.chat_input("Andika ujumbe wako hapa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Kupata jibu kutoka kwa AI
    with st.chat_message("assistant"):
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
            config={
                "system_instruction": "Wewe ni HITECH AI, msaidizi wa kidijitali mwenye akili sana, mchangamfu, na unayejibu kwa Kiswahili fasaha, kirafiki na kwa ufasaha wa hali ya juu."
            }
        )
        st.markdown(response.text)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
