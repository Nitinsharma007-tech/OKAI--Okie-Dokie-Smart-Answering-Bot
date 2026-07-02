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
# ----------------------------
# CSS
# ----------------------------

st.markdown("""
<style>

/* ---------------- Main ---------------- */

.block-container{
    padding-top:3rem;
    padding-bottom:2rem;
    padding-left:2rem;
    padding-right:2rem;
}

/* Hide Streamlit Branding */

#MainMenu{
    visibility:hidden;
}

footer{
    visibility:hidden;
}

header{
    visibility:hidden;
}

/* Sidebar */

[data-testid="stSidebar"]{
    background:#171923;
}

/* Hero Title */

.main-title{

    font-size:50px;

    font-weight:800;

    color:#FFD54F;

    margin-bottom:0px;

    line-height:1.2;

}

.sub-title{

    font-size:20px;

    color:#BDBDBD;

    margin-top:5px;

    margin-bottom:25px;

}

/* Buttons */

.stButton>button{

    width:100%;

    border-radius:12px;

    height:45px;

    background:#262730;

    color:white;

    border:1px solid #444;

    transition:0.3s;

}

.stButton>button:hover{

    background:#FFD54F;

    color:black;

}

/* Metrics */

[data-testid="stMetric"]{

    background:#202123;

    padding:15px;

    border-radius:12px;

}

/* Chat Input */

[data-testid="stChatInput"]{

    padding-top:10px;

}

/* Scrollbar */

::-webkit-scrollbar{

    width:8px;

}

::-webkit-scrollbar-thumb{

    background:#444;

    border-radius:20px;

}

    </style>
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

    st.metric("Knowledge Topics","70")
    st.metric("Top-K Retrieval","3")

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

bot = load_okai()
# ============================================================
# Display Previous Messages
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

# ============================================================
# Chat Input
# ============================================================

question = st.chat_input(
    "Ask anything about the ERP..."
)

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

    if st.button("💰 How do I collect student fees?"):
        question = "How do I collect student fees?"

        st.rerun()

    if st.button("🚌 How do I assign transport?"):

        question = "How do I assign transport to students?"

        st.rerun()

with col2:

    if st.button("👨‍💼 How do I process salary?"):

        question = "How do I process employee salary?"

        st.rerun()

    if st.button("📦 How do I add inventory items?"):

        question = "How do I create a new inventory item?"

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