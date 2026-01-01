from flask import Flask, render_template, request, send_file
from stego import hide_text, extract_text
from PIL import Image
import os, shutil, base64, math
from cryptography.fernet import Fernet

app = Flask(__name__)

TEMP_DIR = "temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def derive_key(user_key: str) -> bytes:
    raw = user_key.encode("utf-8")
    raw = raw.ljust(32, b'0')[:32]
    return base64.urlsafe_b64encode(raw)

@app.route("/", methods=["GET", "POST"])
def index():
    message = ""
    download_link = ""

    if request.method == "POST":
        action = request.form.get("action")

        try:
            if action == "hide":
                image_file = request.files["image"]
                audio_file = request.files["audio"]
                outname = request.form["outname"]
                user_key = request.form["key"]
                folder_input = request.form.get("folder")

                if len(user_key) < 8:
                    raise Exception("Encryption key too short!")

                SAVE_PATH = folder_input if folder_input else "./output/"
                os.makedirs(SAVE_PATH, exist_ok=True)

                key = derive_key(user_key)
                fernet = Fernet(key)

                image_path = os.path.join(TEMP_DIR, "img.png")
                audio_path = os.path.join(TEMP_DIR, "audio.bin")
                image_file.save(image_path)
                audio_file.save(audio_path)

                with open(audio_path, "rb") as f:
                    audio_bytes = f.read()

                encrypted_audio = fernet.encrypt(audio_bytes)
                data_bits_len = len(encrypted_audio) * 8

                img = Image.open(image_path)
                orig_width, orig_height = img.size
                capacity = orig_width * orig_height

                if data_bits_len > capacity:
                    new_size = math.ceil(math.sqrt(data_bits_len))
                    img = Image.new("RGB", (new_size, new_size), color=(255, 255, 255))
                    image_path = os.path.join(TEMP_DIR, "resized_img.png")
                    img.save(image_path)
                    img.close()

                if not outname.lower().endswith(".png"):
                    outname += ".png"
                final_out = os.path.join(SAVE_PATH, outname)

                hide_text(image_path, encrypted_audio, final_out)
                message = f"Audio hidden successfully in {outname}"
                download_link = final_out

            elif action == "extract":
                image_file = request.files["image"]
                user_key = request.form["key"]

                key = derive_key(user_key)
                fernet = Fernet(key)

                image_path = os.path.join(TEMP_DIR, "extract.png")
                image_file.save(image_path)

                encrypted = extract_text(image_path)
                decrypted_audio = fernet.decrypt(encrypted)

                audio_out = os.path.join(TEMP_DIR, "extracted_audio.wav")
                with open(audio_out, "wb") as f:
                    f.write(decrypted_audio)

                return send_file(audio_out, as_attachment=True)

        except Exception as e:
            message = f"Error: " + str(e)

    return render_template("index.html", message=message, download_link=download_link)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
