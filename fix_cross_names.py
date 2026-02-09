#!/usr/bin/env python3
"""
Fix incarnation cross names in hd_constants.py
- Remove leading "The " from all cross names
- Fix "of the Eden" → "of Eden" and similar cases
- Keep "the" in names like "the Sleeping Phoenix", "the Four Ways", etc.
"""

import re

# Crosses that should NOT have "the" before the name
crosses_without_the = [
    "Eden",
    "Plane",  # Should be "of the Plane"? Let me check...
]

# Actually, let's just do a simple pattern fix:
# Remove "The " from the beginning of all cross names
# The "the" within the name will be preserved where it belongs

input_file = "/Users/joe/VibologyOS/System/Cartographer/src/cartographer/hd_constants.py"
output_file = input_file

with open(input_file, 'r') as f:
    content = f.read()

# Pattern 1: Remove "The Right Angle Cross" → "Right Angle Cross"
content = re.sub(r'"The Right Angle Cross', '"Right Angle Cross', content)

# Pattern 2: Remove "The Left Angle Cross" → "Left Angle Cross"
content = re.sub(r'"The Left Angle Cross', '"Left Angle Cross', content)

# Pattern 3: Remove "The Juxtaposition Cross" → "Juxtaposition Cross"
content = re.sub(r'"The Juxtaposition Cross', '"Juxtaposition Cross', content)

# Pattern 4: Fix "of the Eden" → "of Eden" (Eden doesn't have "the")
content = re.sub(r'of the Eden', 'of Eden', content)

with open(output_file, 'w') as f:
    f.write(content)

print("✓ Fixed cross names in hd_constants.py")
print("  - Removed leading 'The' from all crosses")
print("  - Fixed 'of the Eden' → 'of Eden'")
