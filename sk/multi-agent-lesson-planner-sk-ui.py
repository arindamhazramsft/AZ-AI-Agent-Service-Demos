import asyncio
import streamlit as st

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion

#######################
# Helper functions and class definitions
#######################

def _create_kernel_with_chat_completion(service_id: str) -> Kernel:
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id))
    return kernel

class ApprovedTerminationStrategy(TerminationStrategy):
    """Terminates when 'approved' is found in Educator's response (case-insensitive)."""
    async def should_agent_terminate(self, agent, history):
        return "approved" in history[-1].content.lower()

# Define agent names and instructions
LESSON_PLANNER_NAME = "LessonPlanner"
LESSON_PLANNER_INSTRUCTIONS = (
    "You are an expert lesson planner. Your task is to research and design a precise, high-level lesson plan regarding "
    "a specific topic provided by an Educator. Your lesson plan should include clear objectives, activities, assessments, "
    "resources, and timing for each section. Ensure that your plan outline is actionable. Only provide a single proposal per response. "
    "Consider suggestions when refining an idea."
)

EDUCATOR_NAME = "Educator"
EDUCATOR_INSTRUCTIONS = (
    "You are an experienced educator. Your role is to review the lesson plan provided by the LessonPlanner and suggest modifications "
    "appropriate to various grade levels (elementary, high school, or college) or other relevant changes. The goal is to determine "
    "if the provided lesson plan is acceptable. If so, state that it is approved; if not, provide insight on how to refine the plan. "
)

#######################
# Streamlit App UI
#######################

# Set dark theme and custom styles for title, buttons, etc.
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
    h1 {
        font-size: 1.5rem !important;
        color: #FFFFFF !important;
    }
    /* Force main area markdown to white */
    div[data-testid="stMarkdownContainer"] * {
        color: #FFFFFF !important;
    }
    /* Sidebar styling: dark background with white text for logs */
    section[data-testid="stSidebar"] {
        background-color: #333333;
        border-right: 2px solid #555555;
    }
    section[data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    /* Style the Submit button */
    button {
        background-color: blue !important;
        color: white !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Multi-Agent Group Chat (Semantic Kernel)")

# Input text for topic and grade.
user_input = st.text_input(
    "Provide your topic and grade to create the lesson planning",
    placeholder="e.g. Incorporating Technology in the Classroom - high school"
)

# Sidebar placeholder for logging conversation steps.
log_placeholder = st.sidebar.empty()
if "conversation_logs" not in st.session_state:
    st.session_state.conversation_logs = []

def log_message(msg: str):
    st.session_state.conversation_logs.append(msg)
    log_placeholder.markdown("\n".join(st.session_state.conversation_logs))

# Placeholder for final result.
result_placeholder = st.empty()

# Function to run the multi-agent conversation asynchronously.
async def run_group_chat(task: str):
    # 1. Create agents.
    agent_lesson_planner = ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("lessonplanner"),
        name=LESSON_PLANNER_NAME,
        instructions=LESSON_PLANNER_INSTRUCTIONS,
    )
    agent_educator = ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("educator"),
        name=EDUCATOR_NAME,
        instructions=EDUCATOR_INSTRUCTIONS,
    )

    # 2. Create a group chat with a termination strategy based on Educator's "approved" reply.
    group_chat = AgentGroupChat(
        agents=[agent_lesson_planner, agent_educator],
        termination_strategy=ApprovedTerminationStrategy(
            agents=[agent_educator],
            maximum_iterations=10,
        ),
    )

    # 3. Add the task to the group chat.
    await group_chat.add_chat_message(message=task)
    log_message(f"# Educator provided task: {task}")

    final_result = None
    # 4. Invoke the group chat and log all conversation messages.
    async for content in group_chat.invoke():
        log_message(f"# {content.name}: {content.content}")
        if content.name == LESSON_PLANNER_NAME:
            final_result = content.content

    return final_result

# When the user clicks Submit, run the conversation.
if st.button("Submit") and user_input:
    # Clear previous logs and result.
    st.session_state.conversation_logs = []
    log_message("### Conversation Started")
    result_placeholder.markdown("Processing...")
    # Build TASK using the user input.
    TASK = f"Design a lesson plan on {user_input}."
    # Run the async conversation.
    final_output = asyncio.run(run_group_chat(TASK))
    if final_output:
        result_placeholder.markdown(f"### Final Lesson Plan (from {LESSON_PLANNER_NAME}):\n\n{final_output}")
    else:
        result_placeholder.markdown("No final output received.")