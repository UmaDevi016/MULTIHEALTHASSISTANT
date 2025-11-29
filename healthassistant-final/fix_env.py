import os

def fix_env_file():
    env_path = '.env'
    if not os.path.exists(env_path):
        print("Error: .env file not found")
        return

    with open(env_path, 'r') as f:
        content = f.read()
    
    print("Original content length:", len(content))
    print("First 50 chars:", repr(content[:50]))
    
    # Always clean up the file
    print("Cleaning up .env file...")
    
    # Remove any leading spaces before variable names
    lines = content.split('\n')
    clean_lines = []
    for line in lines:
        if '=' in line:
            key, val = line.split('=', 1)
            clean_lines.append(f"{key.strip()}={val.strip()}")
        else:
            clean_lines.append(line.strip())
    
    fixed_content = '\n'.join([l for l in clean_lines if l])
    
    print("Fixed content length:", len(fixed_content))
    
    with open(env_path, 'w') as f:
        f.write(fixed_content)
        
    print("Successfully fixed .env file")
    
    # Verify
    with open(env_path, 'r') as f:
        new_content = f.read()
        print("New content preview:")
        for line in new_content.split('\n'):
            # Mask keys for security in output
            if "=" in line:
                key, val = line.split('=', 1)
                print(f"{key}={val[:5]}...")

if __name__ == "__main__":
    fix_env_file()
