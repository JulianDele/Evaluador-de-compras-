#!/usr/bin/env python3
"""Remove all emojis from project files"""
import os
import re
import sys

files_to_clean = [
    'PROYECTO_PORTABLE.md',
    'INDEX.md',
    'AGREGAR_USUARIOS.md',
    'SETUP.md',
    'docker-compose.yml',
    '.env.example',
    'backend/.env.example',
    'README.md',
    'start-dev.sh',
    'check-requirements.py'
]

# Comprehensive emoji pattern
emoji_pattern = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map
    "\U0001F700-\U0001F77F"  # alchemical
    "\U0001F780-\U0001F7FF"  # Geometric
    "\U0001F800-\U0001F8FF"  # Supplemental
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols
    "\u2300-\u23FF"  # Miscellaneous Technical
    "\u2600-\u27BF"  # Miscellaneous Symbols
    "\u2B50"  # star
    "\u2705\u274c\u26a0"  # check, x, warning
    "\ufe0f"  # variation selector
    "]+",
    flags=re.UNICODE
)

def clean_file(filepath):
    """Remove emojis from a file"""
    if not os.path.exists(filepath):
        return f"SKIP: {filepath} (not found)"
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()
        
        cleaned = emoji_pattern.sub('', text)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned)
        
        return f"OK: {filepath}"
    except Exception as e:
        return f"ERROR: {filepath} - {str(e)}"

if __name__ == '__main__':
    print("Removing emojis from project files...")
    for filepath in files_to_clean:
        result = clean_file(filepath)
        print(result)
    print("\nDone!")
