import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
import time
import re

from platforms.code_review_platform import CodeReviewPlatform
from confrig import Config
from utils.formatters import pretty_review, create_summary
from utils.storage import save_report

# Page configuration
st.set_page_config(
    page_title="CRQA - AI Code Review Platform",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for clean styling
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-response {
        background: #f8f9fa;
        border-left: 4px solid #667eea;
        padding: 1.5rem;
        margin: 1rem 0;
        border-radius: 0 8px 8px 0;
    }
    
    .agent-header {
        font-size: 1.2em;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    .summary-item {
        background: white;
        border: 1px solid #e9ecef;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 2rem;
        background-color: #f1f3f4;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

def run_asyncio_task(task):
    return asyncio.run(task)

@st.cache_resource
def init_platform():
    try:
        api_key = Config.get_api_key()
        use_openrouter = Config.use_openrouter()
        platform = CodeReviewPlatform(api_key, use_openrouter)
        return platform, None
    except Exception as e:
        return None, str(e)

def clean_agent_response(raw_content):
    """Extract only clean agent responses from raw content."""
    # Look for agent sections using various patterns
    agent_patterns = [
        r'\[([A-Z_\s]+)\]\s*\n((?:(?!\[)[^\n]*\n?)*)',
        r'🔍\s*\[([A-Z_\s]+)\]\s*\n((?:(?!🔍)[^\n]*\n?)*)',
        r'(\w+\s*SPECIALIST|\w+\s*REVIEWER)\s*:?\s*\n((?:(?!\w+\s*(?:SPECIALIST|REVIEWER))[^\n]*\n?)*)'
    ]
    
    agents_found = []
    
    for pattern in agent_patterns:
        matches = re.finditer(pattern, raw_content, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            agent_name = match.group(1).strip().upper()
            content = match.group(2).strip()
            
            # Clean up content - remove tool calls and technical noise
            clean_content = []
            for line in content.split('\n'):
                line = line.strip()
                # Skip technical/tool call lines
                if any(skip in line.lower() for skip in [
                    'toolcallexecutionevent', 'toolcallsummarymessage', 'call_id=',
                    'is_error=', 'name=', 'metadata=', 'created_at=',
                    'models_usage=', 'function_execution_result'
                ]):
                    continue
                if line and len(line) > 10:  # Only keep substantial content
                    clean_content.append(line)
            
            if clean_content:
                agents_found.append({
                    'name': agent_name,
                    'content': '\n'.join(clean_content)
                })
    
    return agents_found

def extract_summary_points(content):
    """Extract key points for executive summary."""
    summary_points = []
    
    # Look for bullet points or numbered lists
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if any(line.startswith(prefix) for prefix in ['•', '-', '*', '1.', '2.', '3.', '4.', '5.']):
            # Clean up the point
            clean_point = re.sub(r'^[•\-*\d\.]\s*', '', line)
            if len(clean_point) > 20:  # Only substantial points
                summary_points.append(clean_point)
    
    return summary_points[:3]  # Limit to top 3 points

# Initialize platform
platform, init_error = init_platform()

# Header
st.markdown("""
<div class="main-header">
    <h1>🤖 CRQA - AI Code Review Platform</h1>
    <p>Clean, professional code analysis by specialized AI agents</p>
</div>
""", unsafe_allow_html=True)

if init_error:
    st.error(f"❌ Platform initialization failed: {init_error}")
    st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")
    
    review_types = {
        "quick": "⚡ Quick Analysis",
        "comprehensive": "🔍 Comprehensive Review", 
        "security_focused": "🔒 Security Focus",
        "performance_focused": "🚀 Performance Focus"
    }
    
    review_type = st.selectbox(
        "Review Type",
        options=list(review_types.keys()),
        format_func=lambda x: review_types[x],
        index=1
    )

# Main input area
tab1, tab2 = st.tabs(["📝 Paste Code", "📁 Upload File"])

code_input = None
description = None

with tab1:
    code_input = st.text_area(
        "Enter your code:",
        height=300,
        placeholder="# Paste your code here..."
    )
    description = st.text_input("Description (optional):")

with tab2:
    uploaded_file = st.file_uploader("Choose a file", type=["py", "js", "java", "cpp", "txt"])
    if uploaded_file is not None:
        code_input = uploaded_file.read().decode("utf-8")
        description = uploaded_file.name
        st.success(f"✅ Loaded: {uploaded_file.name}")

# Review button
if st.button("🚀 Run Code Review", type="primary", use_container_width=True):
    if not code_input or code_input.strip() == "":
        st.error("❌ Please provide code to review.")
    else:
        with st.spinner("🤖 AI agents analyzing your code..."):
            try:
                result = run_asyncio_task(platform.review_code(
                    code=code_input,
                    description=description or "Code review",
                    review_type=review_type
                ))
                
                if result.get("status") == "completed":
                    raw_review = result.get("review", "")
                    
                    # Extract clean agent responses
                    agents = clean_agent_response(raw_review)
                    
                    if not agents:
                        st.error("❌ Could not extract readable responses from agents.")
                        with st.expander("🔍 Raw Output (Debug)"):
                            st.text(raw_review[:1000] + "..." if len(raw_review) > 1000 else raw_review)
                    else:
                        st.success(f"✅ Review completed! ({len(agents)} agents responded)")
                        
                        # Executive Summary
                        st.markdown("## 📋 Executive Summary")
                        
                        for agent in agents:
                            summary_points = extract_summary_points(agent['content'])
                            if summary_points:
                                agent_icon = {
                                    'CODE_REVIEWER': '🔍',
                                    'CODE REVIEWER': '🔍', 
                                    'SECURITY_SPECIALIST': '🔒',
                                    'SECURITY SPECIALIST': '🔒',
                                    'PERFORMANCE_SPECIALIST': '🚀',
                                    'PERFORMANCE SPECIALIST': '🚀',
                                    'QA_SPECIALIST': '🧪',
                                    'QA SPECIALIST': '🧪'
                                }.get(agent['name'], '🤖')
                                
                                st.markdown(f"""
                                <div class="summary-item">
                                    <strong>{agent_icon} {agent['name'].replace('_', ' ')}</strong><br>
                                    {summary_points[0]}
                                </div>
                                """, unsafe_allow_html=True)
                        
                        # Detailed Analysis
                        st.markdown("## 📊 Detailed Analysis")
                        
                        for agent in agents:
                            agent_icon = {
                                'CODE_REVIEWER': '🔍',
                                'CODE REVIEWER': '🔍',
                                'SECURITY_SPECIALIST': '🔒', 
                                'SECURITY SPECIALIST': '🔒',
                                'PERFORMANCE_SPECIALIST': '🚀',
                                'PERFORMANCE SPECIALIST': '🚀',
                                'QA_SPECIALIST': '🧪',
                                'QA SPECIALIST': '🧪'
                            }.get(agent['name'], '🤖')
                            
                            with st.expander(f"{agent_icon} {agent['name'].replace('_', ' ')} Analysis", expanded=True):
                                # Clean up and format the content
                                content = agent['content']
                                # Remove any remaining technical artifacts
                                content = re.sub(r'type=\'[^\']+\'', '', content)
                                content = re.sub(r'source=\'[^\']+\'', '', content)
                                content = re.sub(r'\s+', ' ', content)  # Normalize whitespace
                                
                                st.markdown(content)
                        
                        # Save report
                        formatted_content = "\n\n".join([
                            f"## {agent['name'].replace('_', ' ')}\n{agent['content']}" 
                            for agent in agents
                        ])
                        
                        report_path = save_report(
                            formatted_content, 
                            description or "streamlit_review", 
                            review_type
                        )
                        
                        # Download button
                        with open(report_path, 'r', encoding='utf-8') as f:
                            report_content = f.read()
                        
                        st.download_button(
                            label="📥 Download Report",
                            data=report_content,
                            file_name=report_path.name,
                            mime="text/markdown"
                        )
                        
                        st.info(f"💾 Report saved as: `{report_path.name}`")
                
                else:
                    st.error(f"❌ Review failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
