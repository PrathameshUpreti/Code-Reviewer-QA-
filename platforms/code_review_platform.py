"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.
"""
from workflows.code_review_workflow import CodeReviewWorkflow

from agents import (
    create_code_reviewer_agent,
    create_security_specialist_agent,
    create_qa_specialist_agent,
    create_performance_specialist_agent

)
from tools import (
    code_quality_analyzer,  
    security_scan_tool,
    generate_test_cases,
    analyze_complexity
)

from autogen_ext.models.openai import OpenAIChatCompletionClient

class CodeReviewPlatform:
    def __init__(self, api_key, use_openrouter=True):

        if use_openrouter:
            self.model_client = OpenAIChatCompletionClient(
                model="deepseek/deepseek-r1",
                api_key=api_key,
                api_base="https://openrouter.ai/v1",
                model_info={"function_calling": True, "vision": False, "json_output": False, "family": "deepseek", "structured_output": True}  # Adjust model_info as needed
            )
        else:
            self.model_client = OpenAIChatCompletionClient(
                model="gpt-4o",
                api_key=api_key,
                base_url="https://api.openai.com/v1"

            )
        self.agents = {
            "code_reviewer": create_code_reviewer_agent(self.model_client),
            "security_specialist": create_security_specialist_agent(self.model_client),
            "qa_specialist": create_qa_specialist_agent(self.model_client),
            "performance_specialist": create_performance_specialist_agent(self.model_client)
        }
       

        self.workflow = CodeReviewWorkflow(self.agents)

    async def review_code(self, code, description="code review",review_type="comprehensive"):
            """
            Run the code review workflow with the provided code and description.

            Args:
                code (str): The code to be reviewed.
                description (str): A brief description of the code.
                review_type (str): The type of review to perform (e.g., "comprehensive", "security", "qa").

            Returns:
                dict: The results of the code review.
            """
            return await self.workflow.run_review(code, description, review_type)
    
    