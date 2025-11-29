import os

def find_empty_directories():
    empty_dirs = []
    for root, dirs, files in os.walk('.'):
        # Skip hidden and cache directories
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        if not dirs and not files:
            empty_dirs.append(root)
    return empty_dirs

if __name__ == "__main__":
    empty_dirs = find_empty_directories()
    print(f"Found {len(empty_dirs)} empty directories:")
    for d in empty_dirs:
        print(f"  {d}")
    
    # Fix by adding .gitkeep files
    for d in empty_dirs:
        gitkeep_path = os.path.join(d, '.gitkeep')
        with open(gitkeep_path, 'w') as f:
            f.write('# Keep this directory\n')
        print(f"Added .gitkeep to: {d}")
