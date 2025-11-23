import base64, zlib, sys

if len(sys.argv) < 3:
    exit()

input_file = sys.argv[1]
output_file = sys.argv[2]
with open(input_file, "rb") as input_file:
    payload = input_file.read()

def deobfuscate_layer(data: bytes, level: int):
    print(f"[Layer {level}] reversing...")
    rev = data[::-1]

    print(f"[Layer {level}] base64 decoding...")
    try:
        decoded = base64.b64decode(rev)
    except Exception as e:
        print(f"[Layer {level}] base64 error:", e)
        return None

    print(f"[Layer {level}] zlib decompressing...")
    try:
        raw = zlib.decompress(decoded)
    except Exception as e:
        print(f"[Layer {level}] zlib error:", e)
        return None

    print(f"[Layer {level}] OK")
    return raw


marker = b"exec((_)(b'"

if marker in payload:
    payload = payload.split(marker, 1)[1]
    if payload.endswith(b"'))"):
        payload = payload[:-3]
else:
    raise ValueError("First layer not found")

level = 1
decoded = deobfuscate_layer(payload, level)
if decoded is None:
    raise SystemExit("Error decoding first layer")

payload = decoded
level += 1

while payload.startswith(b"exec((_)(b'"):
    print(f"\n--- Entering layer {level} ---")
    inner = payload[len(b"exec((_)(b'"):-len(b"'))")]
    decoded = deobfuscate_layer(inner, level)
    if decoded is None:
        print(f"[Layer {level}] stopped")
        break
    payload = decoded
    level += 1

with open(output_file, "wb") as deobfuscated:
    deobfuscated.write(payload)

print(f"\nFinished at layer {level - 1}")
print("Output written.")
