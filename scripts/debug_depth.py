#!/usr/bin/env python3
"""
Debug directory depth issues.
"""

import os

def max_depth(path: str, current_depth: int = 0) -> int:
    if current_depth > 10:  # Prevent infinite recursion
        return current_depth
    if not os.path.isdir(path):
        return current_depth
    
    max_child_depth = current_depth
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                child_depth = max_depth(item_path, current_depth + 1)
                max_child_depth = max(max_child_depth, child_depth)
    except PermissionError:
        pass
    
    return max_child_depth

def find_deep_directories(path: str, current_depth: int = 0, max_depth_found: list = []):
    if current_depth > 5:  # Show directories deeper than 5 levels
        max_depth_found.append((path, current_depth))
    
    if current_depth > 10:  # Prevent infinite recursion
        return
    
    if not os.path.isdir(path):
        return
    
    try:
        for item in os.listdir(path):
            item_path = os.path.join(path, item)
            if os.path.isdir(item_path) and not item.startswith('.'):
                find_deep_directories(item_path, current_depth + 1, max_depth_found)
    except PermissionError:
        pass

if __name__ == "__main__":
    print("Checking directory depth...")
    max_d = max_depth(".")
    print(f"Maximum depth: {max_d}")
    
    print("\nFinding directories deeper than 5 levels:")
    deep_dirs = []
    find_deep_directories(".", 0, deep_dirs)
    
    for path, depth in deep_dirs:
        print(f"  {path} (depth: {depth})")
    
    print(f"\nTotal deep directories: {len(deep_dirs)}")
