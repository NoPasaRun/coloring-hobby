# Bogdasha's Coloring App

## Description

This is an interactive image coloring application developed in Python using the Pygame library. The app allows users to select levels (images), color them using a palette of colors extracted from the image itself, and enjoy music with heart animation synced to the beats.

## Features

- **Level Menu**: Select saved images for coloring.
- **Interactive Coloring**: Color pixels using a dynamically generated color palette from the image.
- **Settings**: Customize color depth and number of particles (pixels).
- **Music and Animation**: Background music with beat detection and heart pulsing animation.
- **Undo Actions**: Ability to undo the last coloring actions.
- **Zoom and Pan**: Scale and move the image for detailed work.
- **Auto Mode**: Toggle between colored view and original grayscale view.
- **Unique Coloring System**: Particles are created based on image colors, quantized for limited palette, making coloring fun and challenging.

## Installation

### Requirements

- Python 3.8+
- pip

### Dependencies

Install dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

Dependencies include:
- numpy
- PyAudio
- scipy
- soundfile
- pygame
- wave
- librosa

### Running

Run the application:

```bash
python application/main.py
```

## Usage

### Controls

- **Menu**:
  - Select a level by clicking "Play" on an image.
  - Go to settings by clicking "Settings".

- **Level**:
  - Select a color from the palette on the left.
  - Click on squares to color them.
  - Right-click and drag to pan.
  - Scroll wheel to zoom in/out.
  - "Undo" - undo the last action.
  - "Auto" - toggle between colored and original view.

- **Settings**:
  - Change color depth and particle count.
  - Click "Save" to apply.

### Adding Levels

Place an `image.png` in a new folder inside `application/saves/` (e.g., `save6/image.png`).

### Generating Music Beats

To generate `beats.json` from an MP3 file, use the script:

```bash
python application/generate_beats.py path/to/song.mp3 threshold
```

Where `threshold` is the beat intensity threshold (e.g., 0.5).

## Project Structure

```
coloring-hobby/
├── requirements.txt
├── application/
│   ├── __init__.py
│   ├── main.py          # Main application file
│   ├── animation.py     # Animation classes
│   ├── base.py          # Base object classes
│   ├── generate_beats.py # Beat generation script
│   ├── ui.py            # UI components
│   ├── __pycache__/
│   ├── saves/           # Saved levels
│   │   ├── save1/
│   │   │   └── image.png
│   │   └── ...
│   └── src/             # Assets
│       ├── beats.json
│       ├── dead.jpg
│       ├── heart.png
│       ├── icon.png
│       ├── line.png
│       ├── play_button.png
│       ├── point.png
│       ├── rubber.png
│       ├── song.mp3
│       ├── square.png
│       └── start_back.png
└── utils/
    ├── __init__.py
    ├── builders.py      # Particle and color builders
    ├── consts.py        # Constants
    └── enums.py         # Enums
```

## Development

### Architecture

- **App**: Main application class managing states and loop.
- **UI Components**: Button, Grid, Level, Heart, etc.
- **Animation**: Frame, Transition for transitions and animations.
- **Builders**: ParticleBuilder for creating colorable squares.

### Adding Features

- Add new states to the `States` enum.
- Implement event handlers in `App`.
- Use `ParticleBuilder` for new particle types.

## License

This project is licensed under the MIT License. See LICENSE file for details.
