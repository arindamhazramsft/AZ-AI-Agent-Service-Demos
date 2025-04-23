import asyncio
import streamlit as st

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize session state for chat history and execution log
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "log_steps" not in st.session_state:
    st.session_state.log_steps = []

def log_step(step: str):
    st.session_state.log_steps.append(step)
    # Update the sidebar using the placeholder if available.
    if "sidebar_placeholder" in st.session_state:
        st.session_state["sidebar_placeholder"].markdown("\n".join(st.session_state.log_steps))

async def get_agent_response(topic: str):
    log_step("Initializing agent...")
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="CoursePlanner",
        instructions=(
            "You are an educational planning assistant. "
            "Please help the user by creating detailed course and study plans based on the topic provided. "
            "Include different course titles, subtitles, and a planner for one or more semesters."
        )
    )
    log_step(f"Agent initialized. Processing input: {topic}")
    response = await agent.get_response(messages=topic)
    log_step("Received response from agent.")
    return response

def reset_chat():
    st.session_state.chat_history = []
    st.session_state.log_steps = []
    log_step("Chat history and logs have been reset.")

def main():
    # CSS overrides...
    st.markdown(
        """
        <style>
        body {
            background-color: #333333;
            color: #FFFFFF;
        }
        .stApp {
            background-color: #333333;
        }
        /* Override title style */
        h1 {
            font-size: 1.2rem !important;
            color: #FFFFFF !important;
        }
        /* Force main area markdown to white */
        div[data-testid="stMarkdownContainer"] * {
            color: #FFFFFF !important;
        }
        /* Sidebar styling: force text to black */
        section[data-testid="stSidebar"] {
            background-color: #333333;
            border-right: 2px solid #555555;
        }
        section[data-testid="stSidebar"] * {
            color: #FFFFFF !important;
        }
        /* Button styling – using first-of-type and last-of-type for buttons */
        div[data-testid="stHorizontalBlock"] div.stButton button:first-of-type {
            background-color: blue !important;
            color: white !important;
        }
        div[data-testid="stHorizontalBlock"] div.stButton button:last-of-type {
            background-color: blue !important;
            color: white !important;
        }
        /* Download button styling: blue background with white text */
        div[data-testid="stDownloadButton"] button {
            background-color: blue !important;
            color: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
    
    st.title("Couse Planner Assistant(Semantic Kernel)")
    
    # Sidebar for streaming logs (text forced to black)
    st.sidebar.title("Execution Log")
    sidebar_placeholder = st.sidebar.empty()
    st.session_state["sidebar_placeholder"] = sidebar_placeholder
    sidebar_placeholder.markdown("\n".join(st.session_state.log_steps))
    
    # Text input for topic
    topic = st.text_input(
        "Enter your topic to create a course plan",
        placeholder="e.g., Artificial Intelligence in Education"
    )
    
    # Horizontal container for Submit and Reset buttons
    col_buttons = st.columns(2)
    submit_clicked = col_buttons[0].button("Submit")
    reset_clicked = col_buttons[1].button("Reset")
    
    if reset_clicked:
        reset_chat()
        if hasattr(st, "experimental_rerun"):
            st.experimental_rerun()
        else:
            st.write("Please refresh your browser to restart the chat.")
    
    # Process response if Submit is clicked and topic provided.
    if submit_clicked and topic:
        # Display user message with avatar :male-office-worker:
        user_avatar = ":male-office-worker:"
        st.markdown(f"{user_avatar} **User:** {topic}")
        st.session_state.chat_history.append(f"User: {topic}")
        
        # Synchronously run the async agent call
        response = asyncio.run(get_agent_response(topic))
        agent_response_md = str(response)
        
        # Display assistant response in Markdown with avatar :robot_face:
        assistant_avatar = ":robot_face:"
        st.markdown(f"{assistant_avatar} **CoursePlanner:**\n\n{agent_response_md}")
        st.session_state.chat_history.append(f"CoursePlanner: {agent_response_md}")
        
        # Provide a download button for the response
        st.download_button(
            label="Download Response",
            data=agent_response_md,
            file_name="course_plan.md",
            mime="text/markdown"
        )

if __name__ == "__main__":
    main()