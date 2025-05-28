
# Image Processing Tool with FFmpeg

This Python script provides a command-line tool for processing image files using `ffmpeg`. It supports the following features:

- Adding watermarks
- Creating thumbnails
- Generating animated GIFs
- Exporting metadata

It supports both individual image files and entire directories containing `.jpg`, `.jpeg`, or `.png` images.

---

## 📂 Features

| Feature        | Description |
|----------------|-------------|
| `--watermark`  | Adds a centered watermark (folder or base name) to the image |
| `--thumbnail`  | Creates a 1280x720 thumbnail (with padding to preserve aspect ratio) |
| `--gif`        | Generates an animated GIF of all images in the directory (optionally watermarked) |
| `--metadata`   | Outputs a text file with image metadata including file size, dimensions, format, and tags |

---

## 🛠️ Requirements

- Python 3
- [ffmpeg](https://ffmpeg.org/download.html)
- [ffprobe](https://ffmpeg.org/ffprobe.html) (comes with ffmpeg)

Make sure `ffmpeg` and `ffprobe` are available in your system’s PATH.

## ▶️ Usage

```bash
python image_processing.py <input_path> [options]
```

### ✅ Examples

```bash
# Add watermark to a single image
python image_processing.py VFX_Folder/Bath_VFX_v01.JPG -w

# Add watermark and create thumbnail for one image
python image_processing.py VFX_Folder/Pirate_VFX_v02.JPG -w -t

# Process a directory: watermark, create gif, and export metadata
python image_processing.py VFX_Folder/ -w -g -m
```

### 📥 Arguments

| Argument | Description |
|----------|-------------|
| `input`  | Input file or directory path |
| `-w`, `--watermark` | Apply watermark with folder/base name |
| `-t`, `--thumbnail` | Generate a thumbnail (1280x720) |
| `-g`, `--gif`       | Create animated GIF from input images |
| `-m`, `--metadata`  | Export metadata to `ME_VFX_01.txt` |

---

## 📄 Output Files

Output files are saved in the same directory as the input. Output filenames include:

- `WM_<base>_vXX.jpg` – watermarked image
- `TC_<base>_vXX.jpg` – thumbnail
- `WMTC_<base>_vXX.jpg` – watermarked + thumbnail
- `GC_VFX_01.gif` or `WMGC_VFX_01.gif` – animated GIF
- `ME_VFX_01.txt` – metadata report

Filenames include incrementing version numbers to prevent overwriting.

---

## 📌 Notes

- Filenames ending in `_vNN` (e.g., `_v01`) are auto-cleaned for consistent output names.
- Image extensions supported: `.jpg`, `.jpeg`, `.png`
- Text watermark appears at the center of the image.
- GIF duration per frame is 2 seconds.

---

## 🧪 Debugging

If `ffmpeg` fails, the script will silently skip that file. You can modify `run_ffmpeg()` to print detailed errors if needed.

---

## 📃 License

MIT License – free to use and modify.
