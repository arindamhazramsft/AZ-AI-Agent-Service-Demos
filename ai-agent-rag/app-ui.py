import os
import streamlit as st
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, MessageAttachment, FilePurpose
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

# Initialize project client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.getenv('PROJECT_CONNECTION_STRING')
)

# Streamlit UI
st.title("AI Agent File Search Tool")
st.sidebar.title("Agent Steps")

# File upload
uploaded_file = st.sidebar.file_uploader("Upload a PDF file", type="pdf")
if uploaded_file:
    file_path = os.path.join(os.getcwd(), uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.sidebar.write(f"Uploaded file: {uploaded_file.name}")

    with project_client:
        # Upload the file and create vector store
        file = project_client.agents.upload_file_and_poll(file_path=file_path, purpose=FilePurpose.AGENTS)
        st.sidebar.write(f"Uploaded file, file ID: {file.id}")

        vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="agent_vectorstore")
        st.sidebar.write(f"Created vector store, vector store ID: {vector_store.id}")

        # Create a file search tool
        file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

        # Chat interface
        if "messages" not in st.session_state:
            st.session_state.messages = []

        user_input = st.text_input("Ask a question:")
        if st.button("Send"):
            if user_input:
                # Create an agent
                agent = project_client.agents.create_agent(
                    model=os.getenv('MODEL_DEPLOYMENT_NAME'),
                    name="file-search-agent",
                    instructions="You are a helpful agent which provides answer only from the search data. For other questions, please say 'I don't know'.",
                    tools=file_search_tool.definitions,
                    tool_resources=file_search_tool.resources,
                )
                st.sidebar.write(f"Created agent, agent ID: {agent.id}")

                # Create a thread
                thread = project_client.agents.create_thread()
                st.sidebar.write(f"Created thread, thread ID: {thread.id}")

                # Create a message
                message = project_client.agents.create_message(
                    thread_id=thread.id, role="user", content=user_input, attachments=[]
                )
                st.session_state.messages.append({"role": "user", "content": user_input})
                st.sidebar.write(f"Created message, message ID: {message.id}")

                # Process the run
                run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
                st.sidebar.write(f"Created run, run ID: {run.id}")

                # Retrieve and display messages
                messages = project_client.agents.list_messages(thread_id=thread.id)
                messages_data = messages["data"]
                sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

                for msg in sorted_messages:
                    role = msg["role"].upper()
                    content_blocks = msg.get("content", [])
                    text_value = ""
                    if content_blocks and content_blocks[0]["type"] == "text":
                        text_value = content_blocks[0]["text"]["value"]
                    if role == "ASSISTANT":
                        st.session_state.messages.append({"role": "assistant", "content": text_value})

                # Clean up resources
                project_client.agents.delete_vector_store(vector_store.id)
                st.sidebar.write("Deleted vector store")
                project_client.agents.delete_agent(agent.id)
                st.sidebar.write("Deleted agent")

        # Display chat messages
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                st.write(f"**You:** {msg['content']}")
            else:
                st.write(f"**Assistant:** {msg['content']}")