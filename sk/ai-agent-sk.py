import asyncio

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
from dotenv import load_dotenv

load_dotenv()

async def main():
    # 1. Create the agent by specifying the service and detailed educational instructions
    agent = ChatCompletionAgent(
        service=AzureChatCompletion(),
        name="CoursePlanner",
        instructions=(
            "You are an educational planning assistant. "
            "Please help the user by creating detailed course and study plans based on the topic provided. "
            "Include different course titles, subtitles, and a planner for one or more semesters."
        )
    )

    # Loop to allow user input repeatedly until "exit" is entered
    while True:
        # Get user input asynchronously
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, "Enter your topic to create the course plan (or type 'exit' to quit): ")
        if user_input.strip().lower() == "exit":
            break

        print(f"# User: {user_input}")
        # 2. Invoke the agent for a response
        response = await agent.get_response(
            messages=user_input,
        )
        # 3. Print the response
        print(f"# {response.name}: {response}")

if __name__ == "__main__":
    asyncio.run(main())