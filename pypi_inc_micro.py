import re
from pathlib import Path


def increment_micro_version(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    version_pattern = r'version\s*=\s*"(\d+)\.(\d+)\.(\d+)"'
    match = re.search(version_pattern, content)

    if match:
        major, minor, patch = map(int, match.groups())
        new_version = f'{major}.{minor}.{patch + 1}'
        updated_content = re.sub(version_pattern, f'version = "{new_version}"', content)

        with open(file_path, 'w') as file:
            file.write(updated_content)

        print(f"Version updated to {new_version}")
    else:
        print("Version not found in the file")

def main():
    pyproject_toml = Path(__file__).parent / 'pyproject.toml'
    increment_micro_version(pyproject_toml)


if __name__ == '__main__':
    main()
