# Custom Fonts Directory

This directory is for storing imported custom font files.

## Usage

### Method 1: Import via GUI
1. Launch the program
2. In the "Subtitle Generation" tab, click the "Import Font" button
3. Select a `.ttf` or `.otf` font file
4. The font will be automatically copied to this directory
5. It will auto-load on next program start

### Method 2: Manual Copy
1. Copy `.ttf` or `.otf` font files directly to this directory
2. Restart the program
3. Fonts will appear in the font dropdown list (displayed as "Custom: FontName")

## Supported Font Formats
- `.ttf` (TrueType Font)
- `.otf` (OpenType Font)

## Notes
- Font filenames will be used as display names
- English filenames recommended to avoid special characters
- Font files will be used by FFmpeg during subtitle embedding

## Example
```
fonts/
├── genshin.ttf         → Displays as "Custom: genshin"
├── Arial-Bold.ttf      → Displays as "Custom: Arial-Bold"
└── customfont.otf      → Displays as "Custom: customfont"
```

## Ignore in Git
Font files (`.ttf`, `.otf`) in this directory are ignored by Git to keep the repository size small.
Users can add their own fonts locally.
