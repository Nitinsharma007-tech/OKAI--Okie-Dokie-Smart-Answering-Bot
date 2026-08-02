
import streamlit as st

from app.chatbot import OKAIChatbot


# ----------------------------
# Page Config
# ----------------------------

st.set_page_config(

    page_title="OKAI ERP Assistant",

    page_icon="🤖",

    layout="wide",

    initial_sidebar_state="expanded"

)
@st.cache_resource
def load_okai():

    return OKAIChatbot()
bot = load_okai()
# ----------------------------
# CSS
# ----------------------------

st.markdown("""
<style>
    :root {
        --orange-1: #ff7a33;
        --orange-2: #ff9d57;
        --orange-soft: #fff4eb;
        --bg-white: #ffffff;
        --bg-cream: #fffaf5;
        --text: #111827;
        --muted: #5f6978;
        --line: rgba(255, 122, 51, 0.15);
        --shadow: 0 18px 42px rgba(255, 122, 51, 0.08);
    }

    html, body {
        cursor: none !important;
    }

    .stApp {
        background:
            radial-gradient(circle at 20% 10%, rgba(255, 161, 98, 0.18), transparent 20%),
            radial-gradient(circle at 80% 0%, rgba(255, 122, 51, 0.14), transparent 22%),
            linear-gradient(180deg, #fffdfb 0%, #fff7f3 100%);
    }

    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 2.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1280px;
    }

    #MainMenu, footer, header {
        visibility: hidden;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fffaf5 0%, #fff2e9 100%);
        border-right: 1px solid var(--line);
        box-shadow: 8px 0 20px rgba(17, 24, 39, 0.02);
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.2rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] div {
        color: var(--text);
    }

    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.8);
        border: 1px solid rgba(255, 122, 51, 0.12);
        border-radius: 18px;
        box-shadow: 0 12px 22px rgba(17, 24, 39, 0.02);
        padding: 1rem;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }

    [data-testid="stMetric"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 16px 26px rgba(255, 122, 51, 0.08);
    }

    [data-testid="stAlert"] {
        background: #fffaf6;
        border: 1px solid rgba(255, 122, 51, 0.18);
        border-radius: 14px;
        color: var(--text);
    }

    .stButton>button {
        width: 100%;
        border-radius: 14px;
        height: 46px;
        background: linear-gradient(135deg, #ffffff 0%, #fff7f1 100%);
        color: var(--text);
        border: 1px solid rgba(255, 122, 51, 0.2);
        box-shadow: 0 8px 16px rgba(17, 24, 39, 0.02);
        transition: transform 0.25s ease, border-color 0.25s ease, box-shadow 0.25s ease, background 0.25s ease;
        font-weight: 700;
    }

    .stButton>button:hover {
        border-color: rgba(255, 122, 51, 0.55);
        transform: translateY(-2px) scale(1.01);
        box-shadow: 0 14px 22px rgba(255, 122, 51, 0.12);
        background: linear-gradient(135deg, #fff6ec 0%, #fff0df 100%);
    }

    .stButton>button:focus {
        box-shadow: 0 0 0 4px rgba(255, 122, 51, 0.12);
    }

    .okai-hero {
        position: relative;
        overflow: hidden;
        padding: 1.5rem 1.4rem 1.3rem;
        border-radius: 30px;
        background: linear-gradient(135deg, rgba(255,255,255,0.96) 0%, rgba(255,247,240,0.96) 45%, rgba(255,236,221,0.96) 100%);
        border: 1px solid rgba(255, 122, 51, 0.18);
        box-shadow: var(--shadow);
        margin-bottom: 1.2rem;
        animation: fadeUp 0.45s ease-out;
    }

    .okai-hero::before,
    .okai-hero::after {
        content: "";
        position: absolute;
        border-radius: 50%;
        filter: blur(10px);
        opacity: 0.75;
        animation: floatOrb 8s ease-in-out infinite alternate;
    }

    .okai-hero::before {
        width: 220px;
        height: 220px;
        background: rgba(255, 166, 107, 0.2);
        right: -38px;
        top: -68px;
    }

    .okai-hero::after {
        width: 170px;
        height: 170px;
        background: rgba(255, 122, 51, 0.12);
        left: -22px;
        bottom: -58px;
        animation-delay: 1.1s;
    }

    .hero-tag {
        position: relative;
        z-index: 1;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.45rem 0.85rem;
        border: 1px solid rgba(255, 122, 51, 0.16);
        border-radius: 999px;
        background: rgba(255, 122, 51, 0.06);
        color: var(--orange-1);
        font-size: 0.68rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        font-weight: 800;
        margin-bottom: 0.8rem;
    }

    .main-title {
        position: relative;
        z-index: 1;
        font-size: clamp(2.2rem, 4vw, 4rem);
        font-weight: 900;
        color: #111827;
        margin: 0;
        line-height: 1.05;
        letter-spacing: -0.06em;
    }

    .sub-title {
        position: relative;
        z-index: 1;
        margin: 0.75rem 0 0;
        font-size: 1.06rem;
        color: var(--muted);
        line-height: 1.6;
    }

    .typing-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 1.2rem 0 1.6rem;
        width: 100%;
    }

    .typing-text {
        font-size: clamp(1rem, 2vw, 1.7rem);
        font-weight: 800;
        color: var(--orange-1);
        overflow: hidden;
        white-space: nowrap;
        border-right: 3px solid var(--orange-1);
        animation: typing 4s steps(50, end), blink 0.8s infinite;
        max-width: 100%;
        padding-right: 0.28rem;
    }

    [data-testid="stChatInput"] {
        padding-top: 12px;
    }

    [data-testid="stChatInput"] > div {
        border-radius: 16px;
        border: 1px solid rgba(255, 122, 51, 0.2);
        background: rgba(255, 255, 255, 0.95);
        box-shadow: 0 12px 24px rgba(255, 122, 51, 0.04);
        transition: box-shadow 0.25s ease, border-color 0.25s ease;
    }

    [data-testid="stChatInput"] > div:hover {
        border-color: rgba(255, 122, 51, 0.42);
        box-shadow: 0 18px 28px rgba(255, 122, 51, 0.08);
    }

    [data-testid="stChatMessage"] {
        margin-bottom: 0.9rem;
        animation: fadeUp 0.28s ease-out;
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageAvatar"] {
        background: linear-gradient(135deg, #ff7a33 0%, #ff9d57 100%);
        color: #fff;
        border-radius: 12px;
        box-shadow: 0 10px 20px rgba(255, 122, 51, 0.14);
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        background: rgba(255,255,255,0.9);
        border: 1px solid rgba(255, 122, 51, 0.12);
        border-radius: 18px;
        box-shadow: 0 10px 18px rgba(17, 24, 39, 0.02);
        padding: 1rem 1.1rem;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
    }

    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 14px 22px rgba(255, 122, 51, 0.08);
    }

    [data-testid="stExpander"] {
        border: 1px solid rgba(255, 122, 51, 0.12);
        border-radius: 16px;
        background: rgba(255,255,255,0.7);
        box-shadow: 0 8px 18px rgba(17, 24, 39, 0.01);
    }

    .stTabs [role="tablist"] {
        gap: 0.6rem;
    }

    .stTabs [role="tab"] {
        border-radius: 12px;
        padding: 0.55rem 1rem;
        color: var(--muted);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .stTabs [role="tab"]:hover {
        transform: translateY(-1px);
    }

    .stTabs [role="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--orange-1) 0%, var(--orange-2) 100%);
        color: white;
        box-shadow: 0 10px 18px rgba(255, 122, 51, 0.14);
    }

    ::-webkit-scrollbar {
        width: 8px;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #ffd5b2 0%, #ff7a33 100%);
        border-radius: 20px;
    }

    .cursor-glow,
    .cursor-ring {
        position: fixed;
        pointer-events: none;
        z-index: 9999;
        border-radius: 50%;
        mix-blend-mode: screen;
        transition: opacity 0.2s ease;
    }

    .cursor-glow {
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(255, 166, 100, 0.34) 0%, rgba(255, 122, 51, 0.16) 28%, transparent 70%);
        filter: blur(18px);
        transform: translate(-50%, -50%);
    }

    .cursor-ring {
        width: 22px;
        height: 22px;
        border: 1.5px solid rgba(255, 122, 51, 0.8);
        background: rgba(255, 255, 255, 0.22);
        box-shadow: 0 0 18px rgba(255, 122, 51, 0.2);
        transform: translate(-50%, -50%);
    }

    @keyframes fadeUp {
        from {
            opacity: 0;
            transform: translateY(12px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }

    @keyframes floatOrb {
        0% { transform: translate3d(0, 0, 0) scale(1); }
        100% { transform: translate3d(12px, -18px, 0) scale(1.08); }
    }

    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }

    @keyframes blink {
        50% { border-color: transparent; }
    }
</style>
<div class="cursor-glow"></div>
<div class="cursor-ring"></div>
<script>
    const glow = document.querySelector('.cursor-glow');
    const ring = document.querySelector('.cursor-ring');

    document.addEventListener('pointermove', (e) => {
        if (!glow || !ring) return;
        glow.style.left = `${e.clientX}px`;
        glow.style.top = `${e.clientY}px`;
        ring.style.left = `${e.clientX}px`;
        ring.style.top = `${e.clientY}px`;
    });

    document.querySelectorAll('button, [data-testid="stChatInput"], [data-testid="stMetric"], [role="tab"], [data-testid="stExpander"]').forEach((el) => {
        el.addEventListener('mouseenter', () => {
            if (glow) glow.style.opacity = '1';
            if (ring) ring.style.transform = 'translate(-50%, -50%) scale(1.18)';
        });
        el.addEventListener('mouseleave', () => {
            if (glow) glow.style.opacity = '0.9';
            if (ring) ring.style.transform = 'translate(-50%, -50%) scale(1)';
        });
    });
</script>
""", unsafe_allow_html=True)

# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:

    st.title("🤖 OKAI")

    st.markdown("---")

    st.success("🟢 Knowledge Base Loaded")
    st.success("🧠 Embeddings Ready")
    st.success("✨ Gemini Connected")



    st.metric("Knowledge Topics", len(bot.search.records))
    st.metric("Top-K Retrieval", "3")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):

        st.session_state.messages=[]

        st.rerun()

# ----------------------------
# Title
# ----------------------------

st.markdown("""
<div style="padding-top:25px;padding-bottom:15px;">

<h1 class="main-title">
🤖 OKIE DOKIE OKAI
</h1>

<p class="sub-title">
Your AI Powered ERP Assistant using RAG + Gemini
</p>

</div>

<hr style="border:1px solid #2F3136;">

""", unsafe_allow_html=True)
# ----------------------------
# Session
# ----------------------------

if "messages" not in st.session_state:

    st.session_state.messages=[]

# ==========================================================
# Load OKAI Only Once
# ==========================================================


# ============================================================
# Display Previous Messages
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ============================================================
# Chat Input
# ============================================================

# ============================================================
# Chat Input
# ============================================================

# Store clicked suggested question
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

typed_question = st.chat_input(
    "Ask anything about the ERP..."
)

# Use typed question if available
question = typed_question

# If a suggested question was clicked,
# process it exactly like a new user message.
if st.session_state.pending_question:
    question = st.session_state.pending_question
    st.session_state.pending_question = None

# ============================================================
# When User Sends Message
# ============================================================

if question:

    # ------------------------
    # Show User Message
    # ------------------------

    st.session_state.messages.append({

        "role": "user",

        "content": question

    })

    with st.chat_message("user"):

        st.markdown(question)

    # ------------------------
    # Generate Answer
    # ------------------------

    with st.chat_message("assistant"):

        with st.spinner("🧠 OKAI is thinking..."):

            try:

                # ------------------------------------
                # Semantic Search
                # ------------------------------------

                search_results = bot.search.search(
                    question,
                    top_k=3
                )

                # ------------------------------------
                # Context Builder
                # ------------------------------------

                context = bot.builder.build(
                    search_results
                )

                # ------------------------------------
                # Gemini Prompt
                # ------------------------------------

                prompt = f"""
You are OKAI, an intelligent ERP Assistant.

Answer ONLY using the knowledge provided below.

If the answer is not present in the knowledge,
say:

"I couldn't find this information in the ERP knowledge base."

Do not invent information.

Always answer professionally.

Always explain in simple language.

If there are steps,
present them as numbered points.

==========================
USER QUESTION
==========================

{question}

==========================
ERP KNOWLEDGE
==========================

{context}
"""

                # ------------------------------------
                # Gemini Response
                # ------------------------------------

                answer = bot.gemini.generate(
                    prompt
                )

                st.markdown(answer)

            except Exception as e:

                error_message = str(e)

                # ------------------------------------
                # Gemini Quota Exceeded (429)
                # ------------------------------------
                if "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:

                    answer = f"""
## ⚠️ Gemini API Limit Reached

The free Gemini API request limit has been exceeded.

### 📚 Retrieved ERP Knowledge

{context}

---

💡 **Suggestion:** Please wait for a minute or use another configured API key.
"""

                    st.warning(answer)

                # ------------------------------------
                # Gemini Busy (503)
                # ------------------------------------
                elif "503" in error_message or "UNAVAILABLE" in error_message:

                    answer = """
## ⚠️ Gemini is Busy

The Gemini servers are currently experiencing high demand.

Please try again in a few moments.
"""

                    st.warning(answer)

                # ------------------------------------
                # Any Other Error
                # ------------------------------------
                else:

                    answer = f"""
## ❌ Unexpected Error

{error_message}
"""

                    st.error(answer)

    # ------------------------
    # Save Assistant Message
    # ------------------------

    st.session_state.messages.append({

        "role": "assistant",

        "content": answer

    })
    # ============================================================
# Retrieved Knowledge
# ============================================================

if question:

    with st.expander("📚 Retrieved Knowledge (Top 3 Matches)", expanded=False):

        for i, result in enumerate(search_results, start=1):

            topic = result["topic_data"]

            st.markdown(f"### {i}. {topic.get('topic')}")

            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Module:** {topic.get('module')}")

            with col2:
                st.write(f"**Similarity:** {result['score']:.4f}")

            st.write("**Summary**")
            st.info(topic.get("summary", "No Summary"))

            if topic.get("navigation"):

                st.write("**Navigation**")

                for nav in topic["navigation"]:

                    st.markdown(f"- {nav}")

            st.divider()

#animations

st.markdown("""
<style>

.typing-container{
    display:flex;
    justify-content:center;
    align-items:center;
    margin:20px 0 30px 0;
}

.typing-text{
    font-size:36px;
    font-weight:700;
    color:#FFD54F;
    overflow:hidden;
    white-space:nowrap;
    border-right:3px solid #FFD54F;
    animation:typing 4s steps(55,end), blink .8s infinite;
}

@keyframes typing{
    from{width:0;}
    to{width:100%;}
}

@keyframes blink{
    50%{
        border-color:transparent;
    }
}

</style>

<div class="typing-container">
<div class="typing-text">

🧠 Different Questions • Same Meaning • Same Accurate Answer

</div>
</div>

""", unsafe_allow_html=True)



# ============================================================
# Suggested Questions
# ============================================================

st.markdown("---")
st.subheader("💡 Suggested Questions")

col1, col2 = st.columns(2)

with col1:

    if st.button(
        "💰 How do I collect student fees?",
        use_container_width=True
    ):
        st.session_state.pending_question = (
            "How do I collect student fees?"
        )
        st.rerun()

    if st.button(
        "🚌 How do I assign transport?",
        use_container_width=True
    ):
        st.session_state.pending_question = (
            "How do I assign transport to students?"
        )
        st.rerun()

with col2:

    if st.button(
        "👨‍💼 How do I process salary?",
        use_container_width=True
    ):
        st.session_state.pending_question = (
            "How do I process employee salary?"
        )
        st.rerun()

    if st.button(
        "📦 How do I add inventory items?",
        use_container_width=True
    ):
        st.session_state.pending_question = (
            "How do I create a new inventory item?"
        )
        st.rerun()

# ============================================================
# Footer
# ============================================================

st.markdown("---")

st.markdown(
"""
<div style='text-align:center;color:gray;padding:15px;'>

<h4>🤖 OKIE DOKIE OKAI</h4>

<p>AI Powered ERP Assistant</p>

<p>Retrieval-Augmented Generation (RAG)</p>

<p>Knowledge Base • Semantic Search • Gemini AI</p>

</div>
""",
unsafe_allow_html=True
)
