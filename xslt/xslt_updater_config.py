# XSLT Updater Configuration
# This file contains all configurable constants and settings

from dataclasses import dataclass
from typing import List, Dict

# UI Configuration
class UIConfig:
    # Page configuration
    PAGE_TITLE = "XSLT Updater - Genie"
    PAGE_ICON = "🛠️"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"
    
    # Button and UI text
    CLEAR_CACHE_BUTTON_TEXT = "🔄 Clear All Cache & Conversation"
    PROCESS_REQUIREMENTS_BUTTON_TEXT = "🚀 Process Requirements"
    START_PROCESSING_NODE_BUTTON_TEXT = "🚀 Start Processing Node"
    START_NEW_PROCESSING_BUTTON_TEXT = "🔄 Start New Processing"
    
    # File upload configuration
    XSLT_FILE_TYPES = ["xslt", "xsl"]
    SPECS_FILE_TYPES = ["md", "markdown", "txt"]
    XML_FILE_TYPES = ["xml"]
    
    # Context limits
    MAX_TEXT_HISTORY = 10
    DEFAULT_TEXT_AREA_HEIGHT = 120
    XSLT_DISPLAY_HEIGHT_MIN = 200
    XSLT_DISPLAY_HEIGHT_MAX = 400
    
    # Status messages
    STATUS_MESSAGES = {
        'idle': '💤 Ready to process',
        'processing': '⚡ Processing your requirements...',
        'success': '✅ XSLT generated successfully!',
        'error': '❌ Processing failed',
        'completed': '✅ XSLT processing completed successfully!'
    }

# LLM Configuration
class LLMConfig:
    # Default model
    DEFAULT_MODEL = "GPT4O"
    
    # Prompt templates
    SYSTEM_MESSAGE_TEMPLATE = """You are a universal XSLT expert specialized in generating precise XML elements for insertion into existing XSLT files. You NEVER generate complete templates or stylesheets - only the specific XML elements requested."""
    
    USER_CONTENT_TEMPLATE = """CONTEXT:
- Pattern: {pattern_name} ({pattern_group})
- Instance Count: {instance_count}
- Location: {xpath_location}{operation_info}

CHUNK TO PROCESS:
```xml
{chunk}
```

USER REQUEST: {requirement}
SPECIFICATIONS: {specs}"""

    ASSISTANT_INSTRUCTIONS = """You are an XML/XSLT generator. Your job is to generate ACTUAL XML CONTENT for insertion into existing XSLT files.

CRITICAL RULES:
1. NEVER generate full XSLT templates like <xsl:template match="/"> 
2. NEVER generate comments like "<!-- INSERT..." or "<!-- ADD..." 
3. ALWAYS generate actual XML elements and content ONLY
4. Generate ONLY the specific XML content requested - no template wrappers

WHAT TO GENERATE:
- Generate ONLY the XML element(s) that the user specifically requested
- If conditions are mentioned, wrap ONLY that element in XSLT conditional logic
- DO NOT create complete templates or stylesheets
- The element will be merged into an existing XSLT structure

OUTPUT: Return ONLY the XML element(s) that should be inserted into the existing XSLT structure."""

# Pattern Analysis Configuration
class PatternConfig:
    # XML parsing configuration
    XML_DECLARATION_DEFAULT = '<?xml version="1.0" encoding="UTF-8"?>'
    INDENT_SIZE = 4
    MAX_CONTENT_PREVIEW_LENGTH = 100
    MAX_NAMESPACE_LINES_CHECK = 30
    
    # Pattern grouping keywords
    ENTITY_PATTERNS = {
        'person': 'People & Identity',
        'user': 'People & Identity', 
        'customer': 'People & Identity',
        'passenger': 'People & Identity',
        'contact': 'People & Identity',
        'product': 'Products & Services',
        'service': 'Products & Services',
        'item': 'Products & Services',
        'offer': 'Products & Services',
        'order': 'Orders & Transactions',
        'transaction': 'Orders & Transactions',
        'payment': 'Orders & Transactions',
        'booking': 'Orders & Transactions',
        'account': 'Financial Data',
        'financial': 'Financial Data',
        'money': 'Financial Data',
        'price': 'Financial Data',
        'amount': 'Financial Data',
        'location': 'Location & Geography',
        'address': 'Location & Geography',
        'place': 'Location & Geography',
        'geo': 'Location & Geography'
    }
    
    META_PATTERNS = ['meta', 'config', 'setting', 'header', 'info']
    TECH_PATTERNS = {
        'message': ['request', 'response', 'message', 'envelope'],
        'query': ['query', 'filter', 'search', 'criteria']
    }
    DATA_CONTAINERS = ['list', 'array', 'collection', 'set', 'group', 'items']
    
    # Fallback pattern groups
    FALLBACK_GROUPS = {
        'Configuration & Metadata': META_PATTERNS,
        'Message Structure': TECH_PATTERNS['message'],
        'Query & Filtering': TECH_PATTERNS['query'],
        'Data Collections': DATA_CONTAINERS,
        'Deep Nested Structures': [],  # For deep hierarchies
        'General': []  # Ultimate fallback
    }
    
    # XML and XSLT regex patterns
    XML_ELEMENT_PATTERN = r'<([a-zA-Z][a-zA-Z0-9_-]*)[^>]*>'
    TEMPLATE_PATTERN = r'<xsl:template[^>]*match=["\']([^"\']*)["\'][^>]*>'
    LOOP_PATTERN = r'<xsl:for-each[^>]*select=["\']([^"\']*)["\'][^>]*>(.*?)</xsl:for-each>'
    IF_PATTERN = r'<xsl:if[^>]*test=["\']([^"\']*)["\'][^>]*>(.*?)</xsl:if>'
    PARENT_PATTERN = r'<([a-zA-Z][a-zA-Z0-9_:-]*)[^>]*>'
    OPENING_TAG_PATTERN = r'<[^/][^>]*>'
    CLOSING_TAG_PATTERN = r'</[^>]*>'
    IF_OPEN_PATTERN = r'<xsl:if[^>]*>'
    IF_CLOSE_PATTERN = r'</xsl:if>'
    LOOP_SELECT_PATTERN = r'<xsl:for-each[^>]*select=["\']([^"\']*)["\']'
    QUOTES_PATTERN = r'["\']'
    OPERATORS_PATTERN = r'[=!<>]+'
    WHITESPACE_PATTERN = r'\s+'
    INSTANCE_PATTERN = r'add_after_instance_(\d+)'
    APPEND_INSTANCE_PATTERN = r'append_to_instance_(\d+)'
    TEMPLATE_BRACKET_PATTERN = r'Template\[([^\]]+)\]'
    XML_DECLARATION = '<?xml version="1.0" encoding="UTF-8"?>'
    NAMESPACE_PATTERN = r'xmlns[^=]*=["\'][^"\']*["\']'
    VARIABLE_PATTERN = r'\$([a-zA-Z_][a-zA-Z0-9_]*)'
    XPATH_FULL_PATTERN = r'[A-Za-z][A-Za-z0-9]*(?:/[A-Za-z][A-Za-z0-9]*)+'
    STANDALONE_ELEMENT_PATTERN = r'\b[A-Za-z][A-Za-z0-9]*(?=[^A-Za-z0-9]|$)'
    XML_ELEMENT_EXTRACT_PATTERN = r'<([A-Za-z][A-Za-z0-9]*)[^>]*>'
    XML_COMMENT_PATTERN = r'<!--.*?-->'
    XSLT_STYLESHEET_HEADER = '<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">'

# Extraction Configuration
class ExtractionConfig:
    # Context extraction settings
    DEFAULT_CONTEXT_LINES = 5
    MINIMAL_CONTEXT_LINES = 2
    MAX_PARENT_SEARCH_ATTEMPTS = 10
    MAX_CLOSING_TAGS_TO_CHECK = 10
    
    # Container name generation suffixes
    CONTAINER_SUFFIXES = ['List', 'Container', 'Group', 'Collection', 'Set', 'Array', 'Items', 'Data', 'Info']
    CONTAINER_DETAILS_SUFFIXES = ['Details', 'Information', 'Elements', 'Records', 'Registry']
    GENERIC_CONTAINERS = ['Data', 'Elements', 'Items', 'Records', 'Collection', 'Entries', 'Content']
    TECHNICAL_CONTAINERS = ['xsl:stylesheet', 'Document', 'Root', 'Content']
    
    # Keywords for operation detection
    MODIFY_ACTION_PREFIX = 'modify'
    NEW_ATTRIBUTE_KEYWORDS = ['new', 'add', 'modify', 'update', 'change', 'set', 'value', 'attribute']
    MODIFY_KEYWORDS = ['modify', 'update', 'change', 'edit', 'alter', 'fix']
    STOP_WORDS = [
        'will', 'be', 'is', 'are', 'the', 'and', 'or', 'in', 'on', 'at', 'by', 'for', 'of', 'to', 'from',
        'going', 'forward', 'will', 'refer', 'this', 'node', 'and', 'the', 'for', 'with',
        'within', 'inside', 'containing', 'having', 'using', 'into', 'onto', 'upon'
    ]
    ADD_KEYWORDS = ['create', 'add', 'new', 'append', 'insert', 'another']
    MODIFY_KEYWORDS = ['modify', 'update', 'change', 'edit', 'alter', 'fix']
    
    # Emergency fallback structures
    EMERGENCY_STRUCTURE_TEMPLATE = """<!-- EMERGENCY FALLBACK STRUCTURE -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <!-- Context for adding new {pattern_name} -->
    <example-{pattern_name_lower}>
        <!-- INSERT NEW CONTENT HERE -->
        <!-- Marker for new {pattern_name} insertion -->
    </example-{pattern_name_lower}>
</xsl:stylesheet>"""

# File and Path Configuration
class PathConfig:
    # Relative paths from the script location
    COOKBOOKS_RELATIVE_PATH = "../../../genie_core/config/cookbooks"
    DEFAULT_TEST_DATA_PATH = "../../../genie_core/config/test_data"
    
    # File naming patterns
    UPDATED_XSLT_FILENAME = "updated_xslt.xslt"
    GENERATED_SPECS_FILENAME = "generated_specs.md"
    TRANSFORMED_XML_PREFIX = "transformed_"

# Debug and Logging Configuration
class DebugConfig:
    # Debug mode settings
    DEFAULT_DEBUG_MODE = False
    MAX_DEBUG_CONTENT_DISPLAY = 500
    DEBUG_TRUNCATION_SUFFIX = "..."
    MAX_ELEMENT_DISPLAY = 5
    MAX_FALLBACK_PREVIEW = 3
    
    # Error message templates
    ERROR_MESSAGES = {
        'file_not_found': "❌ File not found: {filepath}",
        'parsing_failed': "❌ Failed to parse {file_type}: {error}",
        'llm_processing_failed': "❌ LLM processing failed: {error}",
        'merge_failed': "🚨 Universal merge failed: {error}",
        'extraction_failed': "⚠️ Extraction failed for pattern '{pattern}': {error}"
    }
    
    # Success message templates  
    SUCCESS_MESSAGES = {
        'file_loaded': "✅ Loaded: {filename}",
        'pattern_found': "✅ Found {count} instances of {pattern}",
        'extraction_success': "✅ Successfully extracted with primary pattern: {pattern}",
        'merge_success': "✅ **MERGE SUCCESSFUL** - {element} merged into XSLT structure"
    }
    
    # Warning message templates
    WARNING_MESSAGES = {
        'no_instances': "⚠️ No instances found for pattern '{pattern}', creating minimal structure",
        'fallback_used': "⚠️ All fallback patterns failed, creating minimal structure",
        'emergency_merge': "🚨 Using emergency merge strategy"
    }

# Validation Configuration
@dataclass
class ValidationConfig:
    """Configuration for validation rules and patterns"""
    COOKBOOK_KEY_PATTERN: str = r'[A-Z0-9]+(_[A-Z0-9]+)*'
    COOKBOOK_KEY_ERROR: str = "Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH)."
class ValidationConfig:
    # Pattern validation
    MIN_ELEMENT_NAME_LENGTH = 2
    MAX_ELEMENT_NAME_LENGTH = 100
    
    # Content validation
    MIN_CHUNK_LENGTH = 10
    MIN_PATTERN_INSTANCES = 1
    MAX_PATTERN_INSTANCES = 1000
    
    # Key validation for cookbook entries
    COOKBOOK_KEY_PATTERN = r'[A-Z0-9]+(_[A-Z0-9]+)*'
    COOKBOOK_KEY_ERROR = "Invalid key! Use only uppercase letters, numbers, and underscores between words (e.g., DUMMY_PATTERN_PATH)."
    
    # Common words to filter from node extraction
    COMMON_WORDS_FILTER = {
        'Input', 'Output', 'Remarks', 'Create', 'Map', 'Hardcoded', 'NA', 'XML', 'XSLT',
        'going', 'forward', 'will', 'refer', 'this', 'node', 'and', 'the', 'for', 'with',
        'new', 'add', 'modify', 'update', 'change', 'set', 'value', 'attribute'
    }

# Analysis Configuration  
class AnalysisConfig:
    # Structure analysis settings
    MAX_XSLT_ANALYSIS_LENGTH = 2000
    MAX_FALLBACK_PATTERNS = 10
    DEEP_NESTING_THRESHOLD = 4
    
    # LLM analysis prompt template
    STRUCTURE_ANALYSIS_PROMPT = """You are an XSLT structure analyzer. Analyze the provided XSLT file and determine the best insertion path for the element '{main_element}'.

ORIGINAL XSLT STRUCTURE:
```xml
{xslt_preview}...
```

ELEMENT TO INSERT: {main_element}

GENERATED CONTENT:
```xml
{clean_chunk}
```

Your task: Analyze the XSLT structure and determine:
1. What is the root container element name (the main template container)?
2. What hierarchical path would be most appropriate for inserting {main_element}?

RULES:
- Look at the existing XSLT structure to understand the hierarchy
- Find logical parent containers for {main_element}
- Suggest a path that makes semantic sense
- If you see existing similar elements, suggest placing near them

RESPONSE FORMAT (JSON):
{{
    "insertion_point": "root_container_name",
    "parent_path": ["parent1", "parent2", "parent3"],
    "reasoning": "Brief explanation of why this path makes sense"
}}

If no clear structure is found, return: {{"insertion_point": null, "parent_path": [], "reasoning": "No clear structure found"}}"""

# Test Configuration
class TestConfig:
    # Testing batch sizes and limits
    MAX_BATCH_FILES = 100
    DEFAULT_TRANSFORMATION_TIMEOUT = 30  # seconds
    
    # Test file paths (for development/testing)
    DEFAULT_TEST_PATHS = {
        'xslt': "/test_data/sample.xslt",
        'specs': "/test_data/sample_specs.md",
        'xml': "/test_data/sample.xml"
    }

# Performance Configuration
class PerformanceConfig:
    # Processing limits
    MAX_FILE_SIZE_MB = 10
    MAX_PROCESSING_TIME_SECONDS = 300
    
    # Cache settings
    MAX_CACHE_ENTRIES = 1000
    CACHE_EXPIRY_HOURS = 24
    
    # Chunking limits
    MAX_CHUNK_SIZE_CHARS = 50000
    DEFAULT_CHUNK_OVERLAP = 200

# Export all configurations
ALL_CONFIGS = {
    'ui': UIConfig,
    'llm': LLMConfig,
    'pattern': PatternConfig,
    'extraction': ExtractionConfig,
    'path': PathConfig,
    'debug': DebugConfig,
    'validation': ValidationConfig,
    'analysis': AnalysisConfig,
    'test': TestConfig,
    'performance': PerformanceConfig
}
