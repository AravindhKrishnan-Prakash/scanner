import json
import sys
from pathlib import Path

from trading_system import decide_trade


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python main.py <input.json>")
        return 1

    input_path = Path(sys.argv[1])
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    result = decide_trade(payload)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
