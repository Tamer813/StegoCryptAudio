from PIL import Image

END_MARKER = b"<<END>>"

def hide_text(image_path, data_bytes, output_path):
    img = Image.open(image_path).convert("RGB")
    pixels = img.load()

    data = data_bytes + END_MARKER
    binary = ''.join(format(byte, '08b') for byte in data)

    capacity = img.width * img.height
    if len(binary) > capacity:
        raise Exception("Data too large for this image.")

    idx = 0
    for y in range(img.height):
        for x in range(img.width):
            if idx >= len(binary):
                img.save(output_path)
                return
            r, g, b = pixels[x, y]
            r = (r & ~1) | int(binary[idx])
            pixels[x, y] = (r, g, b)
            idx += 1

    img.save(output_path)


def extract_text(image_path):
    img = Image.open(image_path)
    pixels = img.load()

    bits = ""
    for y in range(img.height):
        for x in range(img.width):
            r, g, b = pixels[x, y]
            bits += str(r & 1)

    data = bytearray()
    for i in range(0, len(bits), 8):
        byte = bits[i:i+8]
        if len(byte) < 8:
            break
        data.append(int(byte, 2))
        if data[-len(END_MARKER):] == END_MARKER:
            return bytes(data[:-len(END_MARKER)])

    return b""
