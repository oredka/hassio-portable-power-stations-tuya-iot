#!/usr/bin/env python3
"""
GitLab Release Creator Script
Створює GitLab release на основі останнього git tag та CHANGELOG.md
"""

import os
import re
import subprocess
import sys
from pathlib import Path

import requests


def get_latest_tag():
    """Отримує останній git tag"""
    try:
        result = subprocess.run(
            ["git", "tag", "--sort=-v:refname"],
            capture_output=True,
            text=True,
            check=True
        )
        tags = result.stdout.strip().split("\n")
        return tags[0] if tags and tags[0] else None
    except subprocess.CalledProcessError as e:
        print(f"Error getting git tags: {e}")
        return None


def get_changelog_for_version(version):
    """Витягує changelog для конкретної версії з CHANGELOG.md"""
    changelog_path = Path("CHANGELOG.md")
    if not changelog_path.exists():
        print("CHANGELOG.md not found")
        return None

    content = changelog_path.read_text(encoding="utf-8")

    # Видаляємо 'v' з початку версії якщо є
    version_clean = version.lstrip('v')

    # Шукаємо секцію для цієї версії
    pattern = rf"## \[{re.escape(version_clean)}\].*?\n(.*?)(?=\n## \[|$)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()
    return None


def create_gitlab_release(project_id, tag_name, description, gitlab_token, gitlab_url="https://gitlab.com"):
    """Створює release в GitLab"""
    api_url = f"{gitlab_url}/api/v4/projects/{project_id}/releases"

    headers = {
        "PRIVATE-TOKEN": gitlab_token,
        "Content-Type": "application/json"
    }

    data = {
        "tag_name": tag_name,
        "name": tag_name,
        "description": description
    }

    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 201:
        print(f"✓ Release {tag_name} created successfully!")
        return True
    elif response.status_code == 409:
        print(f"! Release {tag_name} already exists")
        return False
    else:
        print(f"✗ Error creating release: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    # Отримуємо параметри з environment variables
    gitlab_token = os.getenv("GITLAB_TOKEN")
    project_id = os.getenv("CI_PROJECT_ID")
    gitlab_url = os.getenv("CI_SERVER_URL", "https://gitlab.com")

    # Для локального запуску можна передати аргументи
    if not gitlab_token:
        if len(sys.argv) > 1:
            gitlab_token = sys.argv[1]
        else:
            print("Error: GITLAB_TOKEN not set")
            print("Usage: python create_gitlab_release.py <GITLAB_TOKEN> [PROJECT_ID]")
            sys.exit(1)

    if not project_id:
        if len(sys.argv) > 2:
            project_id = sys.argv[2]
        else:
            print("Error: CI_PROJECT_ID not set")
            print("Usage: python create_gitlab_release.py <GITLAB_TOKEN> [PROJECT_ID]")
            sys.exit(1)

    # Отримуємо останній tag
    tag = get_latest_tag()
    if not tag:
        print("No git tags found")
        sys.exit(1)

    print(f"Latest tag: {tag}")

    # Отримуємо changelog для цієї версії
    changelog = get_changelog_for_version(tag)
    if not changelog:
        print(f"No changelog found for version {tag}")
        changelog = f"Release {tag}"

    print(f"\nChangelog:\n{changelog}\n")

    # Створюємо release
    success = create_gitlab_release(
        project_id=project_id,
        tag_name=tag,
        description=changelog,
        gitlab_token=gitlab_token,
        gitlab_url=gitlab_url
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
