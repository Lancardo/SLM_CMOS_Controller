# Image Display Application

This application displays images on a secondary screen (like an SLM) and can capture images using a camera connected via the gxipy SDK.

## Installation Instructions

1. Before running the executable, make sure you have the gxipy SDK installed on your system.
2. Copy your local gxipy library files to the `libs` folder.
3. Make sure the SLM is set up as an extended display with 1080p resolution and 100% scaling.

## Usage

1. Launch the executable `image_display.exe`
2. Follow the on-screen instructions to select images or a folder of images
3. Adjust camera settings if needed
4. Display images on the secondary screen

## Building from Source

If you need to rebuild the application:

1. Create a virtual environment:
   ```
   py -3 -m venv venv
   ```
2. Activate the virtual environment:
   ```
   .\venv\Scripts\activate
   ```
3. Install requirements:
   ```
   pip install -r requirements.txt
   ```
4. Add your local gxipy library
5. Run PyInstaller:
   ```
   pyinstaller --onefile --windowed --add-data "libs;libs" image_display.py
   ``` 