import re
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class UserIntent:
    """Represents user intent analysis"""
    action_type: str  # 'add', 'modify', 'delete'
    target_nodes: List[str]
    placement_preference: Optional[str] = None  # 'after_last', 'before_first', 'after_instance_N'
    confidence: float = 0.0

class UniversalUserInteraction:
    """Handles user intent detection and node selection UI"""
    
    @staticmethod
    def extract_nodes_from_requirements(requirement_text: str) -> List[str]:
        """Extract node names mentioned in user requirements"""
        # Common XML element patterns
        node_patterns = [
            r'<([A-Za-z][A-Za-z0-9]*)[^>]*>',  # XML tags
            r'(?:add|create|new|modify|update|change)\s+(?:a\s+)?([A-Z][A-Za-z0-9]*)',  # "add AugPoint"
            r'([A-Z][A-Za-z0-9]*)\s+(?:element|node|tag)',  # "AugPoint element"
            r'(?:with|having)\s+([A-Z][A-Za-z0-9]*)',  # "with ActionCode"
        ]
        
        nodes = set()
        for pattern in node_patterns:
            matches = re.findall(pattern, requirement_text, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match[1]
                if match and len(match) > 1 and match[0].isupper():
                    nodes.add(match)
        
        return list(nodes)
    
    @staticmethod
    def detect_intent(requirement_text: str) -> UserIntent:
        """Detect user intent from requirements text"""
        add_keywords = ['create', 'add', 'new', 'append', 'insert', 'another']
        modify_keywords = ['modify', 'update', 'change', 'edit', 'alter', 'fix']
        delete_keywords = ['delete', 'remove', 'eliminate']
        
        text_lower = requirement_text.lower()
        
        # Calculate scores for each intent
        add_score = sum(1 for keyword in add_keywords if keyword in text_lower)
        modify_score = sum(1 for keyword in modify_keywords if keyword in text_lower)
        delete_score = sum(1 for keyword in delete_keywords if keyword in text_lower)
        
        # Determine primary intent
        if add_score >= modify_score and add_score >= delete_score:
            action_type = 'add'
            confidence = add_score / (add_score + modify_score + delete_score + 1)
        elif modify_score >= delete_score:
            action_type = 'modify'
            confidence = modify_score / (add_score + modify_score + delete_score + 1)
        else:
            action_type = 'delete'
            confidence = delete_score / (add_score + modify_score + delete_score + 1)
        
        target_nodes = UniversalUserInteraction.extract_nodes_from_requirements(requirement_text)
        
        return UserIntent(
            action_type=action_type,
            target_nodes=target_nodes,
            confidence=confidence
        )
    
    @staticmethod
    def check_xpath_matches(xslt_content: str, node_name: str) -> int:
        """Count instances of a node in XSLT content"""
        pattern = f'<{node_name}(?:\\s[^>]*)?>.*?</{node_name}>|<{node_name}/>'
        matches = re.findall(pattern, xslt_content, re.DOTALL)
        return len(matches)
    
    @staticmethod
    def generate_placement_options(node_name: str, instance_count: int, intent: UserIntent) -> List[Dict]:
        """Generate placement options based on intent and instance count"""
        options = []
        
        if intent.action_type == 'add':
            if instance_count > 0:
                # Add after each existing instance
                for i in range(1, instance_count + 1):
                    ordinal = UniversalUserInteraction._get_ordinal(i)
                    options.append({
                        'label': f'After {node_name}{i} ({ordinal} instance)',
                        'value': f'add_after_instance_{i}',
                        'description': f'Add new {node_name} after the {ordinal} existing instance'
                    })
                
                # Add at the end
                options.append({
                    'label': f'After last {node_name}',
                    'value': 'add_after_last',
                    'description': f'Add new {node_name} after all existing instances'
                })
                
                # Add at the beginning
                options.append({
                    'label': f'Before first {node_name}',
                    'value': 'add_before_first',
                    'description': f'Add new {node_name} before all existing instances'
                })
            else:
                # No existing instances
                options.append({
                    'label': f'Create new {node_name}',
                    'value': 'add_new',
                    'description': f'Create the first {node_name} element'
                })
        
        elif intent.action_type == 'modify':
            if instance_count > 0:
                for i in range(1, instance_count + 1):
                    ordinal = UniversalUserInteraction._get_ordinal(i)
                    options.append({
                        'label': f'Modify {node_name}{i} ({ordinal} instance)',
                        'value': f'modify_instance_{i}',
                        'description': f'Modify the {ordinal} {node_name} instance'
                    })
                
                # Option to modify all
                if instance_count > 1:
                    options.append({
                        'label': f'Modify all {node_name} instances',
                        'value': 'modify_all',
                        'description': f'Apply changes to all {instance_count} {node_name} instances'
                    })
            else:
                options.append({
                    'label': f'No {node_name} found to modify',
                    'value': 'no_instances',
                    'description': f'Cannot modify - no {node_name} elements exist'
                })
        
        elif intent.action_type == 'delete':
            if instance_count > 0:
                for i in range(1, instance_count + 1):
                    ordinal = UniversalUserInteraction._get_ordinal(i)
                    options.append({
                        'label': f'Delete {node_name}{i} ({ordinal} instance)',
                        'value': f'delete_instance_{i}',
                        'description': f'Delete the {ordinal} {node_name} instance'
                    })
            else:
                options.append({
                    'label': f'No {node_name} found to delete',
                    'value': 'no_instances',
                    'description': f'Cannot delete - no {node_name} elements exist'
                })
        
        return options
    
    @staticmethod
    def _get_ordinal(number: int) -> str:
        """Convert number to ordinal (1st, 2nd, 3rd, etc.)"""
        if 10 <= number % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(number % 10, 'th')
        return f"{number}{suffix}"
    
    @staticmethod
    def parse_action_selection(selection_value: str) -> Dict:
        """Parse the selected action into components"""
        parts = selection_value.split('_')
        
        result = {
            'action': parts[0],  # add, modify, delete
            'target': '_'.join(parts[1:-1]) if len(parts) > 2 else parts[1],
            'instance': None
        }
        
        # Extract instance number if present
        if parts[-1].isdigit():
            result['instance'] = int(parts[-1])
        elif parts[-1] in ['last', 'first', 'all', 'new']:
            result['target'] = parts[-1]
        
        return result
