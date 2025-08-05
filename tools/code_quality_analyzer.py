import ast
import re
from typing import List, Dict, Any

from autogen_core.tools import FunctionTool

async def code_quality_analyzer(code: str, language:str ="python") -> str:
    """
    Comprehensive code quality analysis with detailed metrics.
    
    Args:
        code: Source code to analyze
        language: Programming language (default: python)
        
    Returns:
        Detailed analysis report with quality score
    """
    analysis_results={
        "sysntex_errors": [],
        "complexity_metrics": {},
        "style_issues": [],
        "sugestions": [],
        "quality_score": 0.0
    }
    try:
        tree= ast.parse(code)


        # We are extracting code components like functions, classes, and imports
        # This can be extended to include more detailed analysis as needed

        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        imports = [node for node in ast.walk(tree) if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom)]

        lines=code.splitlines()
        non_empty_lines = [line for line in lines if line.strip()]
        comment_lines = [line for line in lines if line.strip().startswith("#")]

        analysis_results["complexity_metrics"] = {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines),
            "comment_lines": len(comment_lines),
            "functions_count": len(functions),
            "classes_count": len(classes),
            "imports_count": len(imports),
            "comment_ratio": len(comment_lines) / max(len(non_empty_lines), 1) * 100,
            "avg_function_lines": sum(len(ast.unparse(func).splitlines()) for func in functions) / max(len(functions), 1),
            "max_function_lines": max([len(ast.unparse(func).splitlines()) for func in functions] or [0])
        }

        # Example style issues (can be extended with more sophisticated checks)
        for i, line in enumerate(lines, start=1):
            if len(line) > 80:
                analysis_results["style_issues"].append(f"Line {i}: Exceeds 80 characters")
            if line.rsplit() !=line:
                analysis_results["style_issues"].append(f"Line {i}: Trailing whitespace")
            if ';' in line and not line.strip().startswith('#'):
                analysis_results["style_issues"].append(f"Line {i}: Multiple statements on one line")

        
        for func in functions:
            func_line= len(ast.unparse(func).splitlines() )
            if func_line>50:
                analysis_results["sugestions"].append(f"Function '{func.name}' has too many lines ({func_line}). Consider refactoring.")

            has_docstring= (func.body and isinstance(func[0], ast.Expr) and isinstance(func[0].value, ast.Constant) and isinstance(func[0].value.value, str))
            if not has_docstring:
                analysis_results["sugestions"].append(f"Function '{func.name}' lacks a docstring. Consider adding one for better documentation.")

        base_score = 100
        base_score -= len(analysis_results["sysntex_errors"]) * 25
        base_score -= min(len(analysis_results["style_issues"]) * 2, 30)
        base_score -= max(0, (analysis_results["complexity_metrics"]["max_function_lines"] - 30) * 0.5)
        if analysis_results["complexity_metrics"]["comment_ratio"] > 10:
            base_score += 5
        if len(analysis_results["suggestions"]) == 0:
            base_score += 10
            
        analysis_results["quality_score"] = max(0, min(100, base_score))
        
    except SyntaxError as e:
        analysis_results["syntax_errors"].append(f"Syntax error at line {e.lineno}: {e.msg}")
        analysis_results["quality_score"] = 20
    except Exception as e:
        analysis_results["syntax_errors"].append(f"Analysis error: {str(e)}")
        analysis_results["quality_score"] = 30



        # Report format
    
    report = f"""
   🔍 Code Quality Analysis Report

    ----------------------------------------        
    📊 Complexity Metrics:
    -Total lines: {analysis_results['complexity_metrics'].get('total_lines', 0)}
    -Code lines: {analysis_results['complexity_metrics'].get('code_lines', 0)}
    -Comment lines: {analysis_results['complexity_metrics'].get('comment_lines', 0)}
    -Functions count: {analysis_results['complexity_metrics'].get('functions_count', 0)}
    -Classes count: {analysis_results['complexity_metrics'].get('classes_count', 0)}
    -Imports count: {analysis_results['complexity_metrics'].get('imports_count', 0)}
    -Comment ratio: {analysis_results['complexity_metrics'].get('comment_ratio', 0):.1f}%
    -Average function lines: {analysis_results['complexity_metrics'].get('avg_function_lines', 0):.1f}
    -Max function lines: {analysis_results['complexity_metrics'].get('max_function_lines', 0)} lines

    ----------------------------------------
    
    ❌ SYNTAX ERRORS ({len(analysis_results['syntax_errors'])}):
{chr(10).join(f"• {error}" for error in analysis_results['syntax_errors']) if analysis_results['syntax_errors'] else "• None found ✅"}

⚠️ STYLE ISSUES ({len(analysis_results['style_issues'])}):
{chr(10).join(f"• {issue}" for issue in analysis_results['style_issues'][:5]) if analysis_results['style_issues'] else "• None found ✅"}
{f"• ... and {len(analysis_results['style_issues']) - 5} more issues" if len(analysis_results['style_issues']) > 5 else ""}

💡 SUGGESTIONS ({len(analysis_results['suggestions'])}):
{chr(10).join(f"• {suggestion}" for suggestion in analysis_results['suggestions']) if analysis_results['suggestions'] else "• Code follows good practices!"}

🏆 OVERALL QUALITY SCORE: {analysis_results['quality_score']:.0f}/100
    ----------------------------------------
    
    📋 Detailed Analysis:
    - Functions: {len(functions)} found
    - Classes: {len(classes)} found
    - Imports: {len(imports)} found

    ----------------------------------------
    
    🔗 For more information, refer to the documentation of the code quality analyzer tool.

📈 QUALITY RATING: {
    "Excellent" if analysis_results['quality_score'] >= 90 else
    "Good" if analysis_results['quality_score'] >= 75 else
    "Fair" if analysis_results['quality_score'] >= 60 else
    "Needs Improvement" if analysis_results['quality_score'] >= 40 else
    "Poor"
}
"""
    return report

# Tool definition for integration with autogen_agentchat
code_quality_tool = FunctionTool(
    name="code_quality_analyzer",
    description="Analyzes the quality of code and provides a report.",
    func=code_quality_analyzer
)


