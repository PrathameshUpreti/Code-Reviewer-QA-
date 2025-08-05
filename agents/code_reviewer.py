"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.
"""
from autogen_agentchat.agents import AssistantAgent
from tools import code_quality_analyzer,analyze_complexity

def create_code_reviewer_agent(model_client):
    return AssistantAgent(
        name="code_reviewer",
        description="An agent that reviews code for quality, security, and complexity.",
        model_client=model_client,
        tools=[
            code_quality_analyzer,
            analyze_complexity
        ],
        system_message="""
You are a code reviewer agent. Your task is to analyze code for quality, security, and complexity.
You will use the provided tools to generate reports on code quality, security vulnerabilities, and complexity metrics. If a syntax-analysis section is present, first explain the errors and suggest fixes, then continue with your normal expertise.
You will also provide recommendations for improving code quality and security.

You will analyze the code for potential issues and suggest best practices for writing clean, maintainable, and secure code.
You will also provide recommendations for improving code quality and security.
        """
    )