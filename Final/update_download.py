import os
import re

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Regex to match the downloadDoc function body
    # We look for function downloadDoc(id) { ... }
    # and replace the body.
    
    pattern = r'(function\s+downloadDoc\s*\(\s*id\s*\)\s*\{)([\s\S]*?)(\n\s*\})'
    
    def replacement(match):
        header = match.group(1)
        footer = match.group(3)
        
        # Determine indentation from the header
        indent = header.replace(header.lstrip(), '')
        # Add extra indentation for the body
        body_indent = indent + '    '
        if 'teacher.html' in file_path:
             body_indent = indent + '    '
        elif 'student.html' in file_path:
             body_indent = indent + '  '
             
        new_body = f'\n{body_indent}const d = state.docs.find(x => x.id === id);'
        new_body += f'\n{body_indent}if (!d) return alert(\'Not found\');'
        new_body += f'\n'
        new_body += f'\n{body_indent}// Use backend download route'
        new_body += f'\n{body_indent}window.location.href = `${{API_BASE_URL}}/documents/${{id}}/download`;'
        
        return f'{header}{new_body}{footer}'
    
    new_content = re.sub(pattern, replacement, content)
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes made to {file_path} (pattern not found)")

if __name__ == "__main__":
    base_dir = r"c:/Users/varsh/Desktop/Final"
    update_file(os.path.join(base_dir, "teacher.html"))
    update_file(os.path.join(base_dir, "student.html"))
