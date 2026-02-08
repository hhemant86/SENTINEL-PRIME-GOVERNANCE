import pathlib

def export_project_to_txt(output_filename="project_dump.txt"):
    # Configurations
    exclude_dirs = {".venv", ".git", "__pycache__", ".vscode", "node_modules", ".idea"}
    exclude_ext = {".pyc", ".exe", ".png", ".jpg", ".jpeg", ".gif", ".pdf", ".zip", ".sqlite3", ".log"}
    
    root_dir = pathlib.Path(".")
    output_file = root_dir / output_filename

    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write(f"PROJECT EXPORT: {root_dir.absolute().name}\n")
        f_out.write("=" * 60 + "\n\n")

        # Recursive walk through all files
        for path in sorted(root_dir.rglob('*')):
            # Skip the output file itself and excluded directories
            if path.name == output_filename or any(part in exclude_dirs for part in path.parts):
                continue

            # Process only files with allowed extensions
            if path.is_file() and path.suffix.lower() not in exclude_ext:
                try:
                    content = path.read_text(encoding="utf-8")
                    
                    f_out.write(f"FILE: {path.relative_to(root_dir)}\n")
                    f_out.write("-" * 60 + "\n")
                    f_out.write(content)
                    f_out.write("\n\n" + "=" * 60 + "\n\n")
                    
                    print(f"✔ Added: {path.relative_to(root_dir)}")
                except (UnicodeDecodeError, PermissionError):
                    # Silently skip files that aren't text-based
                    continue

    print(f"\nDone! All code has been exported to: {output_filename}")

if __name__ == "__main__":
    export_project_to_txt()