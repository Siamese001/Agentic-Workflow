#!/usr/bin/env python3
"""
Resume Generator File Enumeration Script
Enumerates ALL files in specified archive folders with zero loss.
Creates MASTER_RG_FILE_INDEX.txt and MASTER_RG_FILE_HASH.txt
"""

import hashlib
from pathlib import Path

def count_lines(file_path):
    """Count lines in text files, return 0 for binary files."""
    text_extensions = {'.py', '.txt', '.md', '.json', '.yaml', '.yml', '.xml', 
                      '.csv', '.html', '.css', '.js', '.ts', '.log', '.diff', 
                      '.patch', '.sql', '.ipynb'}
    
    ext = Path(file_path).suffix.lower()
    if ext not in text_extensions:
        return 0
    
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0

def get_sha256_hash(file_path):
    """Calculate SHA256 hash of file."""
    try:
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    except Exception:
        return "HASH_ERROR"

def enumerate_files():
    """Main enumeration function."""
    base_dir = r"C:\Users\amita\Documents\Work\AI Job Search\AI\ML\DL\GenAI\LLM 101\LLM Pipelines\Resume Gen\Git\Agentic_Workflow-10_11\archive\resume_gen"
    
    target_folders = [
        'Monolith',
        'Microservices Model', 
        'Agentic AI - not communicating',
        'v2', 'v3.8', 'v5.2', 'v5.3', 'v5.4', 'v5.5', 'v5.6', 'v5.8', 'v5.9',
        'v6.0', 'v6.1', 'v6.2', 'v6.3', 'v6.4', 'v6.5', 'v7.0', 'v7.5', 'v8.0', 'v8.5',
        'v9.0', 'v9.5', 'v9.6', 'v9.7', 'v9.8', 'v9.9', 'v10.2', 'v10.4', 'v10.5', 'v10.6', 'v10.7',
        'v10_0', 'v10_1'
    ]
    
    index_file = Path(base_dir).parent / 'MASTER_RG_FILE_INDEX.txt'
    hash_file = Path(base_dir).parent / 'MASTER_RG_FILE_HASH.txt'
    
    print("Starting file enumeration...")
    print(f"Index file: {index_file}")
    print(f"Hash file: {hash_file}")
    
    all_files = []
    
    # Process target folders
    for folder in target_folders:
        folder_path = Path(base_dir) / folder
        if folder_path.exists():
            print(f"Processing folder: {folder}")
            for file_path in folder_path.rglob('*'):
                if file_path.is_file():
                    all_files.append((file_path, folder))
        else:
            print(f"Folder not found: {folder_path}")
    
    # Process files directly under archive/resume_gen
    print("Processing files directly under archive/resume_gen/")
    base_path = Path(base_dir)
    for file_path in base_path.iterdir():
        if file_path.is_file():
            all_files.append((file_path, "OTHER"))
    
    print(f"Found {len(all_files)} files total")
    
    # Write index file with sections
    with open(index_file, 'w', encoding='utf-8') as idx:
        # Write section headers and files
        current_section = None
        
        for file_path, section in all_files:
            # Determine section
            if section == 'Monolith':
                section_name = 'MONOLITH'
            elif section == 'Microservices Model':
                section_name = 'MICROSERVICES MODEL'
            elif section == 'Agentic AI - not communicating':
                section_name = 'AGENTIC AI - NOT COMMUNICATING'
            elif section.startswith('v') or section.startswith('V'):
                section_name = 'VERSIONED FOLDERS'
            elif section == 'OTHER':
                section_name = 'OTHER'
            else:
                section_name = 'VERSIONED FOLDERS'
            
            # Write section header if changed
            if current_section != section_name:
                current_section = section_name
                idx.write(f"=== {section_name} ===\n")
            
            # Get file info
            try:
                size_bytes = file_path.stat().st_size
                line_count = count_lines(file_path)
                last_modified = int(file_path.stat().st_mtime * 100000000)  # Convert to Windows FILETIME format
                
                idx.write(f"{file_path.absolute()} | {size_bytes} | {line_count} | {last_modified}\n")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                idx.write(f"{file_path.absolute()} | ERROR | ERROR | ERROR\n")
    
    # Write hash file
    with open(hash_file, 'w', encoding='utf-8') as hf:
        for file_path, _ in all_files:
            try:
                file_hash = get_sha256_hash(file_path)
                hf.write(f"{file_path.absolute()} | {file_hash}\n")
            except Exception as e:
                print(f"Error hashing {file_path}: {e}")
                hf.write(f"{file_path.absolute()} | HASH_ERROR\n")
    
    print("File enumeration completed!")
    print(f"Total files processed: {len(all_files)}")
    print(f"Index file created: {index_file}")
    print(f"Hash file created: {hash_file}")

if __name__ == "__main__":
    enumerate_files()
