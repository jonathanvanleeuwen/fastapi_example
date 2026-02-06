import base64
import json
import sys
from pathlib import Path


def encode_dict(data: dict) -> str:
    """Encode a dict into a Base64 string."""
    json_str = json.dumps(data)
    return base64.b64encode(json_str.encode("utf-8")).decode("utf-8")


def decode_dict(encoded: str) -> dict:
    """Decode a Base64 string back into a dict."""
    json_str = base64.b64decode(encoded.encode("utf-8")).decode("utf-8")
    return json.loads(json_str)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print(
            "  python secrets_b64.py encode   # reads src/fastapi_example/auth/secrets.json and outputs Base64"
        )
        print("  python secrets_b64.py decode <base64-string>")
        sys.exit(1)

    command = sys.argv[1]

    if command == "encode":
        secrets_file = Path("src/fastapi_example/auth/secrets.json")
        if not secrets_file.exists():
            print("Error: secrets.json not found in src/fastapi_example/auth.")
            sys.exit(1)

        with open(secrets_file, encoding="utf-8") as f:
            data = json.load(f)

        encoded = encode_dict(data)
        print(encoded)

    elif command == "decode":
        if len(sys.argv) < 3:
            print("Usage: python secrets_b64.py decode <base64-string>")
            sys.exit(1)

        encoded = sys.argv[2]
        decoded = decode_dict(encoded)
        print(json.dumps(decoded, indent=2))

    else:
        print("Unknown command. Use 'encode' or 'decode'.")
