# Image Viewer Application

A PyQt6-based image viewer application that supports single image display, slideshow playback, and camera control.

## Features

* Full-screen single image display
* Slideshow playback (customizable interval time)
* Multi-monitor support
* Camera control (based on gxipy SDK)
* Image resolution checking
* Playback progress display

## Installation Requirements

### Python Version

* Python 3.7 or above

### Dependency Installation

1. Install basic dependencies:

```bash
pip install -r requirements.txt
```

2. Install the local gxipy package (camera SDK):

```bash
# Method 1: Install in development mode
pip install -e ./gxipy

# Method 2: If the above does not work, you can add gxipy to the Python path
# Ensure the gxipy folder is in the project root directory before running the program
```

### System Requirements

* Windows 10/11 (recommended)
* Multi-monitor setup support
* Compatible camera device if using camera features

## Usage Instructions

### Run the Program

```bash
python main.py
```

### Basic Operations

1. **Single Image Display**:

   * Click the "Select Single Image" button
   * Choose the image file to display
   * Select the target monitor
   * Click "Display Single Image"

2. **Slideshow Playback**:

   * Click the "Select Image Folder" button
   * Choose the folder containing the images (images must be numerically named starting from 0)
   * Set the playback interval (in milliseconds)
   * Select the target monitor
   * Click "Start Slideshow"

3. **Camera Control**:

   * Check the "Enable Camera" checkbox
   * Set the exposure time
   * The camera will automatically capture photos during playback

### Important Notes

* **SLM Settings**: Before use, set the SLM as an extended screen with 1080p resolution and 100% scaling
* **Image Naming**: When selecting a folder, images must be numerically named (starting from 0), and they will be played in ascending order
* **Resolution Matching**: The program will check if the image resolution matches the target monitor

### Shortcuts

* **ESC Key**: Exit full-screen display

## Troubleshooting

1. **Camera Connection Failed**:

   * Check if the camera is properly connected
   * Ensure the camera driver is installed
   * Verify that the gxipy SDK is correctly installed

2. **Image Display Issues**:

   * Check if the image file format is supported
   * Ensure the image resolution matches the display

3. **Multi-Monitor Issues**:

   * Ensure monitor settings are correct
   * Check extended display mode settings

## Developer

@RuiboLan

## License

This project is for learning and research purposes only. Feel free to ask!
