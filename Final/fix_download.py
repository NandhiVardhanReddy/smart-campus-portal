import os
import re

def fix_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match from downloadDoc start to bookmarkDoc start
    # We want to replace everything in between with the correct downloadDoc implementation
    
    pattern = r'(function\s+downloadDoc\s*\(\s*id\s*\)\s*\{[\s\S]*?)(function\s+bookmarkDoc)'
    
    def replacement(match):
        next_func = match.group(2)
        
        # Determine indentation
        if 'teacher.html' in file_path:
            indent = '        '
            body_indent = '            '
        else:
            indent = '    '
            body_indent = '      '
            
        new_func = f'{indent}function downloadDoc(id) {{\n'
        new_func += f'{body_indent}const d = state.docs.find(x => x.id === id);\n'
        new_func += f'{body_indent}if (!d) return alert(\'Not found\');\n\n'
        new_func += f'{body_indent}// Use backend download route\n'
        new_func += f'{body_indent}window.location.href = `${{API_BASE_URL}}/documents/${{id}}/download`;\n'
        new_func += f'{indent}}}\n'
        new_func += f'{indent}' # Extra newline/indent before next function
        
        return f'{new_func}{next_func}'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Fixed {file_path}")
    else:
        print(f"No changes made to {file_path} (pattern not found)")

if __name__ == "__main__":
    base_dir = r"c:/Users/varsh/Desktop/Final"
    fix_file(os.path.join(base_dir, "teacher.html"))
    fix_file(os.path.join(base_dir, "student.html"))
