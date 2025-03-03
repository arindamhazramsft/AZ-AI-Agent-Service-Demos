from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import BingGroundingTool
import asyncio
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize environment variables
AOAI_API_KEY = os.getenv("AOAI_API_KEY")
PROJECT_CONNECTION_STRING = os.getenv("PROJECT_CONNECTION_STRING")
BING_CONNECTION_NAME = os.getenv("BING_CONNECTION_NAME")
MODEL_DEPLOYMENT_NAME = os.getenv("MODEL_DEPLOYMENT_NAME")
MODEL_API_VERSION = os.getenv("MODEL_API_VERSION")
AOAI_ENDPOINT = os.getenv("AOAI_ENDPOINT")

# Initiate Azure Open AI Client
az_model_client = AzureOpenAIChatCompletionClient(
    azure_deployment=MODEL_DEPLOYMENT_NAME,
    model=MODEL_DEPLOYMENT_NAME,
    api_version=MODEL_API_VERSION,
    azure_endpoint=AOAI_ENDPOINT,
    api_key=AOAI_API_KEY
)

# Initiate Azure AI Project Client
project_client = AIProjectClient.from_connection_string(
    credential=DefaultAzureCredential(),
    conn_str=PROJECT_CONNECTION_STRING,
)

# Retrieve the Grounding with Bing Search connection
bing_connection = project_client.connections.get(connection_name=BING_CONNECTION_NAME)
conn_id = bing_connection.id

# Creating Bing Grounding Tools 
async def search_resources_tool(topic: str) -> str:
    """
    A dedicated Bing call focusing on searching educational resources for 'topic'.
    """
    print(f"[search_resources_tool] Fetching educational resources for {topic}...")
    bing = BingGroundingTool(connection_id=conn_id)
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="search_resources_tool_agent",
        instructions=f"Search for educational resources related to {topic}.",
        tools=bing.definitions,
        headers={"x-ms-enable-preview": "true"}
    )

    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=f"Retrieve educational resources for {topic}."
    )
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    messages = project_client.agents.list_messages(thread_id=thread.id)

    project_client.agents.delete_agent(agent.id)

    return messages["data"][0]["content"][0]["text"]["value"]

async def design_activities_tool(topic: str) -> str:
    """
    A dedicated Bing call focusing on designing classroom activities for 'topic'.
    """
    print(f"[design_activities_tool] Designing classroom activities for {topic}...")
    bing = BingGroundingTool(connection_id=conn_id)
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="design_activities_tool_agent",
        instructions=f"Design classroom activities and assessments for {topic}.",
        tools=bing.definitions,
        headers={"x-ms-enable-preview": "true"}
    )

    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=f"Suggest classroom activities and assessments for {topic}."
    )
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    messages = project_client.agents.list_messages(thread_id=thread.id)

    project_client.agents.delete_agent(agent.id)

    return messages["data"][0]["content"][0]["text"]["value"]

async def optimize_engagement_tool(topic: str) -> str:
    """
    A dedicated Bing call focusing on optimizing classroom engagement for 'topic'.
    """
    print(f"[optimize_engagement_tool] Optimizing classroom engagement for {topic}...")
    bing = BingGroundingTool(connection_id=conn_id)
    agent = project_client.agents.create_agent(
        model="gpt-4o",
        name="optimize_engagement_tool_agent",
        instructions=f"Provide strategies to boost student engagement for {topic}.",
        tools=bing.definitions,
        headers={"x-ms-enable-preview": "true"}
    )

    thread = project_client.agents.create_thread()
    message = project_client.agents.create_message(
        thread_id=thread.id,
        role="user",
        content=f"Provide strategies to boost student engagement for {topic}."
    )
    run = project_client.agents.create_and_process_run(thread_id=thread.id, assistant_id=agent.id)
    messages = project_client.agents.list_messages(thread_id=thread.id)

    project_client.agents.delete_agent(agent.id)

    return messages["data"][0]["content"][0]["text"]["value"]

# Creating AI Agent functions
async def search_resources_agent(topic: str) -> str:
    """Agent function for 'search resources', calls search_resources_tool."""
    return await search_resources_tool(topic)

async def design_activities_agent(topic: str) -> str:
    """Agent function for 'design activities', calls design_activities_tool."""
    return await design_activities_tool(topic)

async def optimize_engagement_agent(topic: str) -> str:
    """Agent function for 'optimize engagement', calls optimize_engagement_tool."""
    return await optimize_engagement_tool(topic)

# Defining AI Agents/Assistants
curriculum_content_curator_assistant = AssistantAgent(
    name="curriculum_content_curator",
    model_client=az_model_client,
    tools=[search_resources_agent],
    system_message=(
        "You are the Curriculum Content Curator. "
        "You search and curate educational resources (e.g., articles, videos, interactive simulations) aligned with the curriculum standards. "
        "Do NOT provide any final lesson plan."
    )
)

activity_assessment_designer_assistant = AssistantAgent(
    name="activity_assessment_designer",
    model_client=az_model_client,
    tools=[design_activities_agent],
    system_message=(
        "You are the Activity and Assessment Designer. "
        "You suggest classroom activities and assessments tailored to different learning styles and objectives. "
        "Do NOT provide any final lesson plan."
    )
)

classroom_engagement_optimizer_assistant = AssistantAgent(
    name="classroom_engagement_optimizer",
    model_client=az_model_client,
    tools=[optimize_engagement_agent],
    system_message=(
        "You are the Classroom Engagement Optimizer. "
        "You provide strategies and ideas to boost student engagement, including interactive techniques and digital tool recommendations. "
        "Do NOT provide any final lesson plan."
    )
)

decision_agent_assistant = AssistantAgent(
    name="decision_agent",
    model_client=az_model_client,
    system_message=(
        "You are the Decision Agent. After reviewing the educational resources, activities, and engagement strategies from the other agents, "
        "you generate a cohesive lesson plan and adjust recommendations based on teacher feedback and classroom constraints. "
        "End your response with 'Lesson Plan Finalized' once you finalize the lesson plan."
    )
)

# Defining Termination Conditions and teams
text_termination = TextMentionTermination("Lesson Plan Finalized")
max_message_termination = MaxMessageTermination(10)
termination = text_termination | max_message_termination

lesson_planning_team = RoundRobinGroupChat(
    [
        curriculum_content_curator_assistant,
        activity_assessment_designer_assistant,
        classroom_engagement_optimizer_assistant,
        decision_agent_assistant,
    ],
    termination_condition=termination
)

# Main function to run the lesson planning
async def main():
    topic = "Photosynthesis"
    await Console(
        lesson_planning_team.run_stream(
            task=f"Search and curate educational resources, design activities and assessments, and provide engagement strategies for the topic {topic}. Then generate a cohesive lesson plan."
        )
    )

if __name__ == "__main__":
    asyncio.run(main())