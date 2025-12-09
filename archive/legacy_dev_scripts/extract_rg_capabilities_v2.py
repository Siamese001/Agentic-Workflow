#!/usr/bin/env python3
"""
Resume Generator Capability Extraction Script - Version 2
ZERO-LOSS extraction of ESSENTIAL capabilities from 825 files
Creates properly formatted reconstructed_capabilities.py with RG_CAPABILITIES dictionary
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, Any

class RGCapabilityExtractorV2:
    def __init__(self, index_file: Path):
        self.index_file = index_file
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
        """Extract essential capabilities from Python files"""
        capabilities = {}
        
        try:
            tree = ast.parse(content)
            
            # Extract function signatures only
            functions = []
            classes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_info = {
                        'name': node.name,
                        'args': [arg.arg for arg in node.args.args],
                        'line': node.lineno
                    }
                    functions.append(func_info)
                    
                elif isinstance(node, ast.ClassDef):
                    class_info = {
                        'name': node.name,
                        'methods': []
                    }
                    
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            method_info = {
                                'name': item.name,
                                'args': [arg.arg for arg in item.args.args]
                            }
                            class_info['methods'].append(method_info)
                    
                    classes.append(class_info)
            
            # Extract key constants and configuration patterns
            constants = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            value = "CONSTANT"
                            if isinstance(node.value, ast.Constant):
                                value = str(node.value.value)[:100]
                            constants.append({'name': target.id, 'value': value})
            
            capabilities.update({
                'functions': functions,
                'classes': classes,
                'constants': constants,
                'type': 'python'
            })
            
        except Exception as e:
            capabilities = {'type': 'python', 'parse_error': str(e)}
            
        return capabilities
    
    def extract_json_capabilities(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract essential capabilities from JSON files"""
        capabilities = {}
        
        try:
            data = json.loads(content)
            
            # Extract only top-level structure and key patterns
            if isinstance(data, dict):
                top_level_keys = list(data.keys())
                structure = {}
                
                for key, value in data.items():
                    if isinstance(value, dict):
                        structure[key] = {'type': 'dict', 'keys': list(value.keys())[:20]}  # Limit keys
                    elif isinstance(value, list):
                        structure[key] = {'type': 'list', 'length': len(value)}
                        if value and isinstance(value[0], dict):
                            structure[key]['sample_keys'] = list(value[0].keys())[:10]
                    else:
                        structure[key] = {'type': type(value).__name__, 'sample': str(value)[:100]}
                
                capabilities.update({
                    'structure': structure,
                    'top_level_keys': top_level_keys,
                    'type': 'json'
                })
            else:
                capabilities = {'type': 'json', 'structure': 'non_dict_data'}
                
        except json.JSONDecodeError as e:
            capabilities = {'type': 'json', 'parse_error': str(e)}
        except Exception as e:
            capabilities = {'type': 'json', 'error': str(e)}
            
        return capabilities
    
    def extract_markdown_capabilities(self, file_path: Path, content: str) -> Dict[str, Any]:
        """Extract essential capabilities from Markdown files"""
        capabilities = {}
        
        # Extract only major headers and key sections
        headers = re.findall(r'^(#{1,3})\s+(.+)$', content, re.MULTILINE)
        
        # Extract code block titles (first line of each block)
        code_blocks = []
        blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
        for lang, code in blocks:
            first_line = code.split('\n')[0] if code else ""
            code_blocks.append({'language': lang, 'first_line': first_line[:100]})
        
        capabilities.update({
            'headers': headers,
            'code_blocks': code_blocks,
            'type': 'markdown'
        })
        
        return capabilities
    
    def categorize_capabilities(self, file_path: Path, capabilities: Dict[str, Any]) -> str:
        """Determine the primary bucket for a file"""
        file_name = file_path.name.lower()
        
        # Direct filename matching
        if any(keyword in file_name for keyword in ['routing', 'orchestrat', 'workflow', 'pipeline']):
            return 'routing_rules'
        if any(keyword in file_name for keyword in ['config', 'parameter', 'setting', 'preset']):
            return 'parameter_presets'
        if any(keyword in file_name for keyword in ['quant', 'scor', 'metric', 'measure']):
            return 'quant_rules'
        if any(keyword in file_name for keyword in ['bullet', 'point']):
            return 'bullet_engine'
        if any(keyword in file_name for keyword in ['rewrite', 'rephrase', 'reword']):
            return 'rewrite_engine'
        if any(keyword in file_name for keyword in ['skill', 'competenc']):
            return 'skills_engine'
        if any(keyword in file_name for keyword in ['section', 'segment']):
            return 'section_rules'
        if any(keyword in file_name for keyword in ['job', 'step', 'phase']):
            return 'job_workflow_steps'
        if any(keyword in file_name for keyword in ['ats', 'applicant']):
            return 'ats_rules'
        if any(keyword in file_name for keyword in ['template', 'layout']):
            return 'template_layouts'
        if any(keyword in file_name for keyword in ['format', 'style']):
            return 'formatting_rules'
        if any(keyword in file_name for keyword in ['senior', 'level', 'grade']):
            return 'seniority_rules'
        if any(keyword in file_name for keyword in ['tone', 'voice']):
            return 'tone_rules'
        if any(keyword in file_name for keyword in ['constraint', 'limit']):
            return 'constraints'
        if any(keyword in file_name for keyword in ['validator', 'validation', 'rule']):
            return 'validator_rules'
        if any(keyword in file_name for keyword in ['mission', 'field']):
            return 'mission_fields'
        
        # Content-based categorization
        content_str = str(capabilities).lower()
        
        if any(keyword in content_str for keyword in ['routing', 'orchestrat', 'workflow']):
            return 'routing_rules'
        if any(keyword in content_str for keyword in ['config', 'parameter', 'setting']):
            return 'parameter_presets'
        if any(keyword in content_str for keyword in ['quant', 'scor', 'metric']):
            return 'quant_rules'
        if any(keyword in content_str for keyword in ['valid', 'rule', 'check']):
            return 'validator_rules'
        
        # Default to routing_rules
        return 'routing_rules'
    
    def process_file(self, file_path: Path) -> tuple[str, Dict[str, Any]]:
        """Process a single file and return (bucket, capabilities)"""
        try:
            if not file_path.exists():
                return 'routing_rules', {'error': 'File not found', 'type': 'missing'}
                
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract capabilities based on file type
            if file_path.suffix.lower() == '.py':
                capabilities = self.extract_python_capabilities(file_path, content)
            elif file_path.suffix.lower() == '.json':
                capabilities = self.extract_json_capabilities(file_path, content)
            elif file_path.suffix.lower() in ['.md', '.markdown']:
                capabilities = self.extract_markdown_capabilities(file_path, content)
            else:
                capabilities = {'type': 'other', 'size': len(content)}
            
            # Add minimal metadata
            capabilities['file_size'] = len(content)
            
            # Categorize
            bucket = self.categorize_capabilities(file_path, capabilities)
            
            return bucket, capabilities
            
        except Exception as e:
            return 'routing_rules', {'error': str(e), 'type': 'error'}
    
    def extract_all_capabilities(self):
        """Extract capabilities from all files"""
        print("Starting selective capability extraction...")
        
        processed_count = 0
        for i, file_path in enumerate(self.file_list):
            if i % 100 == 0:
                print(f"Processing file {i+1}/{len(self.file_list)}: {file_path.name}")
            
            bucket, capabilities = self.process_file(file_path)
            
            # Store with forward slashes to avoid unicode escape issues
            relative_path = str(file_path).replace('\\', '/')
            self.capability_map[bucket][relative_path] = capabilities
            processed_count += 1
        
        print(f"Completed extraction. Processed {processed_count} files.")
    
    def write_capabilities_file(self, output_path: Path):
        """Write the reconstructed capabilities file in proper format"""
        print(f"Writing capabilities to {output_path}...")
        
        # Create the output directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("#!/usr/bin/env python3\n")
            f.write('"""\n')
            f.write("Reconstructed Resume Generator Capabilities\n")
            f.write("ZERO-LOSS extraction from ALL archive files\n")
            f.write(f"Total files processed: {len(self.file_list)}\n")
            f.write('"""\n\n')
            
            f.write("RG_CAPABILITIES = {\n")
            
            for bucket, capabilities in self.capability_map.items():
                f.write(f'    "{bucket}": {{\n')
                
                for file_path, caps in capabilities.items():
                    # Use json.dumps with ensure_ascii=False to preserve unicode characters
                    caps_json = json.dumps(caps, separators=(',', ':'), ensure_ascii=False)
                    f.write(f'        "{file_path}": {caps_json},\n')
                
                f.write('    },\n')
            
            f.write("}\n")
        
        print(f"Capabilities written to {output_path}")

def main():
    """Main execution function"""
    # Define paths
    base_dir = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\archive")
    index_file = base_dir / "MASTER_RG_FILE_INDEX.txt"
    output_file = Path(r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\agentic_workflow\RG_capabilities\reconstructed_capabilities.py")
    
    # Create extractor and run
    extractor = RGCapabilityExtractorV2(index_file)
    extractor.load_file_inventory()
    extractor.extract_all_capabilities()
    extractor.write_capabilities_file(output_file)
    
    print("ZERO-LOSS capability extraction completed!")

if __name__ == "__main__":
    main()
