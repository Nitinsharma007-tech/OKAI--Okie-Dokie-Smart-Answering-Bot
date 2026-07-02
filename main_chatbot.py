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

.block-container{

    padding-top:2rem;

}

.main-title{

    font-size:42px;

    font-weight:700;

    color:#FFD54F;

}

.sub-title{

    color:gray;

    font-size:18px;

}

.status-card{

    border-radius:15px;

    padding:12px;

    background:#202123;

    margin-bottom:12px;

}

.user-msg{

    background:#2563EB;

    padding:15px;

    border-radius:15px;

    margin-bottom:12px;

}

.bot-msg{

    background:#2D2D2D;

    padding:15px;

    border-radius:15px;

    margin-bottom:12px;

}

.footer{

    text-align:center;

    color:gray;

    margin-top:40px;

}

</style>

""", unsafe_allow_html=True)

# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:

    st.title("🤖 OKAI")

    st.markdown("---")

    st.success("Knowledge Base Loaded")

    st.success("Embeddings Loaded")

    st.success("Gemini Connected")

    st.info("Topics : 70")

    st.info("Top-K Retrieval : 3")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):

        st.session_state.messages=[]

        st.rerun()

# ----------------------------
# Title
# ----------------------------

st.markdown(

'<p class="main-title">🤖 OKIE DOKIE OKAI</p>',

unsafe_allow_html=True

)

st.markdown(

'<p class="sub-title">AI Powered ERP Assistant</p>',

unsafe_allow_html=True

)

st.divider()

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

                answer = f"❌ Error\n\n{e}"

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

# ============================================================
# Knowledge Statistics
# ============================================================

with st.sidebar:

    st.markdown("---")

    st.subheader("📊 AI Statistics")

    st.metric(
        "Knowledge Topics",
        "70"
    )

    st.metric(
        "Retrieved",
        "Top 3"
    )

    st.metric(
        "Embedding Size",
        "384"
    )

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