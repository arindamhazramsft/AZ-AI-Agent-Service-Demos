import os
import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import BingGroundingTool
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Create an Azure AI Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=os.getenv("PROJECT_CONNECTION_STRING"),
)

bing_connection = project_client.connections.get(
    connection_name=os.getenv("BING_CONNECTION_NAME")
)
conn_id = bing_connection.id

# Initialize agent bing tool and add the connection id
bing = BingGroundingTool(connection_id=conn_id)

# Streamlit UI setup
st.set_page_config(page_title="Bing Search Agent Demo", page_icon=":mag:")

# Construct the path to the logo.png file
logo_path = os.path.join(os.path.dirname(__file__), 'logo.png')

st.markdown(
    f"""
    <div style="display: flex; align-items: center;">
        <img src="{logo_path}" width="50" style="margin-right: 10px;">
        <h1>Bing Search Agent Demo</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Chat interface
if 'messages' not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input("You: ", "")
if st.button("Send"):
    # Create agent with the bing tool and process assistant run
    with project_client:
        agent = project_client.agents.create_agent(
            model="gpt-4o",
            name="search-assistant",
            instructions="You are a helpful assistant",
            tools=bing.definitions,
            headers={"x-ms-enable-preview": "true"}
        )
        st.sidebar.write(f"Created agent, ID: {agent.id}")

        # Create thread for communication
        thread = project_client.agents.create_thread()
        st.sidebar.write(f"Created thread, ID: {thread.id}")

        # Create message to thread
        message = project_client.agents.create_message(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )
        st.sidebar.write(f"Created message, ID: {message.id}")

        # Create and process agent run in thread with tools
        run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
        st.sidebar.write(f"Run finished with status: {run.status}")

        # Retrieve run step details to get Bing Search query link
        run_steps = project_client.agents.list_run_steps(run_id=run.id, thread_id=thread.id)
        run_steps_data = run_steps['data']

        if run.status == "failed":
            st.sidebar.write(f"Run failed: {run.last_error}")

        # Fetch and log all messages in chronological order
        messages_response = project_client.agents.list_messages(thread_id=thread.id)
        messages_data = messages_response["data"]

        # Sort messages by creation time (ascending)
        sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

        for msg in sorted_messages:
            role = msg["role"].upper()
            content_blocks = msg.get("content", [])
            text_value = ""
            if content_blocks and content_blocks[0]["type"] == "text":
                text_value = content_blocks[0]["text"]["value"]
            if role == "USER":
                st.session_state.messages.append({"role": "user", "content": text_value})
            else:
                st.session_state.messages.append({"role": "assistant", "content": text_value})

        # Delete the assistant when done
        project_client.agents.delete_agent(agent.id)
        st.sidebar.write("Deleted agent")

# Display chat messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 30px; margin-right: 10px;">👤</span>
                <div style="background-color: #f1f1f1; padding: 10px; border-radius: 5px; color: black;">
                    {msg["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"""
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 30px; margin-right: 10px;">🤖</span>
                <div style="background-color: #e1f5fe; padding: 10px; border-radius: 5px; color: black;">
                    {msg["content"]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )