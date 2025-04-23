import os
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, MessageAttachment, FilePurpose
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

load_dotenv()

project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(), conn_str=os.getenv('PROJECT_CONNECTION_STRING')
)

with project_client:
    # upload a local file and store it in vector database managed by MS

    #upload a file
    file = project_client.agents.upload_file_and_poll(file_path='ContosoUniversityFAQ.pdf', purpose=FilePurpose.AGENTS)
    print(f"Uploaded file, file ID: {file.id}")

    # create a vector store with the file you uploaded
    vector_store = project_client.agents.create_vector_store_and_poll(file_ids=[file.id], name="agent_vectorstore")
    print(f"Created vector store, vector store ID: {vector_store.id}")

    # create a file search tool
    file_search_tool = FileSearchTool(vector_store_ids=[vector_store.id])

    # attaching the file search tool to the agent
    agent = project_client.agents.create_agent(
        model=os.getenv('MODEL_DEPLOYMENT_NAME'),
        name="file-search-agent",
        instructions="You are a helpful agent which provides answer onlny from the search data.For other questions, please say 'I don't know'.",
        tools=file_search_tool.definitions,
        tool_resources=file_search_tool.resources,
    )
    print(f"Created agent, agent ID: {agent.id}")

    # Create a thread
    thread = project_client.agents.create_thread()
    print(f"Created thread, thread ID: {thread.id}")

    # Create a message
    # Does Contoso University offer evening or weekend classes? What is (56 * 83)/12+45 ?
    message = project_client.agents.create_message(
        thread_id=thread.id, role="user", content="Does Contoso University offer evening or weekend classes?", attachments=[]
    )
    print(f"Created message, message ID: {message.id}")

    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    print(f"Created run, run ID: {run.id}")

    project_client.agents.delete_vector_store(vector_store.id)
    print("Deleted vector store")

    project_client.agents.delete_agent(agent.id)
    print("Deleted agent")

    # Retrieve and Print Messages in a Clean Format
    messages = project_client.agents.list_messages(thread_id=thread.id)

    messages_data = messages["data"]

    # Sort messages by creation time (ascending)
    sorted_messages = sorted(messages_data, key=lambda x: x["created_at"])

    print("\n--- Thread Messages (sorted) ---")
    for msg in sorted_messages:
        role = msg["role"].upper()
        # Each 'content' is a list; get the first text block if present
        content_blocks = msg.get("content", [])
        text_value = ""
        if content_blocks and content_blocks[0]["type"] == "text":
            text_value = content_blocks[0]["text"]["value"]
        print(f"{role}: {text_value}")