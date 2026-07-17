"""pytest configuration for SkillBridge backend tests.

Adds build/backend/ to sys.path so `from src.xxx import yyy` works without
installing the package.
"""
import sys
from pathlib import Path

# Ensure src/ is importable from any pytest invocation location
sys.path.insert(0, str(Path(__file__).parent))
