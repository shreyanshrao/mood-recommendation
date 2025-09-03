# Music @ Mood - AI Sketch to Music Generator

g

## Features
- HTML5 Canvas drawing interface
- TensorFlow CNN for mood classification (happy, calm, sad, energetic)
- Music recommendation based on predicted mood
- SQLite database for history tracking
- User feedback system for model improvement
- CSV export functionality

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Train the CNN model (optional - app works with fallback method):
   ```bash
   python train_model.py
   ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. Open http://localhost:5000 in your browser

## Usage

1. Draw a sketch on the canvas representing your mood
2. Click "Analyze My Mood" to get AI prediction
3. Listen to recommended music tracks
4. Rate the accuracy to help improve the model
5. View your mood history and export data

## Project Structure

```
music@mood/
├── app.py                 # Main Flask application
├── train_model.py         # CNN model training
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main web interface
├── static/
│   ├── js/app.js         # Frontend JavaScript
│   ├── audio/            # Music files (add your own)
│   └── images/           # Generated images
├── models/               # Trained models
└── data/                 # Training data
```

## Technical Details

- **Backend**: Flask with TensorFlow/Keras
- **Frontend**: HTML5 Canvas + Tailwind CSS + Vanilla JS
- **Database**: SQLite for mood history
- **Audio**: Howler.js for music playback
- **Model**: CNN with data augmentation

## Adding Music Files

Replace placeholder files in `static/audio/` with actual royalty-free MP3 files:
- happy_song1.mp3, happy_song2.mp3, happy_song3.mp3
- calm_song1.mp3, calm_song2.mp3, calm_song3.mp3
- sad_song1.mp3, sad_song2.mp3, sad_song3.mp3
- energy_song1.mp3, energy_song2.mp3, energy_song3.mp3

## License

For educational purposes. Ensure you have proper licenses for any music files used.
