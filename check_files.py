import pathlib

def list_files(directory, indent="", exclude_dirs=None):
    if exclude_dirs is None:
        exclude_dirs = {"venv", ".venv", "env", ".env",
    "__pycache__", ".git", ".idea", ".pytest_cache",
    "site-packages", "dist-info"}

    path = pathlib.Path(directory)
    
    # Get all items in the directory and sort them (folders first, then files)
    items = sorted(path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))

    for i, item in enumerate(items):
        if item.name in exclude_dirs:
            continue

        # Check if this is the last item in the current directory for formatting
        is_last = i == len(items) - 1
        connector = "└── " if is_last else "├── "
        
        print(f"{indent}{connector}{item.name}")

        # If it's a directory, recurse into it
        if item.is_dir():
            new_indent = indent + ("    " if is_last else "│   ")
            list_files(item, new_indent, exclude_dirs)

if __name__ == "__main__":
    # Use '.' for the current directory or provide a specific path
    root_dir = "." 
    print(f"Project Structure: {pathlib.Path(root_dir).absolute().name}")
    list_files(root_dir)