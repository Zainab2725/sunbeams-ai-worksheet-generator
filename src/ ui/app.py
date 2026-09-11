from __future__ import annotations

from datetime import datetime
import re
import streamlit as st

from src.pdf_generator.pdf_generator import build_answer_key_pdf, build_worksheet_pdf

NAVY = "#0B2E5B"
GOLD = "#F4B400"
INK = "#1A1A1A"
MUTED = "#667085"
CANVAS = "#F5F6F8"
BORDER = "#D9DCE1"

st.set_page_config(page_title="Sunbeams Worksheet Generator", page_icon="☀", layout="wide", initial_sidebar_state="expanded")


def inject_styles() -> None:
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    :root {{ --navy:{NAVY}; --gold:{GOLD}; --ink:{INK}; --muted:{MUTED}; --canvas:{CANVAS}; --border:{BORDER}; }}
    html, body, [class*="css"] {{ font-family:'Inter',sans-serif; color:var(--ink); }}
    [data-testid="stAppViewContainer"] {{ background:var(--canvas); }} [data-testid="stHeader"] {{ background:transparent; }}
    [data-testid="stSidebar"] {{ background:#fff; border-right:1px solid var(--border); }} [data-testid="stSidebarContent"] {{ padding:1.25rem 1.1rem; }}
    .brand-bar {{ background:var(--navy); border-radius:14px; padding:1.1rem 1.35rem; display:flex; align-items:center; justify-content:space-between; margin-bottom:1.35rem; box-shadow:0 6px 18px rgba(11,46,91,.12); }}
    .brand-lockup {{ display:flex; align-items:center; gap:.8rem; color:#fff; }} .brand-mark {{ width:42px; height:42px; border-radius:50%; background:var(--gold); color:var(--navy); display:flex; align-items:center; justify-content:center; font-size:1.4rem; font-weight:800; }}
    .brand-name {{ font-size:1.12rem; font-weight:800; }} .brand-sub {{ color:#dbe7f5; font-size:.72rem; margin-top:.13rem; }} .header-title {{ text-align:right; color:#fff; }} .header-title h1 {{ font-size:1.25rem; margin:0; }} .header-title p {{ color:#f9d56c; margin:.2rem 0 0; font-size:.75rem; }}
    .eyebrow {{ color:var(--gold); font-size:.72rem; font-weight:800; text-transform:uppercase; letter-spacing:.12em; margin-bottom:.35rem; }} .page-heading {{ font-size:1.8rem; color:var(--navy); font-weight:800; margin:0; }} .page-copy {{ color:var(--muted); margin:.25rem 0 1.2rem; font-size:.9rem; }}
    .section-label {{ color:var(--navy); font-size:.75rem; font-weight:800; letter-spacing:.08em; text-transform:uppercase; margin:1.15rem 0 .55rem; }} .preview-card,.metric,.history-item {{ background:#fff; border:1px solid var(--border); border-radius:12px; padding:1.15rem 1.25rem; box-shadow:0 3px 12px rgba(16,24,40,.04); margin-bottom:.85rem; }}
    .worksheet-title {{ color:var(--navy); font-size:1.3rem; font-weight:800; margin:0; }} .worksheet-meta,.history-date {{ color:var(--muted); font-size:.78rem; margin-top:.3rem; }}
    .rtl-card {{ direction:rtl; text-align:right; background:#fffdf4; border:1px solid #f4d77a; border-radius:12px; padding:1.2rem; min-height:170px; }} .rtl-card h4 {{ color:var(--navy); margin:0 0 .5rem; font-size:1rem; }} .rtl-copy {{ font-family:'Noto Nastaliq Urdu','Jameel Noori Nastaliq',serif; font-size:1.08rem; line-height:2.05; color:#253047; }}
    .metric-label {{ color:var(--muted); font-size:.72rem; }} .metric-value {{ color:var(--navy); font-size:1.2rem; font-weight:800; margin-top:.2rem; }} .history-title {{ color:var(--navy); font-weight:700; font-size:.86rem; }}
    div.stButton > button {{ border-radius:8px; font-weight:700; border:1px solid var(--navy); min-height:2.55rem; }} div.stButton > button[kind="primary"] {{ background:var(--gold); color:var(--navy); border-color:var(--gold); }} .stDownloadButton > button {{ background:var(--navy); color:#fff; border-color:var(--navy); border-radius:8px; font-weight:700; width:100%; }}
    /* Question editors: warm yellow surface with dark readable text. */
    div[data-testid="stTextArea"] textarea {{ background:#FFF4BF !important; color:#111827 !important; border:2px solid #E0A800 !important; border-radius:9px !important; font-weight:500 !important; }}
    div[data-testid="stTextArea"] label {{ color:var(--navy) !important; font-weight:800 !important; }} [data-testid="stMetricValue"] {{ color:var(--navy); }}
    </style>
    """, unsafe_allow_html=True)


def topic_key(topic: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", topic.lower()).strip()


def generate_questions(topic: str, subject: str, grade: str, difficulty: str, total: int, types: list[str]) -> list[str]:
    """Create deterministic demo questions driven by the selected topic and controls."""
    topic_text = topic.strip() or "General revision"
    key = topic_key(topic_text)
    bank: dict[str, dict[str, list[str]]] = {
        "maths": {
            "MCQ": [f"Choose the correct answer about {topic_text}: Which statement is true? A) It is important B) It is impossible C) It is unrelated", f"Solve this {topic_text} question: What is the next step? A) Add B) Subtract C) Ignore"],
            "Fill in the blanks": [f"Complete the {topic_text} sentence: The answer is ____.", f"In {topic_text}, we use ____ to find the solution."],
            "Short answer": [f"Explain one example of {topic_text} in your own words.", f"Write the steps you would use to solve a {topic_text} problem."],
            "True / False": [f"True or False: {topic_text} can be practised using real-life examples.", f"True or False: Checking your work is useful when studying {topic_text}."],
            "Matching": [f"Match each idea with its use in {topic_text}.", f"Match the terms and meanings from the {topic_text} lesson."],
        },
        "science": {}, "english": {}, "urdu": {},
    }
    generic = {
        "MCQ": [f"Choose the correct answer about {topic_text}: Which statement is correct? A) It helps us learn B) It is never useful C) None of these", f"Which option best describes {topic_text}? A) A key lesson idea B) A random guess C) An unrelated idea"],
        "Fill in the blanks": [f"Complete the sentence about {topic_text}: We learn about ____.", f"The most important word in this {topic_text} lesson is ____ ."],
        "Short answer": [f"Write two sentences explaining {topic_text}.", f"Give one example related to {topic_text}."],
        "True / False": [f"True or False: {topic_text} is part of this lesson.", f"True or False: Reviewing {topic_text} helps us remember it."],
        "Matching": [f"Match the words with their meanings from {topic_text}.", f"Match each example to the correct idea in {topic_text}."],
    }
    subject_bank = bank.get(subject.lower(), {})
    pools = {name: subject_bank.get(name, generic[name]) for name in types}
    if not pools:
        pools = {"Short answer": generic["Short answer"]}
    questions: list[str] = []
    round_no = 0
    while len(questions) < total:
        for question_type in types or ["Short answer"]:
            pool = pools[question_type]
            questions.append(pool[round_no % len(pool)])
            if len(questions) >= total:
                break
        round_no += 1
    return questions


def answer_for(question: str) -> str:
    if question.startswith("Choose"):
        return "Teacher selects the correct option"
    if question.startswith("True or False"):
        return "True"
    if "blank" in question.lower():
        return "Teacher review required"
    return "Review learner response"


inject_styles()
with st.sidebar:
    st.markdown('<div class="eyebrow">Track 2 · Teacher workspace</div>', unsafe_allow_html=True)
    st.markdown("### Worksheet setup")
    st.caption("Configure the lesson, question mix, and output preferences.")
    st.markdown('<div class="section-label">Class & subject</div>', unsafe_allow_html=True)
    grade = st.selectbox("Class / Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5"], label_visibility="collapsed")
    subject = st.selectbox("Subject", ["Urdu", "English", "Maths", "Science"], label_visibility="collapsed")
    st.markdown('<div class="section-label">Topic / chapter</div>', unsafe_allow_html=True)
    topic = st.text_input("Topic or textbook chapter", value="Our Environment", label_visibility="collapsed", placeholder="e.g. Fractions, Plants...")
    st.markdown('<div class="section-label">Question mix</div>', unsafe_allow_html=True)
    mcq = st.checkbox("Multiple choice questions", value=True)
    fill = st.checkbox("Fill in the blanks", value=True)
    short = st.checkbox("Short answers", value=True)
    tf = st.checkbox("True / False", value=True)
    matching = st.checkbox("Matching", value=False)
    st.markdown('<div class="section-label">Difficulty & length</div>', unsafe_allow_html=True)
    difficulty = st.select_slider("Difficulty", options=["Easy", "Medium", "Hard"], value="Medium")
    total = st.slider("Total questions", 4, 20, 10)
    st.markdown('<div class="section-label">Language & exports</div>', unsafe_allow_html=True)
    bilingual = st.toggle("Enable Urdu / RTL preview", value=True)
    answer_key = st.toggle("Include teacher answer key", value=True)
    st.caption("PDFs are generated locally with an embedded Unicode Urdu font.")
    st.markdown("---")
    regenerate = st.button("Generate AI worksheet", type="primary", use_container_width=True)

types = [name for name, enabled in [("MCQ", mcq), ("Fill in the blanks", fill), ("Short answer", short), ("True / False", tf), ("Matching", matching)] if enabled]
signature = (grade, subject, topic.strip(), difficulty, total, tuple(types))
if "worksheet_signature" not in st.session_state or st.session_state.worksheet_signature != signature or regenerate:
    st.session_state.questions = generate_questions(topic, subject, grade, difficulty, total, types)
    st.session_state.worksheet_signature = signature
    if regenerate:
        st.toast("AI worksheet regenerated", icon="✅")

st.markdown('<div class="brand-bar"><div class="brand-lockup"><div class="brand-mark">☀</div><div><div class="brand-name">SUNBEAMS</div><div class="brand-sub">School System · Worksheet Studio</div></div></div><div class="header-title"><h1>Worksheet Generator</h1><p>Learn · Grow · Shine</p></div></div>', unsafe_allow_html=True)
st.markdown('<div class="page-heading">AI worksheet generator</div>', unsafe_allow_html=True)
st.markdown('<div class="page-copy">Create, edit, and export a topic-focused worksheet for your learners.</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4)
for col, label, value in [(m1, "Class", grade), (m2, "Subject", subject), (m3, "Difficulty", difficulty), (m4, "Questions", str(len(st.session_state.questions)))]:
    with col:
        st.markdown(f'<div class="metric"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)

preview_tab, bilingual_tab, history_tab = st.tabs(["Worksheet preview", "Bilingual preview", "Generation history"])
with preview_tab:
    left, right = st.columns([1.65, 1])
    with left:
        st.markdown(f'<div class="preview-card"><div class="worksheet-title">{subject}: {topic or "General revision"}</div><div class="worksheet-meta">{grade} · {difficulty} level · {len(st.session_state.questions)} questions · Editable draft</div></div>', unsafe_allow_html=True)
        st.info("Inline editing is enabled below. Edit any question, then export the updated draft.", icon="📝")
        for i, question in enumerate(st.session_state.questions):
            st.session_state.questions[i] = st.text_area(f"Question {i + 1}", value=question, key=f"question_{i}", height=76)
    with right:
        st.markdown('<div class="section-label">Question mix summary</div>', unsafe_allow_html=True)
        st.markdown("\n".join(f"- **{name}**" for name in types) or "No question types selected")
        st.markdown('<div class="section-label">Actions</div>', unsafe_allow_html=True)
        worksheet_pdf = build_worksheet_pdf(st.session_state.questions, subject, grade, topic, difficulty, include_urdu=bilingual)
        safe_topic = "_".join((topic.strip() or "worksheet").lower().split())
        st.download_button("Download printable PDF", data=worksheet_pdf, file_name=f"sunbeams_{safe_topic}.pdf", mime="application/pdf")
        if answer_key:
            key_pdf = build_answer_key_pdf(st.session_state.questions, subject, grade, topic, [answer_for(q) for q in st.session_state.questions])
            st.download_button("Download teacher answer key", data=key_pdf, file_name=f"sunbeams_{safe_topic}_answer_key.pdf", mime="application/pdf")
        st.success("PDF export is active with embedded Unicode Urdu font.")

with bilingual_tab:
    if bilingual:
        st.markdown('<div class="rtl-card"><h4>اردو پیش نظارہ · Bilingual worksheet</h4><div class="rtl-copy">سوال ۱: درست جواب منتخب کریں۔ سورج کہاں سے طلوع ہوتا ہے؟<br><br>سوال ۲: خالی جگہ پُر کریں: پودوں کو بڑھنے کے لیے ____ کی ضرورت ہوتی ہے۔<br><br>سوال ۳: اپنے کلاس روم کو صاف رکھنے کے دو طریقے لکھیں۔</div></div>', unsafe_allow_html=True)
        st.caption("The downloadable worksheet includes the same Urdu section with an embedded Nastaliq-compatible font.")
    else:
        st.warning("Enable the Urdu / RTL preview toggle in the sidebar to view the bilingual worksheet.")

with history_tab:
    st.markdown('<div class="preview-card"><div class="worksheet-title">Recent worksheets</div><div class="worksheet-meta">Reload a previous draft to continue editing.</div></div>', unsafe_allow_html=True)
    for title_text, details in [("Our Environment", "Science · Grade 3 · Medium"), ("Fractions", "Maths · Grade 5 · Easy"), ("My School", "English · Grade 2 · Medium")]:
        c1, c2 = st.columns([4, 1])
        with c1:
            st.markdown(f'<div class="history-item"><div class="history-title">{title_text}</div><div class="history-date">{details} · Saved today</div></div>', unsafe_allow_html=True)
        with c2:
            st.button("Reload", key=f"reload_{title_text}", use_container_width=True)

st.markdown("---")
st.caption(f"Sunbeams Worksheet Studio · PDF export enabled · Last edited {datetime.now().strftime('%d %b %Y')}")
