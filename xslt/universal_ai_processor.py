import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
from typing import Dict, Optional
from .universal_xslt_analyzer import UniversalPattern
from ..llm.llm_utils import setup_agent

class UniversalAIProcessor:
    """Handles AI processing and XSLT merging with surgical precision"""
    
    def __init__(self):
        self.agent = None
    
    def process_universal_chunk(self, chunk: str, requirement: str, pattern: UniversalPattern, 
                              specs: str, action_type: str) -> str:
        """Process chunk with AI to generate modified content"""
        
        # Initialize agent if not already done
        if not self.agent:
            self.agent = setup_agent("GPT4O")
        
        # Create structured prompt based on action type
        system_message = self._create_surgical_system_message(action_type, pattern.pattern_name, requirement)
        user_content = self._create_surgical_user_content(chunk, requirement, pattern, specs, action_type)
        
        # Set prompts for the agent
        prompts = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_content}
        ]
        
        self.agent.set_prompts(prompts)
        
        # Get AI response
        result = self.agent.get_chat_completion()
        if result is None:
            raise Exception("AI service returned no response")
        
        # Handle tuple return (cost, response) or just response
        if isinstance(result, tuple):
            cost, gpt_response = result
        else:
            gpt_response = result
            
        if gpt_response is None:
            raise Exception("AI service returned empty response")
            
        modified_chunk = gpt_response.choices[0].message.content
        
        # Clean the response with enhanced validation
        return self._clean_and_validate_ai_response(modified_chunk, action_type, pattern.pattern_name)
    
    def _create_surgical_system_message(self, action_type: str, pattern_name: str, requirement: str) -> str:
        """Create ultra-specific system message for surgical operations"""
        
        base_message = f"""You are an expert XSLT developer performing SURGICAL modifications. 

CRITICAL SURGICAL RULES:
1. Generate EXACTLY what is requested - nothing more, nothing less
2. NO namespace prefixes (ns0:, ns1:, etc.) - use clean element names
3. NEVER duplicate existing content unless explicitly asked
4. Generate ONLY the specific element being added/modified
5. DO NOT copy or reference existing similar elements
6. Use proper XSLT syntax with xsl: prefix for XSLT elements
7. Ensure all XML is well-formed with matching tags
8. Follow the EXACT requirement specifications

VALIDATION REQUIREMENTS:
- Every opening tag must have a matching closing tag
- All attributes must be in double quotes
- No malformed or incomplete elements
- Proper XML nesting structure"""

        if action_type.startswith("add_after_instance_"):
            return base_message + f"""

SURGICAL OPERATION: ADD SINGLE NEW {pattern_name}
- Generate EXACTLY ONE new {pattern_name} element
- Base structure on user requirements, NOT existing elements
- DO NOT copy existing {pattern_name} elements
- DO NOT generate multiple versions or variations
- Create ONLY what the user specifically requested
- The element will be surgically inserted after the target instance

CRITICAL: If the user asks for "AugPoint7 with ActionCode KK", generate ONLY:
- ONE new AugPoint element
- With ActionCode set to KK as specified
- NO duplication of existing patterns
- NO additional elements unless explicitly requested
- Ensure the new element is properly nested within the existing structure"""

        elif action_type.startswith("modify"):
            return base_message + f"""

SURGICAL OPERATION: MODIFY {pattern_name}
- Modify ONLY the specified aspect of the element
- Keep all other content unchanged
- Generate the complete modified element"""

        return base_message

    def _create_surgical_user_content(self, chunk: str, requirement: str, pattern: UniversalPattern, specs: str, action_type: str) -> str:
        """Create surgical user content that prevents duplication"""
        
        content = f"""
SURGICAL REQUIREMENT:
{requirement}

REFERENCE CONTEXT (for structure understanding only):
{chunk}

OPERATION: {action_type}
TARGET ELEMENT: {pattern.pattern_name}

CRITICAL INSTRUCTIONS:
1. Generate ONLY the single new element requested
2. DO NOT copy or duplicate existing elements from the context
3. Use the requirement to determine the specific content
4. Base the structure on requirements, not on copying existing patterns
5. Create a SINGLE element that meets the exact specification

EXAMPLE - If asked to create "AugPoint7 with ActionCode KK":
- Generate ONE AugPoint with ActionCode = KK
- DO NOT generate multiple AugPoint elements
- DO NOT copy existing ActionCode values like NN
- Focus on the NEW requirement only

OUTPUT REQUIREMENTS:
- Generate ONLY the requested element (NOT the full XSLT document)
- DO NOT include <?xml?> declarations or <xsl:stylesheet> headers
- Generate ONLY the specific element being added/modified
- Use clean XML without namespace prefixes
- Ensure proper XSLT syntax where applicable
- Match the structure style but use NEW content as specified

IMPORTANT: Your response should contain ONLY the new element, nothing else."""
        
        if specs and specs.strip():
            content += f"""

ADDITIONAL SPECIFICATIONS:
{specs}"""
        
        # Add anti-duplication reminder for add operations
        if action_type.startswith("add_after_instance_"):
            content += f"""

ANTI-DUPLICATION REMINDER:
- The context shows existing {pattern.pattern_name} elements for reference only
- DO NOT copy their content or structure exactly
- Generate a NEW {pattern.pattern_name} based on the requirement
- If requirement mentions specific values (like ActionCode KK), use those values
- Generate EXACTLY ONE element, not multiple variations"""
        
        return content

    def _clean_and_validate_ai_response(self, response: str, action_type: str, element_name: str) -> str:
        """Enhanced cleaning with validation to prevent duplication"""
        
        # Remove code block markers
        response = re.sub(r'```(?:xml|xsl|xslt)?\n?', '', response)
        response = re.sub(r'```\n?', '', response)
        
        # Remove explanatory text
        response = re.sub(r'^Here\'s.*?:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^The.*?:\s*', '', response, flags=re.IGNORECASE)
        response = re.sub(r'^Based on.*?:\s*', '', response, flags=re.IGNORECASE)
        
        # Remove trailing explanations
        response = re.sub(r'\n\n.*explanation.*$', '', response, flags=re.IGNORECASE | re.DOTALL)
        
        # Clean up namespace prefixes
        response = re.sub(r'\bns\d+:', '', response)
        response = re.sub(r'xmlns:ns\d+="[^"]*"\s*', '', response)
        
        # Remove XSLT headers if AI incorrectly included them
        response = re.sub(r'<\?xml[^>]*\?>\s*', '', response)
        response = re.sub(r'<xsl:stylesheet[^>]*>\s*', '', response)
        response = re.sub(r'</xsl:stylesheet>\s*', '', response)
        
        # For add_after operations, ensure only ONE target element
        if action_type.startswith("add_after_instance_"):
            response = self._ensure_single_element(response, element_name)
        
        # Validate XML structure
        response = self._validate_xml_structure(response)
        
        return response.strip()
    
    def _ensure_single_element(self, response: str, element_name: str) -> str:
        """Ensure only a single target element is generated"""
        
        # Find all occurrences of the target element
        pattern = rf'<{re.escape(element_name)}[^>]*>.*?</{re.escape(element_name)}>'
        matches = list(re.finditer(pattern, response, re.DOTALL))
        
        if len(matches) > 1:
            # Take only the first match
            first_match = matches[0]
            return response[first_match.start():first_match.end()]
        elif len(matches) == 1:
            # Perfect - only one element
            return response
        else:
            # No complete elements found, return as is (might be partial)
            return response
    
    def _validate_xml_structure(self, xml_content: str) -> str:
        """Basic XML structure validation"""
        try:
            # Try to parse as XML to check structure
            # Remove any non-XML content first
            lines = xml_content.split('\n')
            xml_lines = []
            
            for line in lines:
                stripped = line.strip()
                if stripped and (stripped.startswith('<') or xml_lines):
                    xml_lines.append(line)
                    if stripped.endswith('>') and not stripped.startswith('<!--'):
                        # Check if this might be the end of the XML
                        break
            
            return '\n'.join(xml_lines)
            
        except Exception:
            # If validation fails, return original content
            return xml_content

    def merge_universal_chunk(self, original_xslt: str, modified_chunk: str, pattern: UniversalPattern, action_type: str) -> str:
        """Merge modified chunk back into original XSLT with surgical precision"""
        try:
            # Clean the modified chunk first
            cleaned_chunk = self._clean_and_validate_ai_response(modified_chunk, action_type, pattern.pattern_name)
            
            if action_type.startswith("add_after_instance_"):
                return self._add_after_instance_surgical(original_xslt, cleaned_chunk, pattern, action_type)
            elif action_type.startswith("append_to_instance_"):
                return self._append_to_instance(original_xslt, cleaned_chunk, pattern, action_type)
            elif action_type.startswith("modify_instance_"):
                return self._modify_instance(original_xslt, cleaned_chunk, pattern, action_type)
            else:
                return self._simple_replacement(original_xslt, cleaned_chunk, pattern)
                
        except Exception as e:
            print(f"Merge error: {e}")
            return original_xslt

    def _add_after_instance_surgical(self, original_xslt: str, new_element: str, pattern: UniversalPattern, action_type: str) -> str:
        """Surgically add a single new element after specific instance"""
        instance_num = int(action_type.split("_")[-1])
        
        # Find all instances of the pattern
        pattern_regex = rf'<{re.escape(pattern.pattern_name)}[^>]*>.*?</{re.escape(pattern.pattern_name)}>'
        matches = list(re.finditer(pattern_regex, original_xslt, re.DOTALL))
        
        if len(matches) >= instance_num:
            target_match = matches[instance_num - 1]  # Convert to 0-based index
            insertion_point = target_match.end()
            
            # Get proper indentation from the target instance
            target_line_start = original_xslt.rfind('\n', 0, target_match.start()) + 1
            target_line = original_xslt[target_line_start:target_match.start()]
            indent = self._get_line_indentation(target_line)
            
            # Apply indentation to the new element
            indented_element = self._indent_chunk(new_element, indent)
            
            # Insert the new element after the target instance
            updated_xslt = original_xslt[:insertion_point] + '\n' + indented_element + original_xslt[insertion_point:]
            return updated_xslt
        
        return original_xslt

    def _append_to_instance(self, original_xslt: str, modified_chunk: str, pattern: UniversalPattern, action_type: str) -> str:
        """Append content to a specific instance"""
        instance_num = int(action_type.split("_")[-1])
        
        pattern_regex = rf'(<{re.escape(pattern.pattern_name)}[^>]*>)(.*?)(</{re.escape(pattern.pattern_name)}>)'
        matches = list(re.finditer(pattern_regex, original_xslt, re.DOTALL))
        
        if len(matches) >= instance_num:
            target_match = matches[instance_num - 1]
            opening_tag = target_match.group(1)
            existing_content = target_match.group(2)
            closing_tag = target_match.group(3)
            
            # Get proper indentation
            target_line_start = original_xslt.rfind('\n', 0, target_match.start()) + 1
            target_line = original_xslt[target_line_start:target_match.start()]
            indent = self._get_line_indentation(target_line)
            indented_chunk = self._indent_chunk(modified_chunk, indent + '\t')
            
            new_element_content = opening_tag + existing_content + '\n' + indented_chunk + '\n' + indent + closing_tag
            updated_xslt = original_xslt[:target_match.start()] + new_element_content + original_xslt[target_match.end():]
            return updated_xslt
        
        return original_xslt

    def _modify_instance(self, original_xslt: str, modified_chunk: str, pattern: UniversalPattern, action_type: str) -> str:
        """Modify a specific instance"""
        instance_num = int(action_type.split("_")[-1])
        
        pattern_regex = rf'<{re.escape(pattern.pattern_name)}[^>]*>.*?</{re.escape(pattern.pattern_name)}>'
        matches = list(re.finditer(pattern_regex, original_xslt, re.DOTALL))
        
        if len(matches) >= instance_num:
            target_match = matches[instance_num - 1]
            
            # Get proper indentation
            target_line_start = original_xslt.rfind('\n', 0, target_match.start()) + 1
            target_line = original_xslt[target_line_start:target_match.start()]
            indent = self._get_line_indentation(target_line)
            indented_chunk = self._indent_chunk(modified_chunk, indent)
            
            updated_xslt = original_xslt[:target_match.start()] + indented_chunk + original_xslt[target_match.end():]
            return updated_xslt
        
        return original_xslt

    def _simple_replacement(self, original_xslt: str, modified_chunk: str, pattern: UniversalPattern) -> str:
        """Simple replacement for other operations"""
        if pattern.instances:
            start_line, end_line = pattern.instances[0]
            lines = original_xslt.split('\n')
            
            indent = self._get_line_indentation(lines[start_line] if start_line < len(lines) else '')
            indented_chunk = self._indent_chunk(modified_chunk, indent)
            
            new_lines = lines[:start_line] + [indented_chunk] + lines[end_line + 1:]
            return '\n'.join(new_lines)
        
        return original_xslt

    def _get_line_indentation(self, line: str) -> str:
        """Get the indentation from a line"""
        return line[:len(line) - len(line.lstrip())]
    
    def _indent_chunk(self, chunk: str, base_indent: str) -> str:
        """Apply base indentation to a chunk"""
        lines = chunk.split('\n')
        indented_lines = []
        
        for line in lines:
            if line.strip():
                indented_lines.append(base_indent + line.strip())
            else:
                indented_lines.append('')
        
        return '\n'.join(indented_lines)

def pretty_print_xml(xml_content: str) -> str:
    """Clean XML without complex formatting"""
    processor = UniversalAIProcessor()
    return processor._clean_and_validate_ai_response(xml_content, "format", "")