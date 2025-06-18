import streamlit as st
import os
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.agents.models import ListSortOrder

load_dotenv()

def init_client():
    client = AIProjectClient(
        credential=DefaultAzureCredential(),
        endpoint=os.getenv("AZURE_AI_PROJECT_ENDPOINT")
    )
    return client, os.getenv("ORCHESTRATOR_AGENT_ID")

def send_message(client, agent_id, thread_id, message):
    client.agents.messages.create(thread_id=thread_id, role="user", content=message)
    run = client.agents.runs.create_and_process(thread_id=thread_id, agent_id=agent_id)
    
    if run.status == "failed":
        return f"Error: {run.last_error}", None
    
    messages = client.agents.messages.list(thread_id=thread_id, order=ListSortOrder.DESCENDING)
    for msg in messages:
        if msg.role == "assistant" and msg.text_messages:
            return msg.text_messages[-1].text.value, run.id
    return "No response", None

def show_agent_flow(client, thread_id, run_id):
    try:
        steps = client.agents.runs.steps.list(thread_id=thread_id, run_id=run_id)
        with st.expander("🔍 Agent Flow"):
            for i, step in enumerate(steps):
                st.write(f"**Step {i+1}:** {step.type} - {step.status}")
                if hasattr(step, 'step_details') and step.step_details and hasattr(step.step_details, 'tool_calls'):
                    for tool in step.step_details.tool_calls or []:
                        if tool.type == 'function':
                            st.write(f"   🔧 {tool.function.name}")
    except:
        pass

st.set_page_config(page_title="Educational Assistant", page_icon="🎓")
st.title("🎓 Educational Assistant")

# Initialize
if 'client' not in st.session_state:
    try:
        client, agent_id = init_client()
        thread = client.agents.threads.create()
        st.session_state.update({
            'client': client, 'agent_id': agent_id, 'thread_id': thread.id, 'runs': []
        })
        st.success("✅ Connected!")
    except Exception as e:
        st.error(f"❌ {e}")
        st.stop()

# Sidebar
with st.sidebar:
    samples = [
        "What courses are offered by Contoso University?",
        "Generate a quiz on Sports Cricket",
        "Create a quiz about available courses"
    ]
    for i, sample in enumerate(samples):
        if st.button(sample, key=i):
            st.session_state.question = sample

# Input
question = st.text_area("Ask your question:", 
                       value=st.session_state.get('question', ''), 
                       height=100)
if st.session_state.get('question'):
    st.session_state.question = ''

if st.button("Send", type="primary") and question:
    with st.spinner("Processing..."):
        response, run_id = send_message(
            st.session_state.client, 
            st.session_state.agent_id, 
            st.session_state.thread_id, 
            question
        )
        if run_id:
            st.session_state.runs.append(run_id)
        st.rerun()

# Conversation
st.header("💬 Conversation")
messages = st.session_state.client.agents.messages.list(
    thread_id=st.session_state.thread_id, 
    order=ListSortOrder.DESCENDING
)

run_idx = 0
for msg in messages:
    if msg.text_messages:
        role = "🙋‍♂️ You" if msg.role == "user" else "🤖 Assistant"
        st.markdown(f"**{role}:** {msg.text_messages[-1].text.value}")
        
        if msg.role == "assistant" and run_idx < len(st.session_state.runs):
            show_agent_flow(st.session_state.client, st.session_state.thread_id, 
                          st.session_state.runs[-(run_idx+1)])
            run_idx += 1
        st.divider()