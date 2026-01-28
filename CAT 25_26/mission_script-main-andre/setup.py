import sys
import subprocess
import platform
from pathlib import Path


class Color:
    GREEN = "\033[92m"
    CYAN = "\033[96m"
    RED = "\033[91m"
    RESET = "\033[0m"


def run(cmd):
    print(">>", " ".join(cmd))
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    root = Path(__file__).parent.resolve()
    venv_dir = root / "venv"

    run([sys.executable, "-m", "venv", str(venv_dir)])

    if platform.system() == "Windows":
        pip_path = venv_dir / "Scripts" / "pip.exe"
    else:
        pip_path = venv_dir / "bin" / "pip"

    run([str(pip_path), "install", "--upgrade", "pip"])
    run([str(pip_path), "install", "-r", str(root / "requirements.txt")])

    print(f"\n\nVirtual environment created at:")
    print(f"{Color.CYAN}{venv_dir}{Color.RESET}")
    print("\nTo activate it, run the following in terminal:")

    if platform.system() == "Windows":
        print(f"{Color.GREEN}venv\\Scripts\\activate{Color.RESET}\n\n")
    else:
        print(f"{Color.GREEN}source venv/bin/activate{Color.RESET}\n\n")


if __name__ == "__main__":
    main()
