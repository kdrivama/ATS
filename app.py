import streamlit as st
from transformers import pipeline

# Initialize the model
classifier = pipeline("zero-shot-classification", model="typeform/distilbert-base-uncased-mnli")

# State management using Streamlit's session state
if "state" not in st.session_state:
    st.session_state.state = {
        "language": None,
        "current_step": 1,
        "exercise_count": 0,
        "last_user_input": "",
        "history": []
    }

# Language content
content = {
    "english": {
        "greeting": "Hello! I'm your ATS Resume Trainer. Let's get started! Which language would you prefer?",
        "principles": [
            "Let me explain the basic principles of writing ATS-friendly resumes:",
            "1. **Action Verb**: Start with a strong action verb (e.g., 'Managed', 'Developed', 'Implemented')",
            "2. **Task Description**: Clearly describe what you did",
            "3. **Quantification**: Add numbers to show impact (e.g., 'increased sales by 20%')",
            "The formula is: **Action Verb + Task Description + Quantification**",
            "Now, let's practice! Please write one line about your work experience (as you would normally write it):"
        ],
        "rewrite_prompt": "Great! Now rewrite that experience following the ATS format (Action Verb + Task Description + Quantification):",
        "feedback": {
            "good": "Excellent! You've nailed the ATS format. Let's try another one to reinforce your learning.",
            "needs_work": "Not quite there. Your response should include a strong action verb, a clear task description, and quantification (e.g., numbers or percentages). Here's a suggestion based on your input: try starting with an action like 'Managed' or 'Developed' and add a metric like 'by 20%'. Please try again."
        },
        "continue_prompt": "Would you like to try another one?",
        "farewell": "You're doing great! With 2-3 more practice sessions, you'll master ATS-friendly resume writing. Goodbye and good luck with your job search!",
        "options": ["English", "Indonesian"]
    },
    "indonesian": {
        "greeting": "Halo! Saya ATS Resume Trainer Anda. Mari kita mulai! Bahasa apa yang Anda inginkan?",
        "principles": [
            "Izinkan saya menjelaskan prinsip dasar menulis resume yang ramah ATS:",
            "1. **Kata Kerja Aksi**: Mulai dengan kata kerja aksi yang kuat (misalnya, 'Mengelola', 'Mengembangkan', 'Menerapkan')",
            "2. **Deskripsi Tugas**: Jelaskan dengan jelas apa yang Anda lakukan",
            "3. **Kuantifikasi**: Tambahkan angka untuk menunjukkan dampak (misalnya, 'meningkatkan penjualan sebesar 20%')",
            "Rumusnya adalah: **Kata Kerja Aksi + Deskripsi Tugas + Kuantifikasi**",
            "Sekarang, mari berlatih! Tolong tulis satu baris tentang pengalaman kerja Anda (seperti yang biasa Anda tulis):"
        ],
        "rewrite_prompt": "Bagus! Sekarang tulis ulang pengalaman itu dengan mengikuti format ATS (Kata Kerja Aksi + Deskripsi Tugas + Kuantifikasi):",
        "feedback": {
            "good": "Luar biasa! Anda telah menguasai format ATS. Mari mencoba yang lain untuk memperkuat pembelajaran Anda.",
            "needs_work": "Belum cukup. Respons Anda harus mencakup kata kerja aksi yang kuat, deskripsi tugas yang jelas, dan kuantifikasi (misalnya, angka atau persentase). Berikut saran berdasarkan input Anda: coba mulai dengan aksi seperti 'Mengelola' atau 'Mengembangkan' dan tambahkan metrik seperti 'sebesar 20%'. Silakan coba lagi."
        },
        "continue_prompt": "Apakah Anda ingin mencoba yang lain?",
        "farewell": "Anda melakukannya dengan baik! Dengan 2-3 sesi latihan lagi, Anda akan menguasai penulisan resume yang ramah ATS. Selamat tinggal dan semoga sukses dengan pencarian kerja Anda!",
        "options": ["Inggris", "Indonesia"]
    }
}

# Analytical check using the model
def analyze_ats_format(text, language):
    if not text or len(text) < 10:
        return False, content[language]["feedback"]["needs_work"]
    
    labels = ["has_action_verb", "has_task_description", "has_quantification"]
    result = classifier(text, labels)
    
    scores = result['scores']
    has_action_verb = scores[labels.index("has_action_verb")] > 0.5
    has_task_description = scores[labels.index("has_task_description")] > 0.5
    has_quantification = scores[labels.index("has_quantification")] > 0.5
    
    if has_action_verb and has_task_description and has_quantification:
        return True, content[language]["feedback"]["good"]
    else:
        return False, content[language]["feedback"]["needs_work"]

# Streamlit app
st.title("ATS Resume Trainer")
st.markdown("**Online • Training you for ATS-friendly resumes**")

# Display chat history
for message in st.session_state.state["history"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle user input and dropdown
if st.session_state.state["current_step"] in [1, 2, 7]:
    options = content["english"]["options"]
    if st.session_state.state["current_step"] == 7:
        options = ["Yes", "No"] if st.session_state.state["language"] == "english" else ["Ya", "Tidak"]
    user_input = st.selectbox("Select an option", options, key=f"select_{st.session_state.state['current_step']}")
else:
    user_input = st.chat_input("Type your message...")

if user_input:
    # Add user input to history
    st.session_state.state["history"].append({"role": "user", "content": user_input})
    
    response = ""
    show_options = False
    
    if st.session_state.state["current_step"] == 1:
        response = content["english"]["greeting"]
        st.session_state.state["current_step"] = 2
        show_options = True
    
    elif st.session_state.state["current_step"] == 2:
        if user_input not in content["english"]["options"] + content["indonesian"]["options"]:
            response = "Please select a valid language (English or Indonesian)."
            show_options = True
        else:
            st.session_state.state["language"] = "english" if user_input == "English" else "indonesian"
            response = content[st.session_state.state["language"]]["greeting"]
            st.session_state.state["current_step"] = 3
    
    elif st.session_state.state["current_step"] == 3:
        response = "\n".join(content[st.session_state.state["language"]]["principles"])
        st.session_state.state["current_step"] = 4
    
    elif st.session_state.state["current_step"] == 4:
        st.session_state.state["last_user_input"] = user_input
        st.session_state.state["current_step"] = 5
        response = content[st.session_state.state["language"]]["rewrite_prompt"]
    
    elif st.session_state.state["current_step"] == 5:
        is_valid, feedback = analyze_ats_format(user_input, st.session_state.state["language"])
        response = feedback
        
        if is_valid:
            st.session_state.state["exercise_count"] += 1
            if st.session_state.state["exercise_count"] >= 3:
                st.session_state.state["current_step"] = 7
                response = content[st.session_state.state["language"]]["continue_prompt"]
                show_options = True
            else:
                st.session_state.state["current_step"] = 4
                response = content[st.session_state.state["language"]]["principles"][-1]
        else:
            response = feedback
    
    elif st.session_state.state["current_step"] == 7:
        valid_options = ["Yes", "No"] if st.session_state.state["language"] == "english" else ["Ya", "Tidak"]
        if user_input not in valid_options:
            response = "Please select Yes/No (or Ya/Tidak)."
            show_options = True
        elif user_input in ("Yes", "Ya"):
            st.session_state.state["current_step"] = 4
            st.session_state.state["exercise_count"] += 1
            response = content[st.session_state.state["language"]]["principles"][-1]
        else:
            st.session_state.state["current_step"] = 1
            st.session_state.state["exercise_count"] = 0
            response = content[st.session_state.state["language"]]["farewell"]
            show_options = True
    
    # Add response to history
    st.session_state.state["history"].append({"role": "assistant", "content": response})
    
    # Refresh to show new messages
    st.rerun()