# Set up the page layout
import streamlit as st
st.set_page_config(
    page_title="XSLT Updater - Genie",
    page_icon="🛠️",
    layout="wide",
    initial_sidebar_state="expanded"
)

import os
import sys
import difflib
import pandas as pd
import json
import logging
import time
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
from genie_core.xml_processing.xml_utils import *
from genie_core.xslt.xslt_utils import *
from genie_core.llm.llm_response_handler_utils import *
from genie_core.llm.llm_utils import *
from genie_core.prompts.prompt_utils import *
from genie_core.database.database_utils import *
from genie_core.common.user_interaction import init_objects_into_session
import genie_core.common.confluence_utils as confluence_utils
from pathlib import Path

# Import new conversational XSLT updater components
from genie_core.xslt.universal_xslt_analyzer import UniversalXSLTAnalyzer, UniversalPattern
from genie_core.xslt.universal_user_interaction import UniversalUserInteraction, UserIntent
from genie_core.xslt.universal_chunk_extractor import UniversalChunkExtractor
from genie_core.xslt.universal_ai_processor import UniversalAIProcessor, pretty_print_xml

# Enhanced UI styling with advanced features
st.markdown("""
<style>
    /* Button Styling with Animations */
    div.stButton > button:first-child {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    div.stButton > button:first-child::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    div.stButton > button:hover::before {
        left: 100%;
    }
    
    div.stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    div.stDownloadButton > button:first-child {
        background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    div.stDownloadButton > button:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 8px 25px rgba(40, 167, 69, 0.4);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin: 1rem 0 2rem 0;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    .content-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e9ecef;
    }
    
    .status-card {
        background: white;
        padding: 0.8rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 0.8rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .status-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #667eea, #764ba2);
        transform: scaleX(0);
        transition: transform 0.3s ease;
    }
    
    .status-card:hover::before {
        transform: scaleX(1);
    }
    
    .status-card:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-left-color: #5a6fd8;
    }
    
    .status-card h4 {
        color: #2c3e50;
        margin-bottom: 0.3rem;
        font-weight: 600;
        font-size: 1rem;
    }
    
    .status-card p {
        font-size: 0.85rem;
        line-height: 1.3;
        margin: 0;
        color: #666;
    }
    
    .warning-card {
        border-left-color: #ffc107;
        background: #fffbf0;
    }
    
    .error-card {
        border-left-color: #dc3545;
        background: #fff5f5;
    }
    
    .success-card {
        border-left-color: #28a745;
        background: #f0fff4;
    }
    
    .sidebar-container {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .metrics-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .metrics-card h3 {
        margin-top: 0;
        color: white;
    }
    
    .metric-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0;
        border-bottom: 1px solid rgba(255,255,255,0.2);
    }
    
    .metric-item:last-child {
        border-bottom: none;
    }
    
    .metric-value {
        font-weight: bold;
        font-size: 1.1rem;
    }
    
    /* Status Indicators */
    .status-indicator {
        display: inline-flex;
        align-items: center;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin: 0.2rem;
    }
    
    .status-processing {
        background: linear-gradient(135deg, #ffeaa7 0%, #fdcb6e 100%);
        color: #2d3436;
        animation: pulse 2s infinite;
    }
    
    .status-success {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
    }
    
    .status-error {
        background: linear-gradient(135deg, #e17055 0%, #d63031 100%);
        color: white;
    }
    
    .status-idle {
        background: linear-gradient(135deg, #a29bfe 0%, #6c5ce7 100%);
        color: white;
    }
    
    /* Progress Bar */
    .progress-container {
        width: 100%;
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
        overflow: hidden;
        margin: 0.5rem 0;
    }
    
    .progress-bar {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 3px;
        transition: width 0.3s ease;
        animation: shimmer 2s infinite;
    }
    
    /* Collapsible Sections */
    .collapsible-header {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1rem;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #dee2e6;
        margin-bottom: 0.5rem;
    }
    
    .collapsible-header:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .collapsible-content {
        max-height: 0;
        overflow: hidden;
        transition: max-height 0.3s ease;
        background: white;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .collapsible-content.expanded {
        max-height: 1000px;
        padding: 1rem;
        border: 1px solid #dee2e6;
    }
    
    /* Enhanced Code Blocks */
    .code-container {
        position: relative;
        background: #2d3748;
        border-radius: 8px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .code-header {
        background: #1a202c;
        padding: 0.5rem 1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.8rem;
        color: #a0aec0;
    }
    
    .copy-button {
        background: #4a5568;
        color: white;
        border: none;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        cursor: pointer;
        font-size: 0.7rem;
        transition: background 0.2s ease;
    }
    
    .copy-button:hover {
        background: #667eea;
    }
    
    /* Animations */
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200px 0; }
        100% { background-position: calc(200px + 100%) 0; }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Processing Timer */
    .processing-timer {
        display: inline-flex;
        align-items: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-left: 0.5rem;
    }
    
    .timer-icon {
        margin-right: 0.3rem;
        animation: spin 2s linear infinite;
    }
    
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
</style>
""", unsafe_allow_html=True)

# Clear cache button with improved styling
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🔄 Clear All Cache & Conversation", type="primary", use_container_width=True):
        # clear new‐style caches
        try:
            st.cache_data.clear()
            st.cache_resource.clear()
        except AttributeError:
            # fallback for older Streamlit
            st.legacy_caching.clear_cache()

        # clear any memoized calls
        try:
            st.experimental_memo.clear()
        except AttributeError:
            pass

        # wipe out everything in session_state (llm inputs/outputs, html, etc.)
        for key in list(st.session_state.keys()):
            del st.session_state[key]

        # clear any lru_cache on your get_chat_completion
        try:
            get_chat_completion.cache_clear()
        except AttributeError:
            pass
        st.rerun()
    
def display_testing():
    st.markdown("""
    <div class="content-container">
        <h3>🧪 XSLT Testing Suite</h3>
        <p>Upload multiple XML files and an XSLT to test transformations in batch.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced file upload section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**📄 Input XML Files**")
        in_xml = st.file_uploader(
            "Upload XML files to transform", 
            type=["xml"], 
            accept_multiple_files=True,
            help="Select one or more XML files to test your XSLT transformation"
        )
        
        if in_xml:
            st.success(f"✅ Loaded {len(in_xml)} XML file(s)")
            for i, file in enumerate(in_xml):
                st.write(f"• {file.name}")
    
    with col2:
        st.markdown("**🛠️ XSLT File**")
        xslt = st.file_uploader(
            "Upload XSLT transformation", 
            type=["xslt", "xsl"],
            help="Upload the XSLT file to apply to your XML inputs"
        )
        
        if xslt:
            st.success(f"✅ Loaded: {xslt.name}")
    
    # Process files if both are uploaded
    if in_xml and xslt:
        st.markdown("""
        <div class="content-container">
            <h3>🔄 Transformation Results</h3>
        </div>
        """, unsafe_allow_html=True)
        
        xslt_content = xslt.read().decode('utf-8')
        logs = []
        
        # Process each XML file
        for i, xml_file in enumerate(in_xml):
            xml_content = xml_file.read().decode('utf-8')
            
            st.markdown(f"**📄 Result {i+1}: {xml_file.name}**")
            
            try:
                with st.spinner(f'Transforming {xml_file.name}...'):
                    formatted_xml, logs = apply_xslt(xslt_content, xml_content, logs, None)
                
                if formatted_xml:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.success(f"✅ Transformation successful for {xml_file.name}")
                    with col2:
                        st.download_button(
                            label=f"📥 Download",
                            data=formatted_xml,
                            file_name=f"transformed_{xml_file.name}",
                            mime="application/xml",
                            key=f"download_{i}"
                        )
                    
                    # Show transformed XML in expandable section
                    with st.expander(f"📖 View Transformed XML - {xml_file.name}"):
                        st.code(formatted_xml, language='xml', line_numbers=True)
                else:
                    st.error(f"❌ Transformation failed for {xml_file.name}")
                    
            except Exception as e:
                st.markdown(f"""
                <div class="error-card">
                    <h4>❌ Error processing {xml_file.name}</h4>
                    <code>{str(e)}</code>
                </div>
                """, unsafe_allow_html=True)
        
        # Show logs if any
        if logs:
            with st.expander("📋 Transformation Logs"):
                for log in logs:
                    st.text(log)
    
    elif in_xml or xslt:
        missing = "XSLT file" if in_xml else "XML files"
        if in_xml and not xslt:
            missing = "XSLT file"
        elif xslt and not in_xml:
            missing = "XML files"
            
        st.markdown(f"""
        <div class="warning-card">
            <h4>⚠️ Upload Required</h4>
            <p>Please upload the missing <strong>{missing}</strong> to start testing.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card">
            <h4>📤 Ready for Testing</h4>
            <p>Upload your XML files and XSLT to begin batch transformation testing.</p>
            <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; color: #6c757d; margin-top: 1rem;">
                <p>🔄 Waiting for file uploads...</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
            
# Application header with improved styling
st.markdown("""
<div class="main-header">
    <h1>🛠️ XSLT Updater</h1>
    <p>Transform your XSLT files with AI-powered updates and intelligent analysis</p>
</div>
""", unsafe_allow_html=True)

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# Compact feature overview
st.markdown("**🎯 What can you do here?**")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.markdown("""
    <div class="status-card">
        <h4>📝 Update</h4>
        <p>Update XSLT files with AI</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="status-card">
        <h4>⚡ Optimize</h4>
        <p>Test transformations</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="status-card">
        <h4>🔍 Analyze</h4>
        <p>Compare file versions</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="status-card">
        <h4>🧪 Test</h4>
        <p>Batch XML processing</p>
    </div>
    """, unsafe_allow_html=True)

with col5:
    st.markdown("""
    <div class="status-card">
        <h4>📚 Cook-book</h4>
        <p>Manage templates</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
# Main code
update_tab, optimize_tab, analysis_and_review_tab, testing_tab, cook_book_tab = st.tabs(["Update", "Optimize", "Analysis & Review", "Testing", "cook-book"])

shared_agent = setup_agent("GPT4O")
st.session_state.gpt_model_used = "GPT4O"
init_objects_into_session()
with update_tab:
    # Initialize session state variables for the conversational flow
    if 'current_requirement' not in st.session_state:
        st.session_state.current_requirement = None
    if 'operation_status' not in st.session_state:
        st.session_state.operation_status = 'idle'
    if 'processing_start_time' not in st.session_state:
        st.session_state.processing_start_time = None
    if 'patterns_found' not in st.session_state:
        st.session_state.patterns_found = []
    if 'selected_pattern' not in st.session_state:
        st.session_state.selected_pattern = None
    if 'final_action_type' not in st.session_state:
        st.session_state.final_action_type = None
    if 'final_base_node' not in st.session_state:
        st.session_state.final_base_node = None
    if 'node_selection_complete' not in st.session_state:
        st.session_state.node_selection_complete = False
    if 'processing_ready' not in st.session_state:
        st.session_state.processing_ready = False
    if 'conversation_history' not in st.session_state:
        st.session_state.conversation_history = []

    # Sidebar for file uploads
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-container">
            <h3 style="color: #667eea; margin-top: 0; text-align: center;">📁 File Upload</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # XSLT File Upload (Required)
        st.markdown("**📄 XSLT File (Required)**")
        xslt_file = st.file_uploader(
            "Choose your XSLT file", 
            type=["xslt", "xsl"],
            help="Upload the XSLT file you want to update or analyze"
        )
        
        if xslt_file:
            st.success(f"✅ Loaded: {xslt_file.name}")
            # Store XSLT content in session state
            xslt_content = xslt_file.read().decode('utf-8')
            st.session_state.xslt = xslt_content
        
        # Specifications File Upload (Optional)
        st.markdown("**📄 Specifications File (Optional)**")
        specs_file = st.file_uploader(
            "Upload Markdown Specifications", 
            type=["md", "markdown", "txt"],
            help="Upload a markdown file containing your detailed specifications and requirements"
        )
        
        if specs_file:
            st.success(f"✅ Loaded: {specs_file.name}")
            specs_content = specs_file.read().decode('utf-8')
            st.session_state.specs_file = specs_content
        
        # Debug Mode Toggle
        st.markdown("---")
        st.markdown("**🔧 Debug Options**")
        debug_mode = st.checkbox("Enable Debug Mode", help="Show detailed processing information")
        st.session_state.debug_mode = debug_mode
        
        if debug_mode:
            st.info("Debug mode enabled - detailed information will be shown during processing")
        
        # Processing Statistics
        if hasattr(st.session_state, 'patterns_found') and st.session_state.patterns_found:
            st.markdown("**📊 Analysis Stats**")
            st.write(f"Patterns found: {len(st.session_state.patterns_found)}")
            
            if st.session_state.current_requirement:
                st.write(f"Current step: Pattern Analysis")
            if st.session_state.node_selection_complete:
                st.write(f"Selected action: {st.session_state.final_action_type}")
                st.write(f"Target node: {st.session_state.final_base_node}")
        
        # Conversation History
        if st.session_state.conversation_history:
            st.markdown("---")
            st.markdown("**💬 Conversation History**")
            with st.expander(f"View {len(st.session_state.conversation_history)} previous conversations"):
                for i, conv in enumerate(reversed(st.session_state.conversation_history[-5:])):  # Show last 5
                    st.markdown(f"**{i+1}.** {conv['requirement'][:50]}...")
                    st.caption(f"Action: {conv['action']} | Node: {conv['node']}")

    # Main content area
    with st.container():
        # Display current status
        status_col1, status_col2 = st.columns([3, 1])
        with status_col1:
            if st.session_state.operation_status == 'processing':
                st.markdown("""
                <div class="status-indicator status-processing">
                    ⚡ Processing your requirements...
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.operation_status == 'success':
                st.markdown("""
                <div class="status-indicator status-success">
                    ✅ XSLT processing completed successfully!
                </div>
                """, unsafe_allow_html=True)
            elif st.session_state.operation_status == 'error':
                st.markdown("""
                <div class="status-indicator status-error">
                    ❌ Processing failed
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="status-indicator status-idle">
                    💤 Ready to process
                </div>
                """, unsafe_allow_html=True)
                
        with status_col2:
            if st.session_state.operation_status == 'processing' and st.session_state.processing_start_time:
                elapsed = int(time.time() - st.session_state.processing_start_time)
                st.markdown(f"""
                <div class="processing-timer">
                    <span class="timer-icon">⏱️</span>
                    {elapsed}s
                </div>
                """, unsafe_allow_html=True)

        # Main interface - always show requirements input if XSLT is loaded
        if not hasattr(st.session_state, 'xslt') or not st.session_state.xslt:
            st.markdown("""
            <div class="content-container">
                <h3>📤 Upload XSLT File</h3>
                <p>Please upload your XSLT file to begin the conversational update process.</p>
                <div style="background: #f8f9fa; padding: 2rem; border-radius: 8px; text-align: center; color: #6c757d; margin-top: 1rem;">
                    <p>🔄 Waiting for XSLT file upload...</p>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Main interface when XSLT is loaded
        else:
            # Requirements Input Section - Always visible
            
            
            # Requirements text area
            user_requirement_prompt = st.text_area(
                "Describe the changes you need:", 
                value=st.session_state.get('current_requirement', ''),
                height=120,
                help="Provide detailed requirements for updating your XSLT",
                key="requirement_input"
            )
            
            # Update requirement in session state
            if user_requirement_prompt and user_requirement_prompt.strip():
                st.session_state.current_requirement = user_requirement_prompt
            
            # Process Requirements Button - only show if requirements exist and patterns not analyzed
            if (st.session_state.get('current_requirement') and 
                st.session_state.get('current_requirement').strip() and 
                not st.session_state.get('patterns_analyzed')):
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🔍 Analyze Requirements", type="primary", use_container_width=True):
                        st.session_state.patterns_analyzed = False  # Force re-analysis
                        st.rerun()
            
            # Auto-analyze patterns when requirement is entered
            if st.session_state.get('current_requirement') and not st.session_state.get('patterns_analyzed'):
                with st.spinner('🔍 Analyzing XSLT patterns...'):
                    try:
                        analyzer = UniversalXSLTAnalyzer(st.session_state.xslt)
                        all_patterns = analyzer.find_all_repeating_patterns()
                        st.session_state.patterns_found = all_patterns
                        st.session_state.patterns_analyzed = True
                    except Exception as e:
                        st.error(f"Pattern analysis failed: {str(e)}")
            
            # Node Selection - Always visible when patterns are found
            if st.session_state.get('patterns_found') and st.session_state.get('current_requirement'):
                st.markdown("---")
                
                # Detect user intent
                intent = UniversalUserInteraction.detect_intent(st.session_state.current_requirement)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown(f"**Detected Intent:** {intent.action_type.upper()}")
                with col2:
                    st.markdown(f"**Confidence:** {intent.confidence:.2f}")
                
                if intent.target_nodes:
                    st.markdown(f"**Target Nodes:** {', '.join(intent.target_nodes)}")
                    
                    # For each target node, show placement options
                    for node_name in intent.target_nodes:
                        st.markdown(f"**Options for {node_name}:**")
                        
                        # Check how many instances exist
                        instance_count = UniversalUserInteraction.check_xpath_matches(st.session_state.xslt, node_name)
                        st.write(f"Found {instance_count} existing {node_name} instances")
                        
                        # Generate placement options
                        options = UniversalUserInteraction.generate_placement_options(node_name, instance_count, intent)
                        
                        if options:
                            # Store options in session state
                            if f"options_{node_name}" not in st.session_state:
                                st.session_state[f"options_{node_name}"] = options
                            
                            # Create selectbox for better UX
                            option_labels = [opt['label'] for opt in st.session_state[f"options_{node_name}"]]
                            option_values = [opt['value'] for opt in st.session_state[f"options_{node_name}"]]
                            
                            selected_index = st.selectbox(
                                f"Select action for {node_name}:",
                                range(len(option_labels)),
                                format_func=lambda x: option_labels[x],
                                key=f"action_{node_name}"
                            )
                            
                            selected_option = option_values[selected_index]
                            selected_desc = st.session_state[f"options_{node_name}"][selected_index]['description']
                            
                            # Show description for selected option
                            st.info(f"**Action:** {selected_desc}")
                            
                            # Store selections
                            st.session_state.final_action_type = selected_option
                            st.session_state.final_base_node = node_name
                            
                            # Process button
                            col1, col2, col3 = st.columns([1, 1, 1])
                            with col2:
                                if st.button(f"🤖 Process XSLT Update", key=f"process_{node_name}", type="primary", use_container_width=True):
                                    st.session_state.operation_status = 'processing'
                                    st.session_state.processing_start_time = time.time()
                                    st.rerun()
                        else:
                            st.warning(f"No valid options found for {node_name}")
                else:
                    st.warning("No target nodes detected in your requirements. Please be more specific.")
            
            # Clear button
            if st.session_state.get('current_requirement'):
                col1, col2, col3 = st.columns([1, 1, 1])
                with col2:
                    if st.button("🔄 Clear and Start Over", use_container_width=True):
                        # Clear all session state
                        keys_to_clear = ['current_requirement', 'patterns_found', 'patterns_analyzed', 'final_action_type', 'final_base_node', 'operation_status']
                        for key in keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]
                        # Clear stored options
                        keys_to_remove = [key for key in st.session_state.keys() if key.startswith('options_')]
                        for key in keys_to_remove:
                            del st.session_state[key]
                        st.rerun()
        
        # AI Processing when button is clicked
        if st.session_state.get('operation_status') == 'processing':
            st.markdown("""
            <div class="content-container">
                <h3>🤖 AI Processing</h3>
            </div>
            """, unsafe_allow_html=True)
            
            with st.spinner('Processing with Genie...'):
                try:
                    # Find the pattern for the selected node
                    analyzer = UniversalXSLTAnalyzer(st.session_state.xslt)
                    all_patterns = analyzer.find_all_repeating_patterns()
                    
                    # Find matching pattern
                    pattern = None
                    for p in all_patterns:
                        if st.session_state.final_base_node.lower() in p.pattern_name.lower():
                            pattern = p
                            break
                    
                    if not pattern:
                        # Create a minimal pattern if not found
                        from genie_core.xslt.universal_xslt_analyzer import UniversalPattern
                        pattern = UniversalPattern(
                            pattern_name=st.session_state.final_base_node,
                            pattern_type='xml_element',
                            instance_count=0,
                            instances=[],
                            sample_content=''
                        )
                    
                    # Debug information for chunk extraction
                    if st.session_state.get('debug_mode', False):
                        st.markdown("**🔍 Debug: Context Extraction**")
                        st.write(f"Pattern: {pattern.pattern_name}")
                        st.write(f"Action: {st.session_state.final_action_type}")
                    
                    # Extract context
                    extractor = UniversalChunkExtractor(st.session_state.xslt)
                    relevant_chunk = extractor.extract_universal_context(
                        pattern, 
                        st.session_state.current_requirement, 
                        st.session_state.final_action_type
                    )
                    
                    # Debug information for extracted chunk
                    if st.session_state.get('debug_mode', False):
                        with st.expander("🔍 Debug: Extracted Chunk"):
                            st.code(relevant_chunk, language='xml')
                    
                    # Process with AI
                    processor = UniversalAIProcessor()
                    specs = st.session_state.get('specs_file', '')
                    
                    modified_chunk = processor.process_universal_chunk(
                        relevant_chunk,
                        st.session_state.current_requirement,
                        pattern,
                        specs,
                        st.session_state.final_action_type
                    )
                    
                    # Debug information for AI response
                    if st.session_state.get('debug_mode', False):
                        with st.expander("🔍 Debug: AI Generated Chunk"):
                            st.code(modified_chunk, language='xml')
                    
                    # Merge back into original XSLT
                    updated_xslt = processor.merge_universal_chunk(
                        st.session_state.xslt,
                        modified_chunk,
                        pattern,
                        st.session_state.final_action_type
                    )
                    
                    # Apply pretty printing
                    pretty_xslt = pretty_print_xml(updated_xslt)
                    st.session_state.updated_xslt = pretty_xslt
                    st.session_state.operation_status = 'success'
                    
                    # Add to conversation history
                    conversation_entry = {
                        'requirement': st.session_state.current_requirement,
                        'action': st.session_state.final_action_type,
                        'node': st.session_state.final_base_node,
                        'timestamp': time.time(),
                        'success': True
                    }
                    st.session_state.conversation_history.append(conversation_entry)
                    
                    st.rerun()
                    
                except Exception as e:
                    st.session_state.operation_status = 'error'
                    st.error(f"AI processing failed: {str(e)}")
                    if st.session_state.get('debug_mode', False):
                        st.exception(e)
        
        # Processing Complete - Show Results
       
            
        
        # Error handling state
        if st.session_state.get('operation_status') == 'error':
            st.markdown("""
            <div class="content-container">
                <h3>❌ Processing Error</h3>
                <p>An error occurred during processing. Please review the error details and try again.</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button("🔄 Reset and Try Again", type="primary", use_container_width=True):
                    # Reset processing state
                    st.session_state.operation_status = 'idle'
                    st.session_state.processing_start_time = None
                    st.rerun()

    # XSLT output section - only show if content exists
    updated_xslt = st.session_state.get('updated_xslt')
    
    if updated_xslt:
        # Collapsible XSLT output section
        
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("**✅ XSLT Generated Successfully**")
            with col2:
                st.download_button(
                    label="📥 Download XSLT",
                    data=updated_xslt,
                    file_name="updated_xslt.xslt",
                    mime="application/xslt",
                    type="primary"
                )
            
            # Enhanced code display with copy functionality and fixed height
            st.markdown("""
            <div class="code-container">
                <div class="code-header">
                    <span>📄 XSLT Code</span>
                    <button class="copy-button" onclick="copyToClipboard('xslt-code')">📋 Copy</button>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display XSLT in fixed height text area (like original)
            st.markdown("**📄 XSLT Code**")
            
            # Simple, effective approach - fixed height text area with custom styling
            st.markdown("""
            <style>
            div[data-testid="stTextArea"] > div > div > textarea {
                background-color: #f8f9fa !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            height = min(400, max(200, len(updated_xslt.split('\n')) * 20))
            st.text_area("", updated_xslt, height=height, key="xslt_display")
            
            # Add JavaScript for copy functionality
            st.markdown("""
            <script>
            function copyToClipboard(elementId) {
                const code = document.querySelector('code').textContent;
                navigator.clipboard.writeText(code).then(() => {
                    alert('Code copied to clipboard!');
                });
            }
            
            function toggleCollapse(sectionId) {
                const section = document.getElementById(sectionId);
                const arrow = document.getElementById(sectionId.replace('-section', '-arrow'));
                if (section.classList.contains('expanded')) {
                    section.classList.remove('expanded');
                    arrow.style.transform = 'rotate(-90deg)';
                } else {
                    section.classList.add('expanded');
                    arrow.style.transform = 'rotate(0deg)';
                }
            }
            </script>
            """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)  # Close collapsible section
    
    # Enhanced specifications output section - only show if content exists
    generated_specs = st.session_state.get('updated_specs')
    if generated_specs:
        
        
        with st.container():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown("**✅ Specifications Generated Successfully**")
            with col2:
                st.download_button(
                    label="📥 Download Specs",
                    data=generated_specs,
                    file_name="generated_specs.md",
                    mime="text/markdown",
                    type="primary"
                )
            
            # Display specifications with fixed height scrollable container
            st.markdown("**📖 View Specifications**")
            with st.container():
                # Convert markdown to HTML for proper display in scrollable container
                import markdown
                specs_html = markdown.markdown(generated_specs)
                st.markdown(f"""
                <div style="height: 400px; overflow-y: auto; border: 1px solid #e0e0e0; border-radius: 8px;padding: 1rem;">
                    {specs_html}
                </div>
                """, unsafe_allow_html=True)
            
with optimize_tab:
    st.markdown("""
    <div class="content-container">
        <h3>⚡ XSLT Optimization & Testing</h3>
        <p>Test your generated XSLT with sample XML data to ensure it works correctly.</p>
    </div>
    """, unsafe_allow_html=True)
    
    output_placeholder = st.empty()

    updated_xslt = st.session_state.get('updated_xslt')
    source_xml = st.session_state.get('source_xml')

    if updated_xslt and source_xml:
        try:
            with st.spinner('🔄 Applying XSLT transformation...'):
                logs = []
                formatted_xml, logs = apply_xslt(updated_xslt, source_xml, logs, None)
                
            if formatted_xml:
                st.session_state.llm_target_xml = formatted_xml
                
                # Success message with download
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.success("✅ XSLT transformation completed successfully!")
                with col2:
                    st.download_button(
                        label="📥 Download XML",
                        data=formatted_xml,
                        file_name="transformed_xml.xml",
                        mime="application/xml",
                        type="primary"
                    )
                
                # Display transformed XML with syntax highlighting
                with st.expander("📄 View Transformed XML", expanded=True):
                    st.code(formatted_xml, language='xml', line_numbers=True)
                    
                # Show logs if any
                if logs:
                    with st.expander("📋 Transformation Logs"):
                        for log in logs:
                            st.text(log)
            else:
                st.error("❌ XSLT transformation failed - no output generated")
                
        except Exception as e:
            st.markdown(f"""
            <div class="error-card">
                <h4>❌ Transformation Error</h4>
                <p>An error occurred during the XSLT transformation:</p>
                <code>{str(e)}</code>
            </div>
            """, unsafe_allow_html=True)
    else:
        missing_items = []
        if not updated_xslt:
            missing_items.append("📄 Generated XSLT")
        if not source_xml:
            missing_items.append("📄 Source XML data")
            
        st.markdown(f"""
        <div class="warning-card">
            <h4>⚠️ Missing Required Data</h4>
            <p>To test your XSLT transformation, you need:</p>
            <ul>
                {''.join([f'<li>{item}</li>' for item in missing_items])}
            </ul>
            <p>Please generate the XSLT first in the <strong>Update</strong> tab.</p>
        </div>
        """, unsafe_allow_html=True)

with analysis_and_review_tab:
    st.markdown("""
    <div class="content-container">
        <h3>🔍 Analysis & Review Dashboard</h3>
        <p>Compare your original and updated XSLT files and specifications side by side.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Logic to compare existing_xslt and updated_xslt
    def normalize_lines(xslt_str):
        # Unify line endings, replace tabs with spaces, remove trailing (not leading) whitespace
        return [
            line.rstrip().replace('\t', '    ')
            for line in xslt_str.replace('\r\n', '\n').replace('\r', '\n').split('\n')
        ]
    def compare_xslt(existing_xslt, updated_xslt):
        existing_lines = normalize_lines(existing_xslt)
        updated_lines = normalize_lines(updated_xslt)
        diff = difflib.HtmlDiff().make_table(
            existing_lines,
            updated_lines,
            fromdesc='Existing XSLT',
            todesc='Updated XSLT',
            context=False,
            numlines=0
        )
            # Custom styling to fix column widths
        custom_style = """
        <style>
            table {
                width: 120%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                word-break: break-word; /* Break long words */
                white-space: pre-wrap;  /* Preserve formatting but allow wrapping */
            }

            th {
                background-color: #f2f2f2;
            }
            .diff_next {
                display: none;
            }
            pre {
                white-space: pre-wrap;
            }
            .diff_header {
                font-weight: bold;
                background-color: #ddd;
            }
            .diff_add {
                background-color: #d4fcbc;
            }
            .diff_chg {
                background-color: #ffeeba;
            }
            .diff_sub {
                background-color: #ffbaba;
            }
        </style>
        """
        return custom_style + diff
        #return diff
    
    def get_files():
        if "xslt" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/xslt.xslt", 'r') as file:
                    existing_xslt = file.read()
        else:
            existing_xslt = st.session_state.xslt
        
        if "specs_file" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/specs.md", 'r') as file:
                    existing_specs = file.read()
        else:
            existing_specs = st.session_state.specs_file
        
        if "updated_xslt" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/updated_xslt.xslt", 'r') as file:
                    updated_xslt = file.read()
        else:
            updated_xslt = st.session_state.updated_xslt
        
        if "updated_specs" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/update_xslt/content-transformer-new/1_6_1_openai/learning/xslt_generator/config/test_data/NDC_Cancel/updated_specs.md", 'r') as file:
                    updated_specs = file.read()
        else:
            updated_specs = st.session_state.updated_specs
        return existing_xslt, existing_specs, updated_xslt, updated_specs

    # Logic to compare existing_specs and updated_specs
    def compare_specs(existing_specs, updated_specs):
        diff = difflib.HtmlDiff().make_table(
            existing_specs.splitlines(keepends=True),
            updated_specs.splitlines(keepends=True),
            fromdesc='Existing Specs',
            todesc='Updated Specs',
            context=False,
            numlines=0
        )
            # Custom styling to fix column widths
        custom_style = """
        <style>
            table {
                width: 120%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                text-align: left;
                word-break: break-word; /* Break long words */
                white-space: pre-wrap;  /* Preserve formatting but allow wrapping */
            }

            td:nth-child(2), th:nth-child(2) {
            width: 5%;
            min-width: 25px;
            }
            td:nth-child(5), th:nth-child(5) {
            width: 5%;
            min-width: 25px;
            }


            th {
                background-color: #f2f2f2;
            }
            .diff_next {
                display: none;
            }
            pre {
                white-space: pre-wrap;
            }
            .diff_header {
                font-weight: bold;
                background-color: #ddd;
            }
            .diff_add {
                background-color: #d4fcbc;
            }
            .diff_chg {
                background-color: #ffeeba;
            }
            .diff_sub {
                background-color: #ffbaba;
            }
        </style>
        """

        return custom_style + diff
        #return diff


    def finetune_specs_llm():
        with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/prompts/generic/system_read_spec_file_for_publish.txt") as file:
            specs_read_prompt = file.read()
        
        prompts = []
        prompts.append({"role":"system", "content":specs_read_prompt})
        
        if "specs_file" not in st.session_state:
            with open("/Users/nlepakshi/Documents/GitHub/demo_master/content-transformer-new/xslt_generator/config/test_data/Ord_cancel/generated_specs.txt") as file:
                spec_file = file.read()
        else:
            spec_file = st.session_state.updated_specs

        prompts.append({"role":"user", "content":spec_file})
            
        llm_response = get_chat_completion(prompts)
        response_obj = None
        if llm_response:
            response_obj = llm_response.choices[0].message.content
            st.download_button(
                label="Download Specs",
                data=response_obj,
                file_name="updated_specs.html",
                mime="application/html"
            )

    def publish(body):
        confluence_utils.reupload_page(2354569017,'OrderRetrieve Request Specifications copy', body=body)

    existing_xslt, existing_specs, updated_xslt, updated_specs = get_files()
    if existing_xslt and updated_xslt:
        try:
            diff = compare_xslt(existing_xslt, updated_xslt)
            st.markdown("""
            <div class="content-container">
                <h3>🔍 XSLT Comparison Results</h3>
                <p>Review the differences between your existing and updated XSLT files.</p>
            </div>
            """, unsafe_allow_html=True)
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing XSLT files: {str(e)}")
            
    if existing_specs and updated_specs:
        try:
            diff = compare_specs(existing_specs, updated_specs)
            
            st.markdown("""
            <div class="content-container">
                <h3>📋 Specifications Comparison</h3>
                <p>Review the differences between your existing and updated specifications.</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Confluence publish button
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("🚀 Update Confluence Page", type="primary", use_container_width=True):
                    try:
                        confluence_utils.publish_content(st.session_state.space, st.session_state.page_name, st.session_state.html)
                        st.success("✅ Successfully updated Confluence page!")
                    except Exception as e:
                        st.error(f"❌ Failed to update Confluence: {str(e)}")
            
            st.markdown(diff, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error comparing specs files: {str(e)}")
        # #finetune_specs_llm()

    else:
        st.markdown("""
        <div class="warning-card">
            <h4>⚠️ No Data Available</h4>
            <p>To perform analysis and comparison, please:</p>
            <ul>
                <li>📄 Upload XSLT files in the <strong>Update</strong> tab</li>
                <li>🔄 Generate updated XSLT and specifications</li>
                <li>📊 Return here to view the comparison</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # st.markdown("""
    #     <style>
    #     .diff_add { background-color: #ccffcc; }  /* Green background for additions */
    #     .diff_sub { background-color: #ffcccc; }  /* Red background for deletions */
    #     table { width: 100%; }                    /* Full width table */
    #     td { padding: 8px; border: 1px solid #ddd; } /* Table cell styling */
    #     </style>
    #     """, unsafe_allow_html=True)
    
with testing_tab:
    display_testing()
    
with cook_book_tab:
    st.markdown("""
    <div class="content-container">
        <h3>📚 XSLT Cookbook Manager</h3>
        <p>Manage transformation patterns, templates, and reusable code snippets for your XSLT projects.</p>
    </div>
    """, unsafe_allow_html=True)
    
    current_dir = Path(__file__).resolve().parent
    directory_path = current_dir / "../../../genie_core/config/cookbooks"
    
    if os.path.exists(directory_path):
        files = [f for f in os.listdir(directory_path) if os.path.isfile(os.path.join(directory_path, f))]
        if files:
            st.markdown("**📁 Select Cookbook File**")
            selected_file = st.selectbox(
                "Choose a cookbook to edit", 
                files,
                help="Select from available cookbook files containing XSLT patterns and templates"
            )
            file_path = os.path.join(directory_path, selected_file)

            # Read and extract all JSON objects robustly
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # Remove comments
                content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
                # Robustly extract JSON objects by counting braces
                data = []
                buf = ''
                depth = 0
                in_obj = False
                for c in content:
                    if c == '{':
                        if depth == 0:
                            buf = ''
                            in_obj = True
                        depth += 1
                    if in_obj:
                        buf += c
                    if c == '}':
                        depth -= 1
                        if depth == 0 and in_obj:
                            try:
                                data.append(json.loads(buf))
                            except Exception as e:
                                logging.error(f"Failed to parse JSON object: {e}. Problematic snippet: {buf}")
                            in_obj = False

            # Build a list of keys for the dropdown
            key_list = ["Select key to edit..."]
            key_map = {}  # Map key to index in data
            for idx, item in enumerate(data):
                k = item.get("key", f"Item {idx+1}")
                key_list.append(k)
                key_map[k] = idx

            selected_key = st.selectbox("Select key to edit", key_list)

            # --- Edit Section ---
            if selected_key != "Select key to edit...":
                selected_idx = key_map[selected_key]
                selected_item = data[selected_idx]
                st.markdown("""
                <div class="content-container">
                    <h3>✏️ Edit Selected Pattern</h3>
                </div>
                """, unsafe_allow_html=True)
                new_key = st.text_input("Key", value=selected_item.get("key", ""), key="edit_key")
                edit_key_valid = True
                if new_key and not re.fullmatch(r'[A-Z0-9]+(_[A-Z0-9]+)*', new_key):
                    st.error("Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH).")
                    edit_key_valid = False

                new_code = st.text_area("Code", value=selected_item.get("code", ""), key="edit_code")
                new_example = st.text_area("Example", value=selected_item.get("example", ""), key="edit_example")
                new_description = st.text_area("Description (optional)", value=selected_item.get("description", ""), key="edit_description")

                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("💾 Save Changes", type="primary", use_container_width=True):
                        if not edit_key_valid:
                            st.error("⚠️ Please fix the key validation errors before saving.")
                        else:
                            updated_item = {
                                "key": new_key,
                                "code": new_code,
                                "example": new_example
                            }
                            if new_description.strip():
                                updated_item["description"] = new_description
                            data[selected_idx] = updated_item
                            try:
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, ensure_ascii=False, indent=2)
                                st.success("✅ Pattern updated successfully!")
                            except Exception as e:
                                st.error(f"Failed to save: {e}")

            # --- Add Section ---
            st.markdown("""
            <div class="content-container">
                <h3>➕ Add New Pattern</h3>
                <p>Create a new XSLT pattern or template for reuse in future transformations.</p>
            </div>
            """, unsafe_allow_html=True)
            add_key = st.text_input("New Key", key="add_key")
            key_valid = True
            if add_key and not re.fullmatch(r'[A-Z0-9]+(_[A-Z0-9]+)*', add_key):
                st.error("Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH).")
                key_valid = False

            add_code = st.text_area("New Code", key="add_code")
            add_example = st.text_area("New Example", key="add_example")
            add_description = st.text_area("New Description (optional)", key="add_description")
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("➕ Add New Pattern", type="primary", use_container_width=True):
                    if not key_valid:
                        st.error("⚠️ Please fix the key validation errors before adding.")
                    else:
                        new_item = {
                            "key": add_key,
                            "code": add_code,
                            "example": add_example
                        }
                        if add_description.strip():
                            new_item["description"] = add_description
                        data.append(new_item)
                        try:
                            with open(file_path, 'w', encoding='utf-8') as f:
                                for i, obj in enumerate(data):
                                    json_str = json.dumps(obj, ensure_ascii=False, indent=2)
                                    if i != 0:
                                        f.write(",\n")
                                    f.write(json_str)
                                f.write("\n")
                            st.success("✅ New pattern added successfully!")
                        except Exception as e:
                            st.error(f"Failed to add: {e}")
        else:
            st.markdown("""
            <div class="warning-card">
                <h4>⚠️ No Cookbook Files Found</h4>
                <p>No cookbook files were found in the directory. Please ensure cookbook files exist in:</p>
                <code>genie_core/config/cookbooks/</code>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="error-card">
            <h4>❌ Cookbook Directory Missing</h4>
            <p>The cookbook directory does not exist. Please create the directory:</p>
            <code>genie_core/config/cookbooks/</code>
        </div>
        """, unsafe_allow_html=True)
        
    with st.sidebar:
        with st.container():
            st.markdown(
                """
                <div class="metrics-card">
                    <h3>📊 Model Information & Metrics</h3>
                    <div class="metric-item">
                        <span>🤖 GPT Model:</span>
                        <span class="metric-value">{gpt_model}</span>
                    </div>
                    <div class="metric-item">
                        <span>📞 API Calls:</span>
                        <span class="metric-value">{calls}</span>
                    </div>
                    <div class="metric-item">
                        <span>💰 Total Cost:</span>
                        <span class="metric-value">{cost_eur} EUR</span>
                    </div>
                    <div class="metric-item">
                        <span>💰 Cost (INR):</span>
                        <span class="metric-value">{cost_inr} INR</span>
                    </div>
                </div>
                """.format(
                    gpt_model=st.session_state.get('gpt_model_used', 'N/A'),
                    calls=st.session_state.get('number_of_calls_to_llm', 0),
                    cost_eur=st.session_state.get('total_cost_per_tool', 0.0),
                    cost_inr=TokenCostCalculator.convert_cost(st.session_state.get('total_cost_per_tool', 0.0), "INR") if 'TokenCostCalculator' in globals() else 'N/A'
                ),
                unsafe_allow_html=True,
            )