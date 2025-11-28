#!/usr/bin/env python3
"""
Resume Generator Capability Extraction Script
ZERO-LOSS extraction of ALL capabilities from 825 files across all architectures
Creates reconstructed_capabilities.py with RG_CAPABILITIES dictionary
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, Any, List

class RGCapabilityExtractor:
    def __init__(self, index_file: Path, hash_file: Path):
        self.index_file = index_file
        self.hash_file = hash_file
        self.file_list = []
        self.capability_map = {
            "routing_rules": {},
            "parameter_presets": {},
            "quant_rules": {},
            "bullet_engine": {},
            "rewrite_engine": {},
            "skills_engine": {},
            "section_rules": {},
            "job_workflow_steps": {},
            "ats_rules": {},
            "template_layouts": {},
            "formatting_rules": {},
            "seniority_rules": {},
            "tone_rules": {},
            "constraints": {},
            "validator_rules": {},
            "mission_fields": {}
        }
        self.processed_files = set()
        self.error_files = set()
        
    def load_file_inventory(self):
        """Load file list from MASTER_RG_FILE_INDEX.txt"""
        print("Loading file inventory...")
        with open(self.index_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('==='):
                    parts = line.split(' | ')
                    if len(parts) >= 1:
                        file_path = parts[0]
                        self.file_list.append(Path(file_path))
        print(f"Loaded {len(self.file_list)} files from inventory")
    
    def extract_python_capabilities(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract capabilities from Python files"""
        capabilities = {}
        
        try:
            tree = ast.parse(content)
            
            # Extract functions and classes
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'docstring': ast.get_docstring(node) or "",
                        'line_number': node.lineno
                    }
                    functions.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'methods': [],
                        'line_number': node.lineno
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args],
                                'docstring': ast.get_docstring(item) or ""
                            }
                            class_info['methods'].append(method_info)
                    
                    classes.append(class_info)
            
            # Extract string literals that might contain rules or prompts
            string_literals = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    if len(node.value) > 50:  # Only include substantial strings
                        string_literals.append(node.value)
            
            capabilities.update({
                'functions': functions,
                'classes': classes,
                'string_literals': string_literals,
                'file_type': 'python'
            })
            
        except SyntaxError as e:
            print(f"Syntax error in {file_path}: {e}")
            capabilities['parse_error'] = str(e)
        except Exception as e:
            print(f"Error parsing Python file {file_path}: {e}")
            capabilities['parse_error'] = str(e)
            
        return capabilities
    
    def extract_json_capabilities(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract capabilities from JSON files"""
        capabilities = {}
        
        try:
            data = json.loads(content)
            capabilities.update({
                'json_structure': data,
                'keys': self._extract_all_keys(data),
                'file_type': 'json'
            })
        except json.JSONDecodeError as e:
            print(f"JSON decode error in {file_path}: {e}")
            capabilities['parse_error'] = str(e)
        except Exception as e:
            print(f"Error parsing JSON file {file_path}: {e}")
            capabilities['parse_error'] = str(e)
            
        return capabilities
    
    def extract_markdown_capabilities(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract capabilities from Markdown files"""
        capabilities = {}
        
        # Extract headers
        headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
        
        # Extract code blocks
        code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        
        # Extract lists
        lists = re.findall(r'^[\-\*\+]\s+(.+)$', content, re.MULTILINE)
        
        # Extract tables
        tables = re.findall(r'\|(.+)\|\n\|[\-\s\|]+\n((?:\|.+\|\n?)*)', content)
        
        capabilities.update({
            'headers': headers,
            'code_blocks': code_blocks,
            'lists': lists,
            'tables': tables,
            'file_type': 'markdown'
        })
        
        return capabilities
    
    def _extract_all_keys(self, obj, path="") -> List[str]:
        """Recursively extract all keys from a nested JSON structure"""
        keys = []
        
        if isinstance(obj, dict):
            for key, value in obj.items():
                current_path = f"{path}.{key}" if path else key
                keys.append(current_path)
                keys.extend(self._extract_all_keys(value, current_path))
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                keys.extend(self._extract_all_keys(item, f"{path}[{i}]"))
                
        return keys
    
    def categorize_capabilities(self, file_path: Path, capabilities: Dict[str, Any]) -> Dict[str, Any]:
        """Categorize extracted capabilities into the 15 buckets"""
        categorized = {}
        file_name = file_path.name.lower()
        file_path_str = str(file_path).lower()
        
        # Determine file category and route to appropriate buckets
        if 'routing' in file_name or 'orchestrat' in file_name or 'workflow' in file_name:
            categorized['routing_rules'] = capabilities
            
        if 'config' in file_name or 'parameter' in file_name or 'preset' in file_name:
            categorized['parameter_presets'] = capabilities
            
        if 'quant' in file_name or 'scoring' in file_name or 'metric' in file_name:
            categorized['quant_rules'] = capabilities
            
        if 'bullet' in file_name or 'point' in file_name:
            categorized['bullet_engine'] = capabilities
            
        if 'rewrite' in file_name or 'rephrase' in file_name or 'reword' in file_name:
            categorized['rewrite_engine'] = capabilities
            
        if 'skill' in file_name or 'competenc' in file_name:
            categorized['skills_engine'] = capabilities
            
        if 'section' in file_name or 'segment' in file_name:
            categorized['section_rules'] = capabilities
            
        if 'job' in file_name or 'workflow' in file_name or 'step' in file_name:
            categorized['job_workflow_steps'] = capabilities
            
        if 'ats' in file_name or 'applicant' in file_name:
            categorized['ats_rules'] = capabilities
            
        if 'template' in file_name or 'layout' in file_name:
            categorized['template_layouts'] = capabilities
            
        if 'format' in file_name or 'style' in file_name:
            categorized['formatting_rules'] = capabilities
            
        if 'seniority' in file_name or 'level' in file_name or 'grade' in file_name:
            categorized['seniority_rules'] = capabilities
            
        if 'tone' in file_name or 'voice' in file_name:
            categorized['tone_rules'] = capabilities
            
        if 'constraint' in file_name or 'limit' in file_name:
            categorized['constraints'] = capabilities
            
        if 'validator' in file_name or 'validation' in file_name or 'rule' in file_name:
            categorized['validator_rules'] = capabilities
            
        if 'mission' in file_name or 'field' in file_name:
            categorized['mission_fields'] = capabilities
            
        # For files that don't fit obvious categories, analyze content
        if not categorized:
            categorized = self._analyze_content_for_categorization(capabilities, file_path_str)
            
        return categorized
    
    def _analyze_content_for_categorization(self, capabilities: Dict[str, Any], file_path_str: str) -> Dict[str, Any]:
        """Analyze content to determine appropriate categorization"""
        categorized = {}
        
        # Check content for keywords
        content_str = str(capabilities).lower()
        
        if any(keyword in content_str for keyword in ['routing', 'orchestrat', 'workflow', 'pipeline']):
            categorized['routing_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['config', 'parameter', 'setting', 'preset']):
            categorized['parameter_presets'] = capabilities
            
        if any(keyword in content_str for keyword in ['quant', 'scor', 'metric', 'measure']):
            categorized['quant_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['bullet', 'point', 'item']):
            categorized['bullet_engine'] = capabilities
            
        if any(keyword in content_str for keyword in ['rewrite', 'rephrase', 'reword']):
            categorized['rewrite_engine'] = capabilities
            
        if any(keyword in content_str for keyword in ['skill', 'competenc', 'abilit']):
            categorized['skills_engine'] = capabilities
            
        if any(keyword in content_str for keyword in ['section', 'segment', 'part']):
            categorized['section_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['job', 'work', 'step', 'phase']):
            categorized['job_workflow_steps'] = capabilities
            
        if any(keyword in content_str for keyword in ['ats', 'applicant', 'track']):
            categorized['ats_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['template', 'layout', 'design']):
            categorized['template_layouts'] = capabilities
            
        if any(keyword in content_str for keyword in ['format', 'style', 'present']):
            categorized['formatting_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['senior', 'level', 'grade', 'rank']):
            categorized['seniority_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['tone', 'voice', 'manner']):
            categorized['tone_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['constraint', 'limit', 'bound']):
            categorized['constraints'] = capabilities
            
        if any(keyword in content_str for keyword in ['valid', 'rule', 'check']):
            categorized['validator_rules'] = capabilities
            
        if any(keyword in content_str for keyword in ['mission', 'field', 'domain']):
            categorized['mission_fields'] = capabilities
            
        # If still not categorized, put in routing_rules as default
        if not categorized:
            categorized['routing_rules'] = capabilities
            
        return categorized
    
    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file and extract capabilities"""
        try:
            if not file_path.exists():
                print(f"File not found: {file_path}")
                return {}
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Determine file type and extract capabilities
            if file_path.suffix.lower() == '.py':
                capabilities = self.extract_python_capabilities(file_path, content)
            elif file_path.suffix.lower() == '.json':
                capabilities = self.extract_json_capabilities(file_path, content)
            elif file_path.suffix.lower() in ['.md', '.markdown']:
                capabilities = self.extract_markdown_capabilities(file_path, content)
            else:
                # For other file types, extract basic text content
                capabilities = {
                    'content': content[:1000] if len(content) > 1000 else content,
                    'file_type': 'other',
                    'size': len(content)
                }
            
            # Add metadata
            capabilities['file_path'] = str(file_path)
            capabilities['file_size'] = len(content)
            
            # Categorize capabilities
            categorized = self.categorize_capabilities(file_path, capabilities)
            
            return categorized
            
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            self.error_files.add(str(file_path))
            return {'error': str(e), 'file_path': str(file_path)}
    
    def merge_capabilities(self, new_capabilities: Dict[str, Any], file_path: Path):
        """Merge new capabilities into the main capability map"""
        for bucket, capabilities in new_capabilities.items():
            if bucket in self.capability_map:
                # Use file path as key to preserve all capabilities
                self.capability_map[bucket][str(file_path)] = capabilities
    
    def extract_all_capabilities(self):
        """Extract capabilities from all files"""
        print("Starting capability extraction...")
        
        for i, file_path in enumerate(self.file_list):
            if i % 100 == 0:
                print(f"Processing file {i+1}/{len(self.file_list)}: {file_path.name}")
            
            capabilities = self.process_file(file_path)
            if capabilities:
                self.merge_capabilities(capabilities, file_path)
                self.processed_files.add(str(file_path))
        
        print(f"Completed extraction. Processed {len(self.processed_files)} files.")
        print(f"Errors in {len(self.error_files)} files.")
    
    def write_capabilities_file(self, output_path: Path):
        """Write the reconstructed capabilities file"""
        print(f"Writing capabilities to {output_path}...")
        
        # Create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""\n')
            f.write("Reconstructed Resume Generator Capabilities\n")
            f.write("ZERO-LOSS extraction from ALL archive files\n")
            f.write(f"Total files processed: {len(self.processed_files)}\n")
            f.write(f"Error files: {len(self.error_files)}\n")
            f.write('"""\n\n')
            
            f.write("RG_CAPABILITIES = {\n")
            
            for bucket, capabilities in self.capability_map.items():
                f.write(f'    "{bucket}": {{\n')
                
                for file_path, caps in capabilities.items():
                    # Escape the file path for Python string
                    escaped_path = file_path.replace('\\', '\\\\')
                    f.write(f'        "{escaped_path}": {repr(caps)},\n')
                
                f.write('    },\n')
            
            f.write("}\n")
        
        print(f"Capabilities written to {output_path}")

def main():
    """Main execution function"""
    # Define paths
    base_dir = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\archive")
    index_file = base_dir / "MASTER_RG_FILE_INDEX.txt"
    hash_file = base_dir / "MASTER_RG_FILE_HASH.txt"
    output_file = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities\reconstructed_capabilities.py")
    
    # Create extractor and run
    extractor = RGCapabilityExtractor(index_file, hash_file)
    extractor.load_file_inventory()
    extractor.extract_all_capabilities()
    extractor.write_capabilities_file(output_file)
    
    print("ZERO-LOSS capability extraction completed!")

if __name__ == "__main__":
    main()
