from __future__ import annotations

import sys

from construction_intelligence_mcp.runtime.certify_program100 import (
    main as certify_program100_main,
)
from construction_intelligence_mcp.runtime.health import main as health_main
from construction_intelligence_mcp.runtime.validate import main as validate_main

if __name__ == "__main__":
    arguments = sys.argv[1:]
    if arguments[:1] == ["validate"]:
        sys.exit(validate_main(arguments))
    if arguments[:1] == ["certify-program100"]:
        sys.exit(certify_program100_main(arguments))
    if arguments[:1] == ["health"]:
        sys.exit(health_main(arguments))
    sys.exit(validate_main(arguments))
