import os
from pathlib import Path

def port_sovereign_system(output_file="full_project_snapshot.txt"):
    # Configurations
    exclude_dirs = {".venv", "venv", ".git", "__pycache__", ".vscode", "legacy_scripts"}
    include_ext = {".py", ".toml", ".json", ".md", ".env"} # We need logic and config
    
    root_dir = Path(".")
    project_name = root_dir.absolute().name

    with open(output_file, "w", encoding="utf-8") as f_out:
        f_out.write(f"PROPRIETARY SNAPSHOT: {project_name}\n")
        f_out.write("=" * 60 + "\n\n")

        # 1. Generate Tree Structure for Context
        f_out.write("--- SYSTEM ARCHITECTURE TREE ---\n")
        for path in sorted(root_dir.rglob('*')):
            if any(part in exclude_dirs for part in path.parts):
                continue
            depth = len(path.relative_to(root_dir).parts)
            spacer = "    " * (depth - 1)
            if path.is_dir():
                f_out.write(f"{spacer}📁 {path.name}/\n")
            else:
                f_out.write(f"{spacer}📄 {path.name}\n")
        
        f_out.write("\n" + "=" * 60 + "\n\n")

        # 2. Extract All Logic
        f_out.write("--- CORE LOGIC & CONFIGURATIONS ---\n\n")
        for path in sorted(root_dir.rglob('*')):
            if any(part in exclude_dirs for part in path.parts):
                continue
                
            if path.is_file() and path.suffix.lower() in include_ext:
                if path.name == output_file or path.name == "port_project.py":
                    continue
                    
                try:
                    content = path.read_text(encoding="utf-8")
                    f_out.write(f"FILE: {path.relative_to(root_dir)}\n")
                    f_out.write("-" * 40 + "\n")
                    f_out.write(content)
                    f_out.write("\n" + "=" * 40 + "\n\n")
                    print(f"✔ Exported: {path}")
                except Exception as e:
                    print(f"✘ Skipped {path.name}: {e}")

    print(f"\n🚀 PORT COMPLETE! File generated: {output_file}")

if __name__ == "__main__":
    port_sovereign_system()