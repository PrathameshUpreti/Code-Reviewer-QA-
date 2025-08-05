"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.
"""
from autogen_agentchat.agents import AssistantAgent
from tools import generate_test_cases, security_scan_tool

def create_qa_specialist_agent(model_client):
    """
    Create a QA specialist agent that can analyze code quality and generate test cases.

    Args:
        model_client: The model client to use for the agent.

    Returns:
        An AssistantAgent instance configured for QA tasks.
    """
    return AssistantAgent(
        name="qa_specialist",
        description="An agent that analyzes code quality and generates test cases.",
        tools=[
            generate_test_cases,
            security_scan_tool
        ],
        model_client=model_client,
        system_message="""You are a QA specialist agent. Your task is to analyze code quality and generate test cases.
You will use the provided tools to assess code quality, identify potential issues, and generate test cases to ensure code reliability.
You will also provide recommendations for improving code quality and security.
You will analyze the code for potential issues and suggest best practices for writing clean, maintainable,
        """
    )