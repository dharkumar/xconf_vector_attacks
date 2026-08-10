#!/usr/bin/env python3
"""
Quick test to verify which API key is being loaded
"""

import os
from pathlib import Path
from dotenv import load_dotenv

print("=" * 70)
print("🔍 ENVIRONMENT VARIABLE TEST")
print("=" * 70)

# Check system environment BEFORE loading .env
system_key = os.getenv("ANTHROPIC_API_KEY")
print(f"\n1️⃣ System environment variable:")
if system_key:
    print(f"   ⚠️  FOUND: ...{system_key[-10:]}")
    print(f"   Length: {len(system_key)} characters")
else:
    print(f"   ✅ Not set (good!)")

# Now load from .env with override
env_path = Path(__file__).parent / ".env"
print(f"\n2️⃣ Loading from .env file:")
print(f"   Path: {env_path}")
print(f"   Exists: {env_path.exists()}")

if env_path.exists():
    with open(env_path, 'r') as f:
        content = f.read()
        if 'ANTHROPIC_API_KEY' in content:
            # Extract just the key part
            for line in content.split('\n'):
                if line.strip().startswith('ANTHROPIC_API_KEY'):
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key_from_file = parts[1].strip().strip('"').strip("'")
                        print(f"   File contains: ...{key_from_file[-10:]}")
                        print(f"   Length: {len(key_from_file)} characters")

load_dotenv(dotenv_path=env_path, override=True)

# Check what's loaded NOW
final_key = os.getenv("ANTHROPIC_API_KEY")
print(f"\n3️⃣ After load_dotenv(override=True):")
if final_key:
    print(f"   Loaded: ...{final_key[-10:]}")
    print(f"   Length: {len(final_key)} characters")
    
    if system_key and final_key == system_key:
        print(f"\n   ❌ PROBLEM: Still using system variable!")
        print(f"   The override didn't work.")
    elif system_key and final_key != system_key:
        print(f"\n   ✅ SUCCESS: Override worked! Using .env file.")
    else:
        print(f"\n   ✅ Using .env file (no system variable to override)")
else:
    print(f"   ❌ ERROR: No key loaded!")

print("\n" + "=" * 70)
print("SOLUTION:")
print("=" * 70)
if system_key:
    print("\nYou have ANTHROPIC_API_KEY set in your shell environment.")
    print("Check these files and REMOVE the ANTHROPIC_API_KEY line:")
    print("  ~/.zshrc")
    print("  ~/.bash_profile")  
    print("  ~/.profile")
    print("\nThen restart your terminal or run: source ~/.zshrc")
else:
    print("\n✅ No system environment variable found.")
    print("The .env file should work correctly now!")
print("=" * 70 + "\n")
