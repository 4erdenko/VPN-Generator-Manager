#!/usr/bin/env python3
"""
Configuration validation utility for VPN Bot Manager.
Run this script to check if your environment is properly configured.
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and contains required variables."""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found")
        print("   Create .env file using .env.example as template")
        return False
    
    print("✅ .env file found")
    
    # Check required variables
    required_vars = ['BOT_API', 'CHAT_ID']
    missing_vars = []
    
    with open(env_path) as f:
        content = f.read()
        for var in required_vars:
            if f"{var}=" not in content or f"{var}=your_" in content:
                missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing or placeholder values for: {', '.join(missing_vars)}")
        return False
    
    print("✅ Required environment variables are set")
    return True

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 9):
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} is too old")
        print("   Python 3.9+ is required")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} is compatible")
    return True

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import aiogram
        import httpx
        import aiofiles
        import coloredlogs
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e.name}")
        print("   Run: pip install -r requirements.txt")
        return False

def main():
    """Run all configuration checks."""
    print("🔍 Validating VPN Bot Manager configuration...\n")
    
    checks = [
        check_python_version,
        check_dependencies,
        check_env_file,
    ]
    
    results = [check() for check in checks]
    
    print("\n" + "="*50)
    if all(results):
        print("🎉 Configuration is valid! You can start the bot.")
        return 0
    else:
        print("❌ Configuration has issues. Please fix them before starting the bot.")
        return 1

if __name__ == "__main__":
    sys.exit(main())