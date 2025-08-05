"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.
"""
from autogen_agentchat.agents import AssistantAgent
from tools import analyze_complexity

def create_performance_specialist_agent(model_client):
    """
    Create a performance specialist agent that can analyze code performance and suggest optimizations.

    Args:
        model_client: The model client to use for the agent.

    Returns:
        An AssistantAgent instance configured for performance analysis tasks.
    """
    return AssistantAgent(
        name="performance_specialist",
        description="An agent that analyzes code performance and suggests optimizations.",
        tools=[
            analyze_complexity
           
        ],
        model_client=model_client,
        system_message="""You are a performance specialist agent. Your task is to analyze code for performance issues and suggest optimizations.
You will use the provided tools to generate reports on code performance and recommend best practices for improving efficiency.
You will also provide recommendations for improving code performance and efficiency.
You will analyze the code for potential performance bottlenecks and suggest best practices for writing efficient code
        """
    )