import asyncio

from semantic_kernel import Kernel
from semantic_kernel.agents import AgentGroupChat, ChatCompletionAgent
from semantic_kernel.agents.strategies import TerminationStrategy
from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion


def _create_kernel_with_chat_completion(service_id: str) -> Kernel:
    kernel = Kernel()
    kernel.add_service(AzureChatCompletion(service_id=service_id))
    return kernel


class ApprovedTerminationStrategy(TerminationStrategy):
    """A termination strategy that terminates the conversation when "approved" is found in Educator's response."""
    async def should_agent_terminate(self, agent, history):
        # Terminate if the last message contains "approved" (case insensitive)
        return "approved" in history[-1].content.lower()


# Define agent names and instructions
LESSON_PLANNER_NAME = "LessonPlanner"
LESSON_PLANNER_INSTRUCTIONS = (
    "You are an expert lesson planner. Your task is to research and design a precise and high-level lesson plan regarding "
    "a specific topic provided by an Educator. Your lesson plan should include clear objectives, activities, assessments, "
    "resources, and timing for each section. Ensure that your plan outline is actionable."
    "Only provide a single proposal per response."
    "Consider suggestions when refining an idea."
)

EDUCATOR_NAME = "Educator"
EDUCATOR_INSTRUCTIONS = (
    "You are an experienced educator. Your role is to review the lesson plan provided by the LessonPlanner and suggest modifications "
    "appropriate to various grade levels (elementary, high school, or college) or other relevant changes. "
    "The goal is to determine if the provided lesson plan is acceptable to use."
    "If so, state that it is approved."
    "If not, provide insight on how to refine suggested copy without example."
)

# The topic or task that the educator provides.
TASK = "Design a lesson plan on Incorporating Technology in the Classroom."

async def main():
    # 1. Create the LessonPlanner agent
    agent_lesson_planner = ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("lessonplanner"),
        name=LESSON_PLANNER_NAME,
        instructions=LESSON_PLANNER_INSTRUCTIONS,
    )

    # 2. Create the Educator agent
    agent_educator = ChatCompletionAgent(
        kernel=_create_kernel_with_chat_completion("educator"),
        name=EDUCATOR_NAME,
        instructions=EDUCATOR_INSTRUCTIONS,
    )

    # 3. Create a group chat with the two agents and a custom termination strategy.
    group_chat = AgentGroupChat(
        agents=[agent_lesson_planner, agent_educator],
        termination_strategy=ApprovedTerminationStrategy(
            agents=[agent_educator],  # termination is based solely on Educator's response.
            maximum_iterations=10,
        ),
    )

    # 4. Add the task to the group chat.
    await group_chat.add_chat_message(message=TASK)
    print(f"# Educator provided task: {TASK}")

    # 5. Invoke the group chat and print the conversation.
    async for content in group_chat.invoke():
        print(f"# {content.name}: {content.content}")

if __name__ == "__main__":
    asyncio.run(main())