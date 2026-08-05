"""
Configuration parsing utilities for GameCache project.
"""

import os
from pathlib import Path


def parse_config_file(config_path="config.txt"):
    """Parse simple key=value config file"""
    config = {}
    config_file = Path(config_path)

    if not config_file.exists():
        raise FileNotFoundError(f"Config file {config_path} not found")

    with open(config_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue

            # Parse key=value
            if '=' not in line:
                raise ValueError(f"Invalid config line {line_num}: {line}")

            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip()

            # Remove quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            elif value.startswith("'") and value.endswith("'"):
                value = value[1:-1]

            config[key] = value

    return config


def parse_bgg_usernames(raw_value):
    """Split a (possibly comma-separated) bgg_username value into a clean list.

    Supports both the old single-user format (bgg_username = alice) and a new
    multi-user format (bgg_username = alice,bob,carol).
    """
    user_names = [name.strip() for name in raw_value.split(",")]
    user_names = [name for name in user_names if name]

    if not user_names:
        raise ValueError("bgg_username must contain at least one BGG username")

    return user_names


def create_nested_config(config):
    """Convert flat config to nested structure for backward compatibility"""
    user_names = parse_bgg_usernames(config["bgg_username"])

    nested = {
        "project": {
            "title": config["title"]
        },
        "boardgamegeek": {
            # Kept for backward compatibility with any code that still reads
            # a single user_name (e.g. the BGG token setup script).
            "user_name": user_names[0],
            "user_names": user_names,
        },
        "github": {
            "repo": config["github_repo"]
        }
    }
    
    # Check for BGG token in environment variable first
    bgg_token = os.environ.get('GAMECACHE_BGG_TOKEN')

    # If not in environment, try to load from .env file
    # Look for .env in: current dir, parent dir (scripts), or grandparent (repo root)
    if not bgg_token:
        env_locations = [
            Path('.env'),
            Path(__file__).parent.parent.parent / '.env',  # repo root from scripts/gamecache/config.py
        ]
        for env_file in env_locations:
            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('GAMECACHE_BGG_TOKEN='):
                            bgg_token = line.split('=', 1)[1].strip()
                            break
                if bgg_token:
                    break

    # Fall back to config file if still not found
    if bgg_token:
        nested["boardgamegeek"]["token"] = bgg_token
    elif "bgg_token" in config:
        nested["boardgamegeek"]["token"] = config["bgg_token"]
    
    return nested

