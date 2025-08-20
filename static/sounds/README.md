# Message Sound Files

This directory should contain audio files for message notifications.

## Required Files:
- `message.mp3` - MP3 format message notification sound
- `message.wav` - WAV format message notification sound (fallback)

## Recommended Specifications:
- Duration: 1-3 seconds
- Format: MP3 (primary), WAV (fallback)
- Volume: Moderate (not too loud)
- Style: Gentle notification sound

## How to Add:
1. Place your sound files in this directory
2. Name them exactly: `message.mp3` and `message.wav`
3. Ensure they are under 100KB for fast loading

## Alternative:
If you don't have sound files, you can remove the audio elements from `messages.html` to eliminate 404 errors.
