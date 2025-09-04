import re
from typing import List, Dict, Tuple, Optional
from .universal_xslt_analyzer import UniversalPattern

class UniversalChunkExtractor:
    """Enhanced chunk extractor with anti-duplication features"""
    
    def __init__(self, xslt_content: str):
        self.xslt_content = xslt_content
        self.lines = xslt_content.split('\n')
    
    def extract_universal_context(self, pattern: UniversalPattern, requirement: str, action_type: str) -> str:
        """Extract context using surgical strategies to prevent duplication"""
        
        if action_type.startswith("add_after_instance_"):
            return self._extract_surgical_reference_context(pattern, action_type, requirement)
        elif action_type.startswith("append_to_instance_"):
            return self._extract_instance_for_append(pattern, action_type)
        elif action_type.startswith("modify_instance_"):
            return self._extract_instance_for_modification(pattern, action_type)
        else:
            return self._extract_minimal_context(pattern, requirement)
    
    def _extract_surgical_reference_context(self, pattern: UniversalPattern, action_type: str, requirement: str) -> str:
        """Extract surgical reference context that prevents AI from copying existing elements"""
        instance_num = int(action_type.split("_")[-1])
        
        if instance_num <= len(pattern.instances):
            target_start, target_end = pattern.instances[instance_num - 1]
            
            # Extract just ONE reference element with clear instructions
            reference_element = '\n'.join(self.lines[target_start:target_end + 1])
            
            # Create surgical context with explicit anti-duplication instructions
            surgical_context = f"""<!-- REFERENCE ELEMENT (for structure reference only - DO NOT COPY) -->
{reference_element}

<!-- SURGICAL INSTRUCTION: 
The above element is REFERENCE ONLY for understanding structure.
Generate a COMPLETELY NEW {pattern.pattern_name} element based on the requirement.
DO NOT copy the content above - create NEW content as specified.
REQUIREMENT: {requirement}
-->"""
            
            return surgical_context
        else:
            return self._create_minimal_structure(pattern.pattern_name)
    
    def _extract_instance_for_append(self, pattern: UniversalPattern, action_type: str) -> str:
        """Extract specific instance for appending content to it"""
        instance_num = int(action_type.split("_")[-1])
        
        if instance_num <= len(pattern.instances):
            start_line, end_line = pattern.instances[instance_num - 1]
            instance_lines = self.lines[start_line:end_line + 1]
            return '\n'.join(instance_lines)
        else:
            return self._create_minimal_structure(pattern.pattern_name)
    
    def _extract_instance_for_modification(self, pattern: UniversalPattern, action_type: str) -> str:
        """Extract specific instance for modification with minimal context"""
        instance_num = int(action_type.split("_")[-1])
        
        if instance_num <= len(pattern.instances):
            start_line, end_line = pattern.instances[instance_num - 1]
            
            # Include minimal context for modification
            context_start = max(0, start_line - 1)
            context_end = min(len(self.lines), end_line + 2)
            
            instance_lines = self.lines[context_start:context_end]
            return '\n'.join(instance_lines)
        else:
            return self._create_minimal_structure(pattern.pattern_name)
    
    def _extract_minimal_context(self, pattern: UniversalPattern, requirement: str) -> str:
        """Extract minimal context for other operations"""
        if not pattern.instances:
            return self._create_minimal_structure(pattern.pattern_name)
        
        # Extract first instance with minimal context
        start_line, end_line = pattern.instances[0]
        context_lines = 2
        
        context_start = max(0, start_line - context_lines)
        context_end = min(len(self.lines), end_line + context_lines + 1)
        
        chunk_lines = self.lines[context_start:context_end]
        return '\n'.join(chunk_lines)
    
    def _create_minimal_structure(self, pattern_name: str) -> str:
        """Create minimal structure when pattern is not found"""
        return f"""<!-- Minimal structure template for {pattern_name} -->
<{pattern_name}>
    <!-- Content will be generated based on requirements -->
</{pattern_name}>

<!-- INSTRUCTION: Generate a NEW {pattern_name} element with content based on the user requirement -->"""

    def extract_clean_reference_only(self, pattern: UniversalPattern, instance_num: int) -> str:
        """Extract a single clean reference element without encouraging copying"""
        
        if instance_num <= len(pattern.instances):
            start_line, end_line = pattern.instances[instance_num - 1]
            reference_content = '\n'.join(self.lines[start_line:end_line + 1])
            
            # Wrap with clear anti-copying instructions
            return f"""<!-- STRUCTURE REFERENCE ONLY - DO NOT COPY CONTENT -->
{reference_content}
<!-- END REFERENCE - GENERATE NEW CONTENT BASED ON REQUIREMENTS -->"""
        
        return self._create_minimal_structure(pattern.pattern_name)
    
    def get_parent_context(self, pattern: UniversalPattern, lines_before: int = 3, lines_after: int = 3) -> str:
        """Get parent context around the pattern for understanding placement"""
        if not pattern.instances:
            return ""
        
        # Use first instance for context
        start_line, end_line = pattern.instances[0]
        
        context_start = max(0, start_line - lines_before)
        context_end = min(len(self.lines), end_line + lines_after + 1)
        
        context_lines = self.lines[context_start:context_end]
        
        # Mark the target pattern area
        marked_lines = []
        for i, line in enumerate(context_lines):
            actual_line_num = context_start + i
            if start_line <= actual_line_num <= end_line:
                marked_lines.append(f"<!-- TARGET: {line} -->")
            else:
                marked_lines.append(line)
        
        return '\n'.join(marked_lines)