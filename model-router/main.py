import os
import asyncio
import streamlit as st
from dotenv import load_dotenv
from openai import AzureOpenAI
import time

# ──────────────────────────────────────────────────────────────
# Environment Setup
# ──────────────────────────────────────────────────────────────
load_dotenv()
ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "").rstrip("/")
API_KEY = os.getenv("AZURE_OPENAI_KEY", "")
API_VERSION = "2024-12-01-preview"
DEPLOYMENT = "model-router"  # adapt if you changed the name

# ──────────────────────────────────────────────────────────────
# Streamlit Page Configuration
# ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Azure OpenAI Model Router Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────────────────────
# Helper Functions
# ──────────────────────────────────────────────────────────────
def get_ai_response(messages, client):
    """Get response from Azure OpenAI with model router"""
    try:
        response = client.chat.completions.create(
            model=DEPLOYMENT,
            messages=messages,
            max_tokens=8192,
            temperature=0.7,
            top_p=0.95,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stream=True
        )

        full_reply = ""
        model_used = "unknown"
        
        # Create placeholder for streaming response
        response_placeholder = st.empty()
        
        for chunk in response:
            # Skip heartbeat / empty-choice events
            if not getattr(chunk, "choices", []):
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            # Stream tokens
            token = delta.content or ""
            if token:
                full_reply += token
                # Update the response in real-time
                response_placeholder.markdown(f"**Response:** {full_reply}▌")

            # Capture model info once
            if model_used == "unknown" and hasattr(chunk, 'model'):
                model_used = chunk.model

            # Check for completion
            if choice.finish_reason is not None:
                break
        
        # Final update without cursor
        response_placeholder.markdown(f"**Response:** {full_reply}")
        
        return full_reply, model_used
        
    except Exception as e:
        st.error(f"Error getting AI response: {str(e)}")
        return None, None

def validate_environment():
    """Validate required environment variables"""
    if not ENDPOINT:
        st.error("❌ AZURE_OPENAI_ENDPOINT is not set. Please check your .env file.")
        return False
    if not API_KEY:
        st.error("❌ AZURE_OPENAI_KEY is not set. Please check your .env file.")
        return False
    return True

# ──────────────────────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────────────────────
def main():
    # Header
    st.title("🤖 Azure OpenAI Model Router Demo")
    st.markdown("---")
    
    # Sidebar for configuration and info
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info(f"**Endpoint:** {ENDPOINT if ENDPOINT else 'Not set'}")
        st.info(f"**Deployment:** {DEPLOYMENT}")
        st.info(f"**API Version:** {API_VERSION}")
        
        st.header("📝 About")
        st.markdown("""
        This demo showcases Azure OpenAI's **Model Router** capability:
        
        - Ask any question
        - The router automatically selects the best model
        - See which model was used for each response
        - View conversation history
        """)
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
            st.session_state.model_history = []
            st.rerun()

    # Validate environment
    if not validate_environment():
        st.stop()

    # Initialize session state
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "system", "content": "You are a helpful assistant."}]
    
    if "model_history" not in st.session_state:
        st.session_state.model_history = []

    # Initialize client (using synchronous client like in your reference)
    if "client" not in st.session_state:
        st.session_state.client = AzureOpenAI(
            api_version=API_VERSION,
            azure_endpoint=ENDPOINT,
            api_key=API_KEY,
        )

    # Main chat interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("💬 Chat Interface")
        
        # Display chat history (excluding system message)
        for i, message in enumerate(st.session_state.messages[1:], 1):
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            elif message["role"] == "assistant":
                with st.chat_message("assistant"):
                    st.write(message["content"])
                    # Show which model was used
                    if i-1 < len(st.session_state.model_history):
                        model_info = st.session_state.model_history[i-1]
                        st.caption(f"🎯 **Model used:** `{model_info}`")

        # Chat input
        if user_input := st.chat_input("Ask me anything..."):
            # Add user message to chat
            with st.chat_message("user"):
                st.write(user_input)
            
            # Add user message to session state
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # Get AI response
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking..."):
                    response, model_used = get_ai_response(st.session_state.messages, st.session_state.client)
                    
                    if response:
                        # Add assistant message to session state
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.session_state.model_history.append(model_used)
                        
                        # Show model info
                        st.caption(f"🎯 **Model used:** `{model_used}`")
                    else:
                        st.error("Failed to get response from AI")

    with col2:
        st.header("📊 Model Usage History")
        
        if st.session_state.model_history:
            # Show model usage statistics
            from collections import Counter
            model_counts = Counter(st.session_state.model_history)
            
            st.subheader("Model Distribution")
            for model, count in model_counts.items():
                percentage = (count / len(st.session_state.model_history)) * 100
                st.metric(
                    label=model.replace("gpt-", "GPT-"),
                    value=f"{count} uses",
                    delta=f"{percentage:.1f}%"
                )
            
            st.subheader("Recent Usage")
            # Show last 5 model selections
            recent_models = st.session_state.model_history[-5:]
            for i, model in enumerate(reversed(recent_models)):
                st.text(f"{len(recent_models)-i}. {model}")
        else:
            st.info("No conversations yet. Start chatting to see model usage!")

if __name__ == "__main__":
    main()