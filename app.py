"""
Importance — Customs Clearance Documentation Assistant

A Streamlit-based AI assistant that helps generate customs clearance
documentation for products being imported. Powered by Google Gemini.
"""

import os
import streamlit as st

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from dotenv import load_dotenv

load_dotenv()

# ─── Page Config ────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Importance · Customs Clearance Docs",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom Styling ─────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Global */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Header gradient */
    .main-header {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0ea5e9 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(14, 165, 233, 0.15);
    }
    .main-header h1 {
        color: #fff;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }

    /* Cards */
    .info-card {
        background: linear-gradient(145deg, #1e293b, #0f172a);
        border: 1px solid rgba(14, 165, 233, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .info-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(14, 165, 233, 0.12);
    }
    .info-card h3 {
        color: #0ea5e9;
        font-size: 0.95rem;
        font-weight: 600;
        margin: 0 0 0.5rem 0;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .info-card p {
        color: #cbd5e1;
        font-size: 0.9rem;
        margin: 0;
        line-height: 1.6;
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f172a 0%, #1e293b 100%);
    }
    section[data-testid="stSidebar"] .stMarkdown h2 {
        color: #e2e8f0;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label {
        color: #94a3b8;
    }

    /* Chat messages */
    .stChatMessage {
        border-radius: 12px !important;
        border: 1px solid rgba(14, 165, 233, 0.08) !important;
        margin-bottom: 0.75rem !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.6rem;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        letter-spacing: 0.02em;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
    }

    /* Status badge */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 50px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-connected {
        background: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.3);
    }
    .status-disconnected {
        background: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """You are an expert customs clearance consultant and documentation specialist.
Your role is to help users prepare customs clearance documentation for importing products.

When a user asks about a product, provide:

1. **HS Code Suggestions** — Give the most likely Harmonized System (HS) tariff codes for the product,
   with a brief explanation of each code.

2. **Required Customs Forms** — List the specific forms needed (CBP 7501, CBP 3461, ISF 10+2, etc.)
   and briefly explain what each one is for.

3. **Regulatory Requirements** — Mention any relevant agencies (FDA, USDA APHIS, EPA, CPSC, FCC, etc.)
   and permits/licenses required.

4. **Duty & Tax Information** — Provide estimated duty rates for the HS codes and mention any
   applicable trade agreements or preferential tariffs.

5. **Step-by-Step Clearance Process** — Walk the user through the import clearance steps for this
   specific product.

6. **Common Pitfalls** — Warn about typical documentation mistakes or compliance issues for the product.

Always be precise, practical, and cite specific form numbers and regulations.
If you're unsure about something, say so rather than guessing.
Format your responses with clear headings and bullet points for readability.
"""

SAMPLE_PROMPTS = [
    "I need to import olive oil from Tunisia to the US",
    "Help me with customs docs for electronics components from China",
    "What do I need to clear a shipment of cotton textiles from India?",
    "Import documentation for automotive parts from Germany",
    "Clearance requirements for pharmaceutical ingredients from India",
]


# ─── Gemini Setup ────────────────────────────────────────────────────────────────

def init_gemini():
    """Initialize the Gemini model."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return None
    if not GEMINI_AVAILABLE:
        return None
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=SYSTEM_PROMPT,
    )
    return model


def get_ai_response(model, chat_history: list, user_message: str) -> str:
    """Get AI response from Gemini given conversation history."""
    try:
        # Build the Gemini chat from history
        gemini_history = []
        for msg in chat_history:
            role = "user" if msg["role"] == "user" else "model"
            gemini_history.append({"role": role, "parts": [msg["content"]]})

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(user_message)
        return response.text
    except Exception as e:
        return f"⚠️ **Error communicating with Gemini API:** {str(e)}\n\nPlease check your API key and try again."


# ─── Session State ───────────────────────────────────────────────────────────────

if "messages" not in st.session_state:
    st.session_state.messages = []

if "product_context" not in st.session_state:
    st.session_state.product_context = {}


# ─── Sidebar ─────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## 📋 Product Details")
    st.markdown(
        "<p style='color:#64748b; font-size:0.85rem;'>"
        "Fill in product info to get tailored documentation guidance.</p>",
        unsafe_allow_html=True,
    )

    product_name = st.text_input(
        "Product Name",
        placeholder="e.g. Olive Oil, Electronics, Textiles…",
    )
    product_desc = st.text_area(
        "Description",
        placeholder="Brief description of the product, materials, intended use…",
        height=100,
    )
    origin_country = st.text_input(
        "Country of Origin",
        placeholder="e.g. Tunisia, China, Germany…",
    )
    dest_country = st.text_input(
        "Destination Country",
        value="United States",
        placeholder="e.g. United States",
    )

    st.markdown("---")

    if st.button("🚀 Generate Documentation Guide", use_container_width=True):
        if product_name:
            st.session_state.product_context = {
                "product_name": product_name,
                "description": product_desc,
                "origin": origin_country,
                "destination": dest_country,
            }
            prompt_parts = [
                f"I need customs clearance documentation for importing **{product_name}**."
            ]
            if product_desc:
                prompt_parts.append(f"Product description: {product_desc}")
            if origin_country:
                prompt_parts.append(f"Country of origin: {origin_country}")
            if dest_country:
                prompt_parts.append(f"Destination: {dest_country}")
            prompt_parts.append(
                "Please provide a comprehensive customs clearance documentation guide."
            )
            auto_prompt = " ".join(prompt_parts)
            st.session_state.messages.append({"role": "user", "content": auto_prompt})
            st.session_state._generate = True
        else:
            st.warning("Please enter a product name.")

    st.markdown("---")

    # API status
    model = init_gemini()
    if model:
        st.markdown(
            '<span class="status-badge status-connected">● AI Connected</span>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<span class="status-badge status-disconnected">● AI Offline</span>',
            unsafe_allow_html=True,
        )
        st.caption("Set `GEMINI_API_KEY` in your `.env` file to enable AI responses.")

    st.markdown("---")
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.product_context = {}
        st.rerun()


# ─── Main Area ───────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div class="main-header">
        <h1>📦 Importance · Customs Clearance Docs</h1>
        <p>AI-powered customs documentation assistant for import clearance</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Info cards row
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="info-card">
            <h3>📄 Forms & Filings</h3>
            <p>CBP 7501, CBP 3461, ISF 10+2, ACE submissions, and more — tailored to your product.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        """
        <div class="info-card">
            <h3>🔍 HS Code Lookup</h3>
            <p>Get accurate Harmonized System tariff code suggestions with duty rate estimates.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        """
        <div class="info-card">
            <h3>⚖️ Compliance Check</h3>
            <p>FDA, USDA, EPA, CPSC — know which agencies regulate your product.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("")

# ─── Chat Interface ─────────────────────────────────────────────────────────────

# Show existing messages
for msg in st.session_state.messages:
    avatar = "👤" if msg["role"] == "user" else "📦"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Process auto-generated prompt from sidebar
if st.session_state.get("_generate"):
    st.session_state._generate = False
    if model and st.session_state.messages:
        last_msg = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant", avatar="📦"):
            with st.spinner("Analyzing product & generating documentation guide…"):
                response = get_ai_response(
                    model, st.session_state.messages[:-1], last_msg
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
    elif not model:
        fallback = (
            "⚠️ **AI is not connected.** Please set your `GEMINI_API_KEY` in the `.env` file "
            "and restart the application to enable AI-powered documentation generation."
        )
        st.session_state.messages.append({"role": "assistant", "content": fallback})
        st.rerun()

# Chat input for follow-up questions
if user_input := st.chat_input("Ask about customs clearance documentation…"):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    if model:
        with st.chat_message("assistant", avatar="📦"):
            with st.spinner("Thinking…"):
                response = get_ai_response(
                    model, st.session_state.messages[:-1], user_input
                )
                st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})
    else:
        fallback = (
            "⚠️ **AI is not connected.** Please set your `GEMINI_API_KEY` in the `.env` file "
            "and restart the application."
        )
        with st.chat_message("assistant", avatar="📦"):
            st.markdown(fallback)
        st.session_state.messages.append({"role": "assistant", "content": fallback})

# ─── Empty State ─────────────────────────────────────────────────────────────────

if not st.session_state.messages:
    st.markdown("---")
    st.markdown("### 💡 Try asking about…")
    cols = st.columns(2)
    for i, prompt in enumerate(SAMPLE_PROMPTS):
        col = cols[i % 2]
        with col:
            if st.button(f"  {prompt}", key=f"sample_{i}", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state._generate = True
                st.rerun()
