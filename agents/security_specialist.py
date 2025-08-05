"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.
"""
from autogen_agentchat.agents import AssistantAgent
from tools import security_scan_tool

def create_security_specialist_agent(model_client):
    return AssistantAgent(
        name="security_specialist",
        description="An agent that specializes in code security analysis and vulnerability detection.",
        model_client=model_client,
        tools=[security_scan_tool],
        system_message="""You are a security specialist agent. Your task is to analyze code for security vulnerabilities and provide recommendations for improvement.
You will use the provided tools to scan code for security issues and suggest best practices for secure coding.
You will also provide recommendations for improving code security and best practices.
You will analyze the code for potential security vulnerabilities and suggest best practices for writing secure code.
        """
    )