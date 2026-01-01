# StegoCryptAudio

Web application to hide and extract audio files inside images using Flask and encryption.

## Features
- Hide any audio file inside a single image.
- Automatically resizes image if audio is too large.
- Encrypts audio using Fernet encryption.
- Simple black/green web interface with Flask.

## Usage
1. Upload an image and audio file.
2. Enter encryption key.
3. Click "Hide Audio" to generate the stego image.
4. To extract, upload the image and enter the same key.

## Technologies
- Python 3
- Flask
- Pillow (PIL)
- Cryptography (Fernet)
