import streamlit as st
from google import genai

st.set_page_config(page_title="HITECH AI", page_icon="🤖")
st.title("🤖 HITECH AI WANGU")

api_key = st.secrets.get("GEMINI_API_KEY")

if not api_key:
    st.error("Tafadhali weka GEMINI_API_KEY kwenye mfumo wa Streamlit.")
    st.stop()

@st.cache_resource
def get_client(api_key):
    return genai.Client(api_key=api_key)

client = get_client(api_key)

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Andika ujumbe wako hapa..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("⏳ HITECH AI inakifikiri..."):
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=prompt,
                    config={
                        "system_instruction": "Wewe ni HITECH AI, msaidizi wa kidijitali mwenye akili sana, mchangamfu, na unayejibu kwa Kiswahili fasaha, kirafiki na kwa ufasaha wa hali ya juu."
                    }
                )
            st.markdown(response.text)
            st.session_state.messages.append({"role": "assistant", "content": response.text})
        except Exception as e:
            st.error(f"❌ Hitilafu: {str(e)}")
