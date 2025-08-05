"""
Complexity Analyzer Tool
This tool analyzes code complexity, nesting levels, and algorithmic efficiency
"""

import ast
from typing import Dict, List, Any
from autogen_core.tools import FunctionTool

async def analyze_complexity(code: str) -> str:
    """
    Analyze code complexity including cyclomatic complexity and nesting levels.
    This makes your performance agent intelligent about code efficiency!
    """
    
    try:
        # STEP 1: Parse the code
        tree = ast.parse(code)
        
        complexity_data = {
            "function_complexities": {},
            "nesting_levels": {},
            "algorithmic_analysis": {},
            "overall_metrics": {}
        }
        
        # STEP 2: Analyze each function
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        if not functions:
            return "❌ No functions found to analyze complexity."
        
        total_complexity = 0
        max_complexity = 0
        max_nesting = 0
        
        for func in functions:
            func_name = func.name
            
            # STEP 3: Calculate cyclomatic complexity
            # Base complexity is 1, then add 1 for each decision point
            complexity = 1
            decision_nodes = []
            
            for node in ast.walk(func):
                if isinstance(node, ast.If):
                    complexity += 1
                    decision_nodes.append(f"if statement at line {node.lineno}")
                elif isinstance(node, ast.While):
                    complexity += 1
                    decision_nodes.append(f"while loop at line {node.lineno}")
                elif isinstance(node, ast.For):
                    complexity += 1
                    decision_nodes.append(f"for loop at line {node.lineno}")
                elif isinstance(node, ast.Try):
                    complexity += 1
                    decision_nodes.append(f"try block at line {node.lineno}")
                elif isinstance(node, ast.With):
                    complexity += 1
                    decision_nodes.append(f"with statement at line {node.lineno}")
                elif isinstance(node, ast.BoolOp):
                    # Each additional condition in and/or adds complexity
                    complexity += len(node.values) - 1
                    decision_nodes.append(f"boolean operation at line {node.lineno}")
            
            complexity_data["function_complexities"][func_name] = {
                "complexity": complexity,
                "decision_points": decision_nodes,
                "lines": len(ast.unparse(func).splitlines())
            }
            
            # STEP 4: Calculate nesting depth
            def calculate_nesting_depth(node, current_depth=0):
                max_depth = current_depth
                
                for child in ast.iter_child_nodes(node):
                    if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With, ast.FunctionDef, ast.ClassDef)):
                        child_depth = calculate_nesting_depth(child, current_depth + 1)
                        max_depth = max(max_depth, child_depth)
                    else:
                        child_depth = calculate_nesting_depth(child, current_depth)
                        max_depth = max(max_depth, child_depth)
                
                return max_depth
            
            nesting_depth = calculate_nesting_depth(func)
            complexity_data["nesting_levels"][func_name] = nesting_depth
            
            # STEP 5: Analyze algorithmic patterns
            loops = [node for node in ast.walk(func) if isinstance(node, (ast.For, ast.While))]
            nested_loops = 0
            
            for loop in loops:
                inner_loops = [node for node in ast.walk(loop) if isinstance(node, (ast.For, ast.While)) and node != loop]
                if inner_loops:
                    nested_loops += 1
            
            # Estimate time complexity
            if nested_loops >= 2:
                time_complexity = "O(n³) or higher - Cubic or worse"
            elif nested_loops == 1:
                time_complexity = "O(n²) - Quadratic"
            elif loops:
                time_complexity = "O(n) - Linear"
            else:
                time_complexity = "O(1) - Constant"
            
            complexity_data["algorithmic_analysis"][func_name] = {
                "loops": len(loops),
                "nested_loops": nested_loops,
                "estimated_time_complexity": time_complexity
            }
            
            # Update overall metrics
            total_complexity += complexity
            max_complexity = max(max_complexity, complexity)
            max_nesting = max(max_nesting, nesting_depth)
        
        # STEP 6: Calculate overall metrics
        avg_complexity = total_complexity / len(functions)
        
        complexity_data["overall_metrics"] = {
            "total_functions": len(functions),
            "average_complexity": avg_complexity,
            "max_complexity": max_complexity,
            "max_nesting_depth": max_nesting,
            "high_complexity_functions": [name for name, data in complexity_data["function_complexities"].items() if data["complexity"] > 10]
        }
        
        # STEP 7: Generate comprehensive report
        report = f"""
🧮 CODE COMPLEXITY ANALYSIS REPORT

📊 OVERALL METRICS:
• Total functions analyzed: {len(functions)}
• Average cyclomatic complexity: {avg_complexity:.1f}
• Maximum complexity: {max_complexity}
• Maximum nesting depth: {max_nesting}
• High complexity functions: {len(complexity_data["overall_metrics"]["high_complexity_functions"])}

📈 FUNCTION-BY-FUNCTION ANALYSIS:

{chr(10).join(f'''🔍 {func_name}:
• Cyclomatic Complexity: {data["complexity"]} {'🟢 (Low)' if data["complexity"] <= 5 else '🟡 (Medium)' if data["complexity"] <= 10 else '🔴 (High)'}
• Nesting Depth: {complexity_data["nesting_levels"][func_name]} levels
• Time Complexity: {complexity_data["algorithmic_analysis"][func_name]["estimated_time_complexity"]}
• Lines of Code: {data["lines"]}
• Decision Points: {len(data["decision_points"])}''' 
             for func_name, data in complexity_data["function_complexities"].items())}

🚨 HIGH COMPLEXITY FUNCTIONS:
{chr(10).join(f"• {func}: {complexity_data['function_complexities'][func]['complexity']}" 
             for func in complexity_data["overall_metrics"]["high_complexity_functions"]) if complexity_data["overall_metrics"]["high_complexity_functions"] else "• None found ✅"}

🔄 ALGORITHMIC EFFICIENCY:
{chr(10).join(f"• {func}: {analysis['estimated_time_complexity']} ({analysis['loops']} loops, {analysis['nested_loops']} nested)"
             for func, analysis in complexity_data["algorithmic_analysis"].items())}

💡 COMPLEXITY RECOMMENDATIONS:
• Keep cyclomatic complexity under 10 per function (ideally under 5)
• Limit nesting depth to 4 levels maximum
• Break down functions with complexity > 10 into smaller functions
• Use early returns to reduce nesting
• Consider algorithmic improvements for O(n²) or worse complexity
• Extract complex logic into separate, focused functions

📋 REFACTORING PRIORITIES:
{chr(10).join(f"• {func} - Complexity: {data['complexity']}, Nesting: {complexity_data['nesting_levels'][func]}"
             for func, data in complexity_data["function_complexities"].items() 
             if data["complexity"] > 10 or complexity_data["nesting_levels"][func] > 4)[:5] if any(data["complexity"] > 10 or complexity_data["nesting_levels"][func_name] > 4 for func_name, data in complexity_data["function_complexities"].items()) else "• No immediate refactoring needed ✅"}

🎯 COMPLEXITY SCORE: {max(0, 100 - (max_complexity - 5) * 5 - (max_nesting - 3) * 10):.0f}/100

📈 COMPLEXITY LEVEL: {
    "🟢 Excellent" if avg_complexity <= 3 else
    "🟡 Good" if avg_complexity <= 5 else
    "🟠 Fair" if avg_complexity <= 10 else
    "🔴 Needs Refactoring"
}
"""
        
        return report
        
    except SyntaxError as e:
        return f"❌ Syntax Error: Cannot analyze complexity for code with syntax errors: {e}"
    
    except Exception as e:
        return f"❌ Error analyzing complexity: {str(e)}"

# Create the complexity analyzer tool
complexity_analyzer_tool = FunctionTool(
    name="analyze_complexity",
    description="Analyze code complexity including cyclomatic complexity, nesting levels, and algorithmic efficiency",
    func=analyze_complexity
)

