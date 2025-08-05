import re
import textwrap
from typing import List

def pretty_review(raw: str, width: int = 100) -> str:
   
    
    # Look for agent messages using a more flexible pattern
    # This catches both [AGENT]: content and source='agent' content='...' patterns
    patterns = [
        r'\[([A-Z_\s]+)\]\s*(.*?)(?=\n\[|$)',  # [AGENT] format
        r"source='([^']+)'.*?content='([^']*)'",  # AutoGen format
    ]
    
    sections = []
    
    for pattern in patterns:
        matches = re.findall(pattern, raw, re.DOTALL | re.IGNORECASE)
        for match in matches:
            if len(match) == 2:
                speaker = match[0].strip().upper().replace('_', ' ')
                content = match[1].strip()
                
                # Skip empty content or system prompts
                if content and len(content) > 10 and not content.startswith('You are tasked'):
                    # Clean up the content
                    content = content.replace('\\n', '\n')
                    content = re.sub(r'\s+', ' ', content)  # normalize whitespace
                    
                    # Wrap the content
                    wrapped = textwrap.fill(content, width=width, subsequent_indent='    ')
                    sections.append(f"🔍 [{speaker}]\n{wrapped}")
    
    return '\n\n'.join(sections) if sections else "⚠️ Could not extract readable content from review"


def create_summary(review_text: str) -> str:
    """Creates a brief summary from the review text."""
    lines = review_text.split('\n')
    summary_points = []
    
    current_agent = ""
    for line in lines:
        if line.startswith('🔍 ['):
            current_agent = line.replace('🔍 [', '').replace(']', '')
        elif line.strip() and not line.startswith('    '):
            # Take first sentence of each agent's response
            first_sentence = line.split('.')[0] + '.'
            if len(first_sentence) > 20:  # Only if meaningful
                summary_points.append(f"• {current_agent}: {first_sentence}")
    
    return "\n".join(summary_points[:4])  # Limit to 4 key points
