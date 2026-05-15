import streamlit as st
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from collections import Counter
import random
import re
from datetime import datetime, date

# Download NLTK data
@st.cache_resource
def download_nltk():
    nltk.download('punkt_tab')
    nltk.download('stopwords')

download_nltk()

# ---------- Black & White CSS ----------
def set_bw_css():
    st.markdown("""
    <style>
    .stApp { background: #ffffff; }
    h1, h2, h3, p, li, span, label { color: #000000 !important; }
    .stButton button { background: #000000; color: white; border-radius: 20px; }
    .stButton button:hover { background: #333333; }
    .stRadio > div { background: #f5f5f5; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# ---------- Summarizer ----------
stop_words = set(stopwords.words('english'))

def summarize_text(text, num_sentences=3):
    sentences = sent_tokenize(text)
    if len(sentences) <= num_sentences:
        return text
    words = word_tokenize(text.lower())
    words = [w for w in words if w.isalpha() and w not in stop_words]
    freq = Counter(words)
    sentence_scores = {}
    for sent in sentences:
        word_count = len(word_tokenize(sent))
        score = sum(freq.get(w, 0) for w in word_tokenize(sent.lower()) if w.isalpha())
        sentence_scores[sent] = score / word_count if word_count else 0
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]
    return " ".join(top_sentences)

# ---------- Quiz generator ----------
def generate_quiz(text, num_questions=5):
    sentences = sent_tokenize(text)
    if len(sentences) < num_questions:
        num_questions = len(sentences)
    selected = random.sample(sentences, num_questions)
    questions = []
    for s in selected:
        words = word_tokenize(s)
        content_words = [w for w in words if w.isalpha() and len(w) > 3 and w.lower() not in stop_words]
        if not content_words:
            continue
        answer_word = random.choice(content_words)
        question_text = s.replace(answer_word, "______")
        all_words = [w for w in word_tokenize(text) if w.isalpha() and len(w) > 3]
        distractors = [w for w in all_words if w != answer_word]
        if len(distractors) < 3:
            distractors = ["something", "concept", "idea"]
        options = [answer_word] + random.sample(distractors, min(3, len(distractors)))
        random.shuffle(options)
        questions.append({
            "question": question_text,
            "options": options,
            "answer": answer_word
        })
    return questions

# ---------- Study planner ----------
def study_planner(exam_date, total_topics, hours_per_topic=2):
    today = date.today()
    delta = (exam_date - today).days
    if delta <= 0:
        return "Exam date must be in the future."
    total_hours = total_topics * hours_per_topic
    hours_per_day = total_hours / delta
    return f"Study {hours_per_day:.1f} hours/day to cover {total_topics} topics before {exam_date}."

# ---------- Main UI ----------
def main():
    st.set_page_config(page_title="Smart Study Tool", page_icon="📚")
    set_bw_css()
    st.markdown("<h1>📚 Smart Study Tool</h1>", unsafe_allow_html=True)
    st.markdown("Summarize notes • Quiz yourself • Plan study time")
    
    tab1, tab2, tab3 = st.tabs(["📝 Notes & Summary", "❓ Quiz", "⏰ Study Planner"])
    
    with tab1:
        st.subheader("📄 Your Study Notes")
        notes = st.text_area("Paste your notes here", height=200)
        if st.button("🔍 Summarize", key="summarize"):
            if not notes.strip():
                st.warning("Please paste some notes.")
            else:
                summary = summarize_text(notes, num_sentences=3)
                st.success("📌 Key points:")
                st.write(summary)
                st.session_state['notes'] = notes
    
    with tab2:
        st.subheader("❓ Auto-generated Quiz")
        if 'notes' in st.session_state and st.session_state['notes'].strip():
            if st.button("🎲 Generate Quiz", key="gen_quiz"):
                questions = generate_quiz(st.session_state['notes'], num_questions=5)
                st.session_state['quiz_questions'] = questions
                st.session_state['quiz_answers'] = {}
            if 'quiz_questions' in st.session_state:
                answers = {}
                for i, q in enumerate(st.session_state['quiz_questions']):
                    st.markdown(f"**Q{i+1}:** {q['question']}")
                    answer = st.radio(f"Choose answer for Q{i+1}", q['options'], key=f"q{i}")
                    answers[i] = answer
                    st.markdown("---")
                if st.button("✅ Submit Quiz"):
                    score = 0
                    for i, q in enumerate(st.session_state['quiz_questions']):
                        if answers[i] == q['answer']:
                            score += 1
                    st.metric("🏆 Your Score", f"{score}/{len(st.session_state['quiz_questions'])}")
                    if score == len(st.session_state['quiz_questions']):
                        st.balloons()
                        st.success("Perfect! You know your stuff.")
                    else:
                        st.info("💡 Review your notes and try again.")
        else:
            st.info("First paste notes in the 'Notes & Summary' tab and click Summarize.")
    
    with tab3:
        st.subheader("📅 Plan Your Study")
        exam_date = st.date_input("Exam date")
        topics = st.number_input("Number of topics", min_value=1, max_value=50, value=5)
        hours_per_topic = st.number_input("Hours needed per topic", min_value=0.5, max_value=10.0, value=2.0)
        if st.button("⏰ Calculate Plan"):
            if exam_date:
                plan = study_planner(exam_date, topics, hours_per_topic)
                st.info(plan)
            else:
                st.warning("Pick an exam date.")
    
    st.markdown("---")
    st.caption("Study smart, not hard. Generate quizzes from your own notes.")

if __name__ == "__main__":
    main()