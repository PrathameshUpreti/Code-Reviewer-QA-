"""
This file is part of the CRQA project, which provides tools for code analysis, including code quality analysis, security scanning, test generation, and complexity analysis.
It is designed to help developers improve the quality and security of their codebases.

"""
"""
Test Case Generator Tool
This tool creates comprehensive test templates for functions and classes
"""

import ast
import re
from typing import List, Dict, Any
from autogen_core.tools import FunctionTool

async def generate_test_cases(code: str, test_framework: str = "pytest") -> str:
    """
    Generate comprehensive test cases for all functions in the code.
    This is what makes your QA agent intelligent about testing!
    """
    
    try:
        # STEP 1: Parse the code to find functions and classes
        tree = ast.parse(code)
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        
        if not functions and not classes:
            return "❌ No functions or classes found to generate tests for."
        
        test_cases = []
        
        # STEP 2: Generate tests for each function
        for func in functions:
            if func.name.startswith('_'):  # Skip private functions
                continue
                
            func_name = func.name
            args = [arg.arg for arg in func.args.args]
            
            # Analyze function to determine test data types
            test_data = []
            for arg in args:
                if any(keyword in arg.lower() for keyword in ['str', 'name', 'text']):
                    test_data.append(f'"{arg}_test"')
                elif any(keyword in arg.lower() for keyword in ['int', 'num', 'count', 'id']):
                    test_data.append('42')
                elif any(keyword in arg.lower() for keyword in ['list', 'arr', 'items']):
                    test_data.append('[1, 2, 3]')
                elif any(keyword in arg.lower() for keyword in ['dict', 'config']):
                    test_data.append('{"key": "value"}')
                elif any(keyword in arg.lower() for keyword in ['bool', 'flag']):
                    test_data.append('True')
                else:
                    test_data.append(f'test_{arg}')
            
            # Generate comprehensive test template
            test_case = f'''
def test_{func_name}_normal_case():
    """Test {func_name} with normal inputs."""
    # Arrange
    {chr(10).join(f"    {arg} = {test_val}" for arg, test_val in zip(args, test_data)) if args else "    # No parameters needed"}
    
    # Act
    result = {func_name}({", ".join(args) if args else ""})
    
    # Assert
    assert result is not None  # TODO: Add specific assertion
    # TODO: Add more specific assertions based on expected behavior

def test_{func_name}_edge_cases():
    """Test {func_name} with edge case inputs."""
    # TODO: Test with boundary values
    # Examples: empty lists, None values, zero, negative numbers
    pass

def test_{func_name}_error_handling():
    """Test {func_name} error handling."""
    # TODO: Test error conditions
    # Example:
    # with pytest.raises(ValueError):
    #     {func_name}(invalid_input)
    pass

@pytest.mark.parametrize("input_data,expected", [
    # TODO: Add parametrized test cases
    # (test_input_1, expected_output_1),
    # (test_input_2, expected_output_2),
])
def test_{func_name}_parametrized(input_data, expected):
    """Parametrized tests for {func_name}."""
    # result = {func_name}(input_data)
    # assert result == expected
    pass
'''
            test_cases.append(test_case)
        
        # STEP 3: Generate tests for classes
        for cls in classes:
            if cls.name.startswith('_'):
                continue
                
            class_name = cls.name
            methods = [node for node in cls.body if isinstance(node, ast.FunctionDef)]
            
            class_test = f'''
class Test{class_name}:
    """Test cases for {class_name} class."""
    
    @pytest.fixture
    def {class_name.lower()}_instance(self):
        """Create {class_name} instance for testing."""
        return {class_name}()
    
    def test_{class_name.lower()}_creation(self):
        """Test {class_name} instance creation."""
        instance = {class_name}()
        assert instance is not None
        # TODO: Add specific assertions about initial state
'''
            
            # Generate tests for public methods
            for method in methods:
                if method.name.startswith('_') and method.name != '__init__':
                    continue
                    
                method_name = method.name
                if method_name == '__init__':
                    continue  # Already covered in creation test
                
                class_test += f'''
    def test_{method_name}(self, {class_name.lower()}_instance):
        """Test {class_name}.{method_name} method."""
        # TODO: Implement test for {method_name}
        # result = {class_name.lower()}_instance.{method_name}()
        # assert result == expected_result
        pass
'''
            
            test_cases.append(class_test)
        
        # STEP 4: Generate complete test file
        imports = f"""
import pytest
import sys
import os

# Add source directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import your modules here
# from your_module import {', '.join([f.name for f in functions] + [c.name for c in classes])}
"""
        
        full_test_file = f"""{imports}

# Generated test file - customize as needed
{chr(10).join(test_cases)}

# Utility functions for testing
def create_test_data():
    \"\"\"Create sample test data.\"\"\"
    return {{
        "sample_string": "test_data",
        "sample_number": 123,
        "sample_list": [1, 2, 3, 4, 5],
        "sample_dict": {{"key1": "value1", "key2": "value2"}}
    }}

if __name__ == "__main__":
    pytest.main([__file__])
"""
        
        return f"""
🧪 TEST CASE GENERATOR REPORT

📊 ANALYSIS SUMMARY:
• Functions found: {len(functions)}
• Classes found: {len(classes)}
• Test methods generated: {len(functions) * 4 + len(classes) * 2}
• Test framework: {test_framework}

📝 GENERATED TEST FILE:
{full_test_file}

💡 TESTING RECOMMENDATIONS:
• Replace TODO comments with actual test implementations
• Add specific assertions based on expected behavior
• Test both positive and negative scenarios
• Use pytest fixtures for setup and teardown
• Implement parametrized tests for multiple input scenarios
• Add integration tests for complex workflows
• Mock external dependencies and API calls
• Aim for >80% code coverage

🚀 NEXT STEPS:
1. Save as test_your_module.py
2. Install pytest: pip install pytest
3. Run tests: pytest test_your_module.py -v
4. Customize tests based on your specific requirements
5. Add more test data and edge cases

🎯 TESTING SCORE: {min(100, len(functions) * 10 + len(classes) * 15)}/100
"""
        
    except SyntaxError as e:
        return f"❌ Syntax Error: Cannot generate tests for code with syntax errors: {e}"
    
    except Exception as e:
        return f"❌ Error generating tests: {str(e)}"

# Create the test generator tool
test_generator_tool = FunctionTool(
    name="generate_test_cases",
    description="Generate comprehensive test cases for functions and classes in code",
    func=generate_test_cases
)

