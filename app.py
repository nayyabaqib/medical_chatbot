import streamlit as st
import requests
from datetime import datetime
from googletrans import Translator  # pip install googletrans==4.0.0-rc1

# --------- API Setup ---------
GROQ_API_KEY = "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"
API_URL = "https://api.groq.com/openai/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {GROQ_API_KEY}",
    "Content-Type": "application/json"
}

translator = Translator()

# --------- Streamlit Config ---------
st.set_page_config(page_title="Medical Chatbot with Appointments", layout="wide")
st.title(" AI Medical Chatbot")
st.markdown("Ask questions or book an appointment with a specialist.")

# --------- Sidebar Navigation ---------
st.sidebar.title("Navigation")
nav_option = st.sidebar.radio("Choose Option:", ["Chat with Bot", "Book Appointment"])

# --------- Chat History + Language Mode ---------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "language_mode" not in st.session_state:
    st.session_state.language_mode = "english"  # default

# --------- Helper Function: Roman Urdu ---------
def convert_to_roman_urdu(urdu_text):
    mapping = {
        "آپ": "Aap", "کیسے": "kaise", "ہیں": "hain", "میں": "mein", "ہوں": "hoon",
        "کیا": "kya", "ہے": "hai", "نہیں": "nahi", "ہاں": "haan", "جی": "jee",
        "ٹھیک": "theek", "شکریہ": "shukriya", "مجھے": "mujhe", "سر درد": "sirdard",
        "دل": "dil", "درد": "dard", "ہو": "ho", "رہا": "raha", "رہی": "rahi", "تکلیف": "takleef",
        "اسسٹنٹ": "assistant", "میرا": "mera", "نام": "naam", "نبی": "Nabi"
    }
    for urdu_word, roman_word in mapping.items():
        urdu_text = urdu_text.replace(urdu_word, roman_word)
    return urdu_text

# --------- 1. CHATBOT SECTION ---------
if nav_option == "Chat with Bot":
    st.subheader("🤖 Talk to a Medical Specialist")

    specialist = st.sidebar.selectbox("Specialist Type:", [
        "General Physician", "Gynae", "Cardiologist", "Dentist", "Child Specialist",
        "Dermatologist", "Eye Specialist", "Mental Health", "Nutritionist", "Orthopedic", "Physiotherapist"
    ])

    user_message = st.chat_input("Type your message here...")

    if user_message:
        st.chat_message("user").write(user_message)

        msg_lc = user_message.lower().strip()

        # ----------------- Language Switch -----------------
        if "urdu mein baat karo" in msg_lc:
            st.session_state.language_mode = "urdu"
            reply = "Theek hai, ab mein Urdu mein baat karunga."
        elif "roman urdu mein baat karo" in msg_lc:
            st.session_state.language_mode = "roman_urdu"
            reply = "Theek hai, ab mein Roman Urdu mein baat karunga."
        elif "english mein baat karo" in msg_lc:
            st.session_state.language_mode = "english"
            reply = "Okay, I will continue in English."
        # ----------------- Name Prompt -----------------
        elif msg_lc in [
            "tumhara naam kya hai", "aapka naam kya hai", "what is your name", "who are you", "ap ka name kya hai"
        ]:
            reply = "Mera naam Nabi Medical Assistant hai."
        # ----------------- Normal medical response -----------------
        else:
            prompt = f"You are Nabi Medical Assistant, a certified medical assistant specialized in {specialist}. User's message: {user_message}"

            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "system", "content": prompt}],
                "temperature": 0.5
            }

            try:
                with st.spinner("Thinking..."):
                    response = requests.post(API_URL, headers=headers, json=payload)
                    if response.status_code == 200:
                        reply = response.json()["choices"][0]["message"]["content"]
                    else:
                        reply = "⚠️ API Error"
            except Exception as e:
                reply = f"Error: {e}"

        # ----------------- Language Processing -----------------
        lang_mode = st.session_state.language_mode
        if lang_mode == "urdu":
            reply = translator.translate(reply, dest="ur").text
        elif lang_mode == "roman_urdu":
            reply = translator.translate(reply, dest="ur").text
            reply = convert_to_roman_urdu(reply)
        # english → no change

        st.chat_message("assistant").write(reply)
        st.session_state.chat_history.append(("user", user_message))
        st.session_state.chat_history.append(("assistant", reply))

    # 🔁 Only show previous chat if NO new message just now
    if not user_message:
        for role, msg in st.session_state.chat_history:
            st.chat_message(role).write(msg)

# --------- 2. APPOINTMENT SECTION ---------
elif nav_option == "Book Appointment":
    st.subheader("📅 Book a Doctor Appointment")

    with st.form("appointment_form"):
        name = st.text_input("Your Name")
        age = st.number_input("Your Age", min_value=1, max_value=120)
        contact = st.text_input("Phone or Email")
        doctor_type = st.selectbox("Select Specialist", [
            "General Physician", "Gynae", "Cardiologist", "Dentist", "Child Specialist",
            "Dermatologist", "Eye Specialist", "Mental Health", "Nutritionist", "Orthopedic", "Physiotherapist"
        ])
        date = st.date_input("Choose Appointment Date", min_value=datetime.today())
        time = st.time_input("Choose Time")
        submit = st.form_submit_button("Book Appointment")

    if submit:
        st.success("✅ Appointment Confirmed!")
        st.markdown(f"""
        **Name:** {name}  
        **Age:** {age}  
        **Contact:** {contact}  
        **Doctor:** {doctor_type}  
        **Date & Time:** {date.strftime('%d %b %Y')} at {time.strftime('%I:%M %p')}  
        """)
