import re
from typing import List, Dict, Any
from autogen_core.tools import FunctionTool

async def security_scan_tool(code: str, language: str = "python") -> str:
    """
    Perform security analysis on the provided code.
    
    Args:
        code: Source code to analyze
    """
    vunerabilities = []
    security_warnings = []

    # Define the cirtical patterns to search for regarding security issues
    critical_patterns = {
        r'eval\s*\(':{
            "Severity": "CRITICAL",
            "ISSUE":"Code execution vulnerability",
            "DESCRIPTION": "Usage of eval() can lead to code execution vulnerabilities. Avoid using eval() with untrusted input.",
            "SUGGESTION": "Refactor the code to avoid using eval(). Consider using safer alternatives like ast.literal_eval() for parsing literals."},
        r'exec\s*\(':{
            "Severity": "CRITICAL",
            "ISSUE":"Code execution vulnerability",
            "DESCRIPTION": "Usage of exec() can lead to code execution vulnerabilities. Avoid using exec() with untrusted input.",
            "SUGGESTION": "Refactor the code to avoid using exec(). Consider using safer alternatives."},
        
        r'subprocess.*shell\s*=\s*True':{
            "Severity": "HIGH",
            "ISSUE":"Shell injection vulnerability",
            "DESCRIPTION": "Using subprocess with shell=True can lead to shell injection vulnerabilities. Avoid using shell=True with untrusted input.",
            "SUGGESTION": "Refactor the code to use subprocess without shell=True or sanitize inputs."},
         r'pickle\.loads?\s*\(':
            {
            "Severity": "HIGH",
            "ISSUE":"Deserialization vulnerability",
            "DESCRIPTION": "Using pickle.loads() can lead to arbitrary code execution if untrusted data is deserialized.",
            "SUGGESTION": "Avoid using pickle for deserialization. Consider using safer alternatives like json.loads() for JSON data."},
        r'os\.system\s*\(':{
            "Severity": "HIGH",
            "ISSUE":"Command injection vulnerability",
            "DESCRIPTION": "Using os.system() can lead to command injection vulnerabilities. Avoid using os.system() with untrusted input.",
            "SUGGESTION": "Refactor the code to use subprocess.run() or subprocess.Popen() with a list of arguments. Avoid passing untrusted input directly to os.system()."},

        
    }

    credential_patterns = {
        r'api_key\s*=\s*["\'](.*)["\']': {
            "Severity": "HIGH",
            "ISSUE": "Exposed API key",
            "DESCRIPTION": "API keys should not be hardcoded in the source code. This can lead to unauthorized access to services.",
            "SUGGESTION": "Store API keys in environment variables or secure vaults. Avoid hardcoding sensitive information in the source code."},
        r'password\s*=\s*["\'](.*)["\']': {
            "Severity": "HIGH",
            "ISSUE": "Exposed password",
            "DESCRIPTION": "Passwords should not be hardcoded in the source code. This can lead to unauthorized access to services.",
            "SUGGESTION": "Store passwords in environment variables or secure vaults. Avoid hardcoding sensitive information in the source code."}
    }

    medium_patterns = {
        r'input\s*\(':{
            "Severity": "MEDIUM",
            "ISSUE": "Potentially unsafe user input",
            "DESCRIPTION": "User input should be validated and sanitized to prevent injection attacks.",
            "SUGGESTION": "Implement input validation and sanitization for user inputs."},
        r'sql.*["\'](.*)["\']':{
            "Severity": "MEDIUM",   
            "ISSUE": "Potential SQL injection",
            "DESCRIPTION": "SQL queries should be parameterized to prevent SQL injection attacks.",
            "SUGGESTION": "Use parameterized queries or ORM libraries to prevent SQL injection. Avoid concatenating user input directly into SQL queries."},
        r'http[s]?://':{
            "Severity": "MEDIUM",
            "ISSUE": "Hardcoded URL",
            "DESCRIPTION": "Hardcoded URLs can lead to security issues if they point to untrusted sources.",
            "SUGGESTION": "Avoid hardcoding URLs. Use configuration files or environment variables to store URLs."},
    }

    #Combine all patterns into a single dictionary for easier processing
    all_patterns = {**critical_patterns, **credential_patterns, **medium_patterns}

    for pattern, details in all_patterns.items(): # Iterate over each pattern and its details
        # Use regex to find all matches of the pattern in the code
        matches = re.finditer(pattern, code, re.MULTILINE) # Find all matches in the code and iterate over them and multiline to match across lines
        for match in matches:
            # Calculate which line the issue is on
            line_num = code[:match.start()].count('\n') + 1
            vunerabilities.append({
                "pattern": match.group(0),
                "line":line_num,
                "severity": details["Severity"],
                "issue": details["ISSUE"],
                "line_number": code.count('\n', 0, match.start()) + 1,  # Calculate line number
                "details": details
            }) # Append the vulnerability details to the list and calculate the line number like the pattern match above

            #Additional Security check line by line

            line=code.split('/n')

            for i, line in enumerate(line, start=1): # Iterate over each line in the code and start counting from 1
                stripped= line.strip()

                #check for http urls
                if re.search(r'http://(?localhost|127\.0\.0\.1)', stripped): # Check for localhost URLs and strip the line
                    security_warnings.append({
                        "line": i,
                        "issue": "Localhost URL detected",
                        "description": "Using localhost URLs can lead to security issues in production environments.",
                        "suggestion": "Avoid using localhost URLs in production code."
                    })

                #check for hardcoded credentials
                if re.search(r'api\s*=\s*["\'](.*)["\']', stripped):
                    security_warnings.append({
                        "line": i,
                        "issue": "Hardcoded password detected",
                        "description": "Hardcoded passwords can lead to security vulnerabilities.",
                        "suggestion": "Use environment variables or secure vaults to store sensitive information."
                    })
                
                #check for random functions
                if 'random.random()' in stripped or 'random.choice(' in stripped:security_warnings.append({
                "line": i,
                "severity": "MEDIUM", 
                "issue": "Weak random number generation",
                "description": "Use secrets module for cryptographically secure random numbers"
            })
                    
            #calculate the security score based on the number of vulnerabilities found

            critical_count = len([v for v in vunerabilities if v["Severity"] == "CRITICAL"])
            high_count = len([v for v in vunerabilities if v["Severity"] == "HIGH"])
            medium_count = len([v for v in vunerabilities if v["Severity"] == "MEDIUM"])
            low_count = len([v for v in vunerabilities if v["Severity"] == "LOW"])

            security_score= max(0, 100 - (critical_count * 40) - (high_count * 20) - (medium_count * 10) - (low_count * 5))

    # Prepare the security analysis report
    report = f"""
🛡️ SECURITY VULNERABILITY SCAN REPORT

🚨 CRITICAL VULNERABILITIES ({critical_count}):
{chr(10).join(f"• Line {v['line']}: {v['issue']} - {v['description']}" 
              for v in vunerabilities if v['severity'] == 'CRITICAL') if critical_count else "• None found ✅"}

⚠️ HIGH SEVERITY ISSUES ({high_count}):
{chr(10).join(f"• Line {v['line']}: {v['issue']} - {v['description']}"
            for v in vunerabilities if v['severity'] == 'HIGH') if high_count else "• None found ✅"}

🔶 MEDIUM SEVERITY ISSUES ({medium_count}):
{chr(10).join(f"• Line {v['line']}: {v['issue']} - {v['description']}"
            for v in vunerabilities if v['severity'] == 'MEDIUM') if medium_count else "• None found ✅"}

ℹ️ LOW SEVERITY WARNINGS ({low_count}):
{chr(10).join(f"• Line {v['line']}: {v['issue']}"
             for v in security_warnings if v['severity'] == 'LOW') if low_count else "• None found ✅"}

🔒 SECURITY RECOMMENDATIONS:
• Use parameterized queries to prevent SQL injection
• Store secrets in environment variables or secure vaults
• Validate and sanitize all user inputs
• Use HTTPS for all network communications
• Avoid eval(), exec(), and dangerous functions
• Use secure random number generation for security purposes

🛡️ SECURITY SCORE: {security_score:.0f}/100

🎯 SECURITY LEVEL: {
    "Excellent" if security_score >= 95 else
    "Good" if security_score >= 80 else
    "Fair" if security_score >= 60 else
    "Poor" if security_score >= 40 else
    "Critical Risk"
}
"""
    return report

# Define the security scan tool
security_scan_tool = FunctionTool(
    name="security_scan_tool",
    description="Performs security analysis on the provided code to identify vulnerabilities and security issues.",
    func=security_scan_tool,
    
    
)
