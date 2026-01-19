#!/usr/bin/env python3
"""
GitHub Release Creator Script
Створює GitHub release на основі останнього git tag та CHANGELOG.md
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


def create_github_release(repo, tag_name, description, github_token):
    """Створює release в GitHub"""
    api_url = f"https://api.github.com/repos/{repo}/releases"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "tag_name": tag_name,
        "name": tag_name,
        "body": description,
        "draft": False,
        "prerelease": False
    }

    response = requests.post(api_url, json=data, headers=headers)

    if response.status_code == 201:
        print(f"✓ Release {tag_name} created successfully!")
        print(f"URL: {response.json()['html_url']}")
        return True
    elif response.status_code == 422:
        print(f"! Release {tag_name} already exists")
        return False
    else:
        print(f"✗ Error creating release: {response.status_code}")
        print(f"Response: {response.text}")
        return False


def main():
    # Отримуємо параметри
    github_token = os.getenv("GITHUB_TOKEN")
    repo = os.getenv("GITHUB_REPOSITORY")  # формат: owner/repo

    # Для локального запуску
    if not github_token:
        if len(sys.argv) > 1:
            github_token = sys.argv[1]
        else:
            print("Error: GITHUB_TOKEN not set")
            print("Usage: python create_github_release.py <GITHUB_TOKEN> [REPO]")
            print("Example: python create_github_release.py ghp_xxx oredka/2e-power-stations")
            sys.exit(1)

    if not repo:
        if len(sys.argv) > 2:
            repo = sys.argv[2]
        else:
            print("Error: GITHUB_REPOSITORY not set")
            print("Usage: python create_github_release.py <GITHUB_TOKEN> [REPO]")
            print("Example: python create_github_release.py ghp_xxx oredka/2e-power-stations")
            sys.exit(1)

    # Отримуємо останній tag
    tag = get_latest_tag()
    if not tag:
        print("No git tags found")
        sys.exit(1)

    print(f"Latest tag: {tag}")
    print(f"Repository: {repo}")

    # Отримуємо changelog для цієї версії
    changelog = get_changelog_for_version(tag)
    if not changelog:
        print(f"No changelog found for version {tag}")
        changelog = f"Release {tag}"

    print(f"\nChangelog:\n{changelog}\n")

    # Створюємо release
    success = create_github_release(
        repo=repo,
        tag_name=tag,
        description=changelog,
        github_token=github_token
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
