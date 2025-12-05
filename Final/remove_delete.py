import os
import re

def remove_delete_option(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Remove Delete button from renderLibrary
    # Pattern to match the delete button line
    # <button class="btn" onclick="deleteDoc('${doc.id}')">Delete</button>
    button_pattern = r'\s*<button class="btn" onclick="deleteDoc\(\'\${doc\.id}\'\)">Delete</button>'
    
    new_content = re.sub(button_pattern, '', content)
    
    # 2. Remove deleteDoc function definition
    # Match function deleteDoc(id) { ... }
    # This is a bit complex with regex due to nested braces, but we can try a simpler approach 
    # if we assume standard formatting or use a more robust parser.
    # Given the previous view, it looks like:
    # function deleteDoc(id) {
    #   if (!confirm(...)) return;
    #   ...
    # }
    
    # Let's try to match the specific function signature and body until the closing brace
    # We'll use a non-greedy match for the body, but we need to be careful about nested braces.
    # Since we know the structure from previous views (it's likely near the end or after other doc functions),
    # and we can see it in the file view if we look closely.
    
    # Actually, let's just comment it out or replace it with an empty function to be safe, 
    # or try to match it precisely.
    
    # Let's try to find the function and remove it.
    # We will look for "function deleteDoc(id) {" and then count braces to find the end.
    
    start_marker = "function deleteDoc(id) {"
    start_idx = new_content.find(start_marker)
    
    if start_idx != -1:
        # Find the matching closing brace
        open_braces = 0
        end_idx = -1
        for i in range(start_idx, len(new_content)):
            if new_content[i] == '{':
                open_braces += 1
            elif new_content[i] == '}':
                open_braces -= 1
                if open_braces == 0:
                    end_idx = i + 1
                    break
        
        if end_idx != -1:
            # Remove the function
            new_content = new_content[:start_idx] + new_content[end_idx:]
            print("Removed deleteDoc function")
        else:
            print("Could not find end of deleteDoc function")
    else:
        print("deleteDoc function not found")

    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated {file_path}")
    else:
        print(f"No changes made to {file_path}")

if __name__ == "__main__":
    base_dir = r"c:/Users/varsh/Desktop/Final"
    remove_delete_option(os.path.join(base_dir, "student.html"))
