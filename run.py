#!/usr/bin/env python3
"""CLI execution shim for ProseLint."""

import sys
from prose_lint.cli import main

if __name__ == "__main__":
    sys.exit(main())
