import re
import xml.etree.ElementTree as ET
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class UniversalPattern:
    """Represents a detected pattern in XSLT"""
    pattern_name: str
    pattern_type: str  # 'xml_element', 'template', 'loop', 'conditional'
    instance_count: int
    instances: List[Tuple[int, int]]  # List of (start_line, end_line) tuples
    sample_content: str
    xpath_pattern: Optional[str] = None

class UniversalXSLTAnalyzer:
    """Universal XSLT analyzer that detects all types of repeating patterns"""
    
    def __init__(self, xslt_content: str):
        self.xslt_content = xslt_content
        self.lines = xslt_content.split('\n')
        self.patterns = []
        
    def find_all_repeating_patterns(self) -> List[UniversalPattern]:
        """Find all repeating patterns in the XSLT"""
        patterns = []
        
        # Find different types of patterns
        patterns.extend(self._find_repeating_xml_elements())
        patterns.extend(self._find_repeating_templates())
        patterns.extend(self._find_loop_based_patterns())
        patterns.extend(self._find_conditional_patterns())
        
        # Filter patterns with multiple instances
        self.patterns = [p for p in patterns if p.instance_count > 1]
        return self.patterns
    
    def _find_repeating_xml_elements(self) -> List[UniversalPattern]:
        """Find repeating XML elements (non-XSLT elements)"""
        patterns = []
        element_counts = defaultdict(list)
        
        # Pattern to match XML elements (excluding XSLT namespace)
        element_pattern = r'<([^/\s!?][^>\s]*?)(?:\s[^>]*)?>.*?</\1>'
        
        for i, line in enumerate(self.lines):
            # Skip XSLT elements
            if 'xsl:' in line or '<?xml' in line or '<!--' in line:
                continue
                
            # Find opening tags
            opening_tags = re.findall(r'<([^/\s!?][^>\s]*?)(?:\s[^>]*)?>', line)
            for tag in opening_tags:
                if ':' not in tag and tag not in ['xsl', 'xml']:  # Skip namespaced elements
                    element_counts[tag].append(i)
        
        # Create patterns for elements that appear multiple times
        for element_name, line_numbers in element_counts.items():
            if len(line_numbers) > 1:
                instances = self._find_element_instances(element_name)
                if instances:
                    sample_content = self._extract_sample_content(instances[0])
                    pattern = UniversalPattern(
                        pattern_name=element_name,
                        pattern_type='xml_element',
                        instance_count=len(instances),
                        instances=instances,
                        sample_content=sample_content,
                        xpath_pattern=f'//{element_name}'
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_repeating_templates(self) -> List[UniversalPattern]:
        """Find repeating XSLT templates"""
        patterns = []
        template_pattern = r'<xsl:template[^>]*match="([^"]*)"[^>]*>'
        
        template_matches = defaultdict(list)
        
        for i, line in enumerate(self.lines):
            match = re.search(template_pattern, line)
            if match:
                template_match = match.group(1)
                template_matches[template_match].append(i)
        
        # Create patterns for templates that appear multiple times
        for match_pattern, line_numbers in template_matches.items():
            if len(line_numbers) > 1:
                instances = []
                for line_num in line_numbers:
                    start_line = line_num
                    end_line = self._find_template_end(start_line)
                    instances.append((start_line, end_line))
                
                if instances:
                    sample_content = self._extract_sample_content(instances[0])
                    pattern = UniversalPattern(
                        pattern_name=f"template_{match_pattern.replace('/', '_')}",
                        pattern_type='template',
                        instance_count=len(instances),
                        instances=instances,
                        sample_content=sample_content,
                        xpath_pattern=match_pattern
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_loop_based_patterns(self) -> List[UniversalPattern]:
        """Find patterns within xsl:for-each loops"""
        patterns = []
        
        for i, line in enumerate(self.lines):
            if '<xsl:for-each' in line:
                # Extract the select attribute
                select_match = re.search(r'select="([^"]*)"', line)
                if select_match:
                    select_path = select_match.group(1)
                    start_line = i
                    end_line = self._find_loop_end(start_line)
                    
                    # Extract content within the loop
                    loop_content = '\n'.join(self.lines[start_line:end_line + 1])
                    
                    # Find elements within this loop
                    inner_elements = self._extract_loop_elements(loop_content)
                    
                    for element in inner_elements:
                        pattern = UniversalPattern(
                            pattern_name=f"loop_{element}",
                            pattern_type='loop',
                            instance_count=1,  # Each loop is considered one instance
                            instances=[(start_line, end_line)],
                            sample_content=loop_content[:200],
                            xpath_pattern=f"{select_path}/{element}"
                        )
                        patterns.append(pattern)
        
        return patterns
    
    def _find_conditional_patterns(self) -> List[UniversalPattern]:
        """Find patterns within xsl:if or xsl:choose blocks"""
        patterns = []
        
        for i, line in enumerate(self.lines):
            if '<xsl:if' in line or '<xsl:when' in line:
                test_match = re.search(r'test="([^"]*)"', line)
                if test_match:
                    test_condition = test_match.group(1)
                    start_line = i
                    
                    if '<xsl:if' in line:
                        end_line = self._find_if_end(start_line)
                        pattern_name = f"if_{test_condition.replace('/', '_').replace('@', 'attr_')}"
                    else:
                        end_line = self._find_when_end(start_line)
                        pattern_name = f"when_{test_condition.replace('/', '_').replace('@', 'attr_')}"
                    
                    content = '\n'.join(self.lines[start_line:end_line + 1])
                    
                    pattern = UniversalPattern(
                        pattern_name=pattern_name[:50],  # Limit name length
                        pattern_type='conditional',
                        instance_count=1,
                        instances=[(start_line, end_line)],
                        sample_content=content[:200],
                        xpath_pattern=test_condition
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _find_element_instances(self, element_name: str) -> List[Tuple[int, int]]:
        """Find all instances of a specific XML element"""
        instances = []
        i = 0
        
        while i < len(self.lines):
            line = self.lines[i]
            
            # Look for opening tag
            opening_pattern = f'<{element_name}(?:\\s[^>]*)?>|<{element_name}/>'
            if re.search(opening_pattern, line):
                start_line = i
                
                # Check if it's a self-closing tag
                if f'<{element_name}/>' in line:
                    instances.append((start_line, start_line))
                else:
                    # Find the closing tag
                    end_line = self._find_closing_tag(element_name, start_line)
                    if end_line is not None:
                        instances.append((start_line, end_line))
            i += 1
        
        return instances
    
    def _find_closing_tag(self, element_name: str, start_line: int) -> Optional[int]:
        """Find the closing tag for an element starting at start_line"""
        open_count = 1
        
        for i in range(start_line + 1, len(self.lines)):
            line = self.lines[i]
            
            # Count opening tags
            open_tags = len(re.findall(f'<{element_name}(?:\\s[^>]*)?>(?!</)', line))
            open_count += open_tags
            
            # Count closing tags
            close_tags = len(re.findall(f'</{element_name}>', line))
            open_count -= close_tags
            
            if open_count == 0:
                return i
        
        return None
    
    def _find_template_end(self, start_line: int) -> int:
        """Find the end of an XSLT template"""
        for i in range(start_line + 1, len(self.lines)):
            if '</xsl:template>' in self.lines[i]:
                return i
        return len(self.lines) - 1
    
    def _find_loop_end(self, start_line: int) -> int:
        """Find the end of an xsl:for-each loop"""
        for i in range(start_line + 1, len(self.lines)):
            if '</xsl:for-each>' in self.lines[i]:
                return i
        return len(self.lines) - 1
    
    def _find_if_end(self, start_line: int) -> int:
        """Find the end of an xsl:if block"""
        for i in range(start_line + 1, len(self.lines)):
            if '</xsl:if>' in self.lines[i]:
                return i
        return len(self.lines) - 1
    
    def _find_when_end(self, start_line: int) -> int:
        """Find the end of an xsl:when block"""
        for i in range(start_line + 1, len(self.lines)):
            if '</xsl:when>' in self.lines[i] or '</xsl:choose>' in self.lines[i]:
                return i
        return len(self.lines) - 1
    
    def _extract_loop_elements(self, loop_content: str) -> List[str]:
        """Extract XML elements from loop content"""
        elements = []
        element_pattern = r'<([^/\s!?xsl][^>\s]*?)(?:\s[^>]*)?>.*?</\1>'
        matches = re.findall(r'<([^/\s!?][^>\s]*?)(?:\s[^>]*)?>', loop_content)
        
        for match in matches:
            if not match.startswith('xsl:') and match not in elements:
                elements.append(match)
        
        return elements
    
    def _extract_sample_content(self, instance: Tuple[int, int]) -> str:
        """Extract sample content from an instance"""
        start_line, end_line = instance
        content_lines = self.lines[start_line:end_line + 1]
        return '\n'.join(content_lines)
    
    def get_pattern_by_name(self, pattern_name: str) -> Optional[UniversalPattern]:
        """Get a pattern by its name"""
        for pattern in self.patterns:
            if pattern.pattern_name == pattern_name:
                return pattern
        return None
    
    def get_patterns_by_type(self, pattern_type: str) -> List[UniversalPattern]:
        """Get all patterns of a specific type"""
        return [p for p in self.patterns if p.pattern_type == pattern_type]
