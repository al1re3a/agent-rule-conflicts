"""Detect conflicts across AI coding-agent instruction files."""

from .analyzer import analyze
from .discovery import discover
from .models import Directive, Finding, ScanResult

__all__ = ["Directive", "Finding", "ScanResult", "analyze", "discover"]
__version__ = "0.1.0"
