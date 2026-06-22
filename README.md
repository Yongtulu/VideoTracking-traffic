# Traffic Tracker — Vehicle Tracking + Line Crossing Counter

Real-time vehicle detection and tracking system based on YOLOv8 + ByteTrack, with virtual counting line support for IN/OUT direction statistics.

## Demo

![Demo](demo.png)

*YOLOv8 detection + ByteTrack tracking. The red line is the virtual counting line; IN/OUT counts are displayed in the top-left corner in real time.*

## Features

- Multi-class vehicle detection (car / bus / truck / motorcycle)
- ByteTrack cross-frame ID tracking — maintains the same ID through occlusions
- Virtual counting line with crossing detection and IN/OUT direction judgment
- Real-time visualization: bounding boxes, track IDs, crossing highlights, count panel
- Supports video files and webcam input; optional output video saving

## Architecture

```
Video Frame → YOLOv8 Detection → ByteTrack Tracking → LineCounter → Visualization
```

<svg viewBox="0 0 780 420" xmlns="http://www.w3.org/2000/svg" font-family="ui-monospace,monospace" font-size="13">
  <defs>
    <marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto">
      <path d="M0,0 L0,6 L8,3 z" fill="#888"/>
    </marker>
  </defs>

  <rect x="20" y="30" width="130" height="54" rx="8" fill="#1e1e2e" stroke="#444" stroke-width="1.5"/>
  <text x="85" y="52" text-anchor="middle" fill="#cdd6f4" font-weight="600">Video Source</text>
  <text x="85" y="72" text-anchor="middle" fill="#888" font-size="11">mp4 / webcam / DETRAC</text>

  <line x1="150" y1="57" x2="188" y2="57" stroke="#888" stroke-width="1.5" marker-end="url(#arr)"/>

  <rect x="190" y="30" width="140" height="54" rx="8" fill="#1e1e2e" stroke="#89b4fa" stroke-width="1.5"/>
  <text x="260" y="52" text-anchor="middle" fill="#89b4fa" font-weight="600">YOLOv8</text>
  <text x="260" y="72" text-anchor="middle" fill="#888" font-size="11">classes: car/bus/truck/moto</text>

  <line x1="330" y1="57" x2="368" y2="57" stroke="#888" stroke-width="1.5" marker-end="url(#arr)"/>

  <rect x="370" y="30" width="140" height="54" rx="8" fill="#1e1e2e" stroke="#a6e3a1" stroke-width="1.5"/>
  <text x="440" y="52" text-anchor="middle" fill="#a6e3a1" font-weight="600">ByteTrack</text>
  <text x="440" y="72" text-anchor="middle" fill="#888" font-size="11">persist ID across frames</text>

  <line x1="510" y1="57" x2="548" y2="57" stroke="#888" stroke-width="1.5" marker-end="url(#arr)"/>

  <rect x="550" y="30" width="140" height="54" rx="8" fill="#1e1e2e" stroke="#f38ba8" stroke-width="1.5"/>
  <text x="620" y="52" text-anchor="middle" fill="#f38ba8" font-weight="600">LineCounter</text>
  <text x="620" y="72" text-anchor="middle" fill="#888" font-size="11">cross product side test</text>

  <rect x="440" y="140" width="280" height="130" rx="8" fill="#1e1e2e" stroke="#f38ba8" stroke-width="1" stroke-dasharray="5,3"/>
  <text x="580" y="162" text-anchor="middle" fill="#f38ba8" font-weight="600" font-size="12">line_counter.py  logic</text>
  <text x="456" y="185" fill="#888" font-size="11">1. compute cross(line_vec, obj→line_start)</text>
  <text x="456" y="203" fill="#888" font-size="11">2. store side per track_id</text>
  <text x="456" y="221" fill="#888" font-size="11">3. sign flip  →  crossing event</text>
  <text x="456" y="239" fill="#a6e3a1" font-size="11">   +1 → −1  :  IN ↓</text>
  <text x="456" y="257" fill="#fab387" font-size="11">   −1 → +1  :  OUT ↑</text>

  <line x1="620" y1="84" x2="620" y2="138" stroke="#f38ba8" stroke-width="1.2" stroke-dasharray="4,3" marker-end="url(#arr)"/>

  <rect x="20" y="200" width="340" height="130" rx="8" fill="#1e1e2e" stroke="#cba6f7" stroke-width="1.5"/>
  <text x="190" y="222" text-anchor="middle" fill="#cba6f7" font-weight="600">Visualizer  (main.py)</text>
  <rect x="40" y="235" width="70" height="42" rx="4" fill="none" stroke="#a6e3a1" stroke-width="1.5"/>
  <text x="75" y="251" text-anchor="middle" fill="#a6e3a1" font-size="10">ID:12</text>
  <circle cx="75" cy="265" r="3" fill="#a6e3a1"/>
  <rect x="130" y="235" width="70" height="42" rx="4" fill="none" stroke="#89b4fa" stroke-width="1.5"/>
  <text x="165" y="251" text-anchor="middle" fill="#89b4fa" font-size="10">ID:7  IN</text>
  <circle cx="165" cy="265" r="3" fill="#89b4fa"/>
  <line x1="40" y1="295" x2="340" y2="295" stroke="#f38ba8" stroke-width="2"/>
  <circle cx="40" cy="295" r="4" fill="#f38ba8"/>
  <circle cx="340" cy="295" r="4" fill="#f38ba8"/>
  <text x="230" y="252" fill="#89b4fa" font-weight="600" font-size="12">IN:  14</text>
  <text x="230" y="272" fill="#fab387" font-weight="600" font-size="12">OUT:  9</text>

  <line x1="440" y1="84" x2="440" y2="160" stroke="#888" stroke-width="1.2"/>
  <line x1="440" y1="160" x2="200" y2="160" stroke="#888" stroke-width="1.2"/>
  <line x1="200" y1="160" x2="200" y2="198" stroke="#888" stroke-width="1.2" marker-end="url(#arr)"/>

  <rect x="20" y="360" width="150" height="44" rx="8" fill="#1e1e2e" stroke="#444" stroke-width="1.5"/>
  <text x="95" y="380" text-anchor="middle" fill="#cdd6f4" font-size="12">output.mp4</text>
  <text x="95" y="396" text-anchor="middle" fill="#888" font-size="10">+ terminal count log</text>
  <line x1="95" y1="330" x2="95" y2="358" stroke="#888" stroke-width="1.2" marker-end="url(#arr)"/>

  <rect x="440" y="300" width="320" height="110" rx="8" fill="#1e1e2e" stroke="#444" stroke-width="1"/>
  <text x="600" y="320" text-anchor="middle" fill="#cdd6f4" font-weight="600" font-size="12">Files</text>
  <text x="456" y="340" fill="#888" font-size="11">config.py       — line coords, classes, colors</text>
  <text x="456" y="358" fill="#888" font-size="11">line_counter.py — crossing logic</text>
  <text x="456" y="376" fill="#888" font-size="11">main.py         — video loop + drawing</text>
  <text x="456" y="394" fill="#888" font-size="11">download_sample.py — fetch demo video</text>
</svg>

## Project Structure

```
traffic_tracker/
├── config.py           # All tunable parameters (model, classes, line coords, colors)
├── line_counter.py     # Line crossing logic (cross product side test)
├── main.py             # Main inference loop + visualization
├── download_sample.py  # Download a sample traffic video
└── requirements.txt
```

## Installation

```bash
pip install -r requirements.txt
pip install yt-dlp   # only needed for downloading the sample video
```

## Usage

```bash
# Download a sample video (~60 seconds of intersection footage)
python download_sample.py

# Run the tracker; --line specifies the counting line as x1,y1,x2,y2
python main.py --source sample_traffic.mp4 --line 0,360,1280,360

# Save output video
python main.py --source sample_traffic.mp4 --line 0,360,1280,360 --output result.mp4

# Use webcam (0 = default camera)
python main.py --source 0 --line 0,360,1280,360

# Headless mode (no GUI window)
python main.py --source video.mp4 --no-display --output result.mp4
```

Press `q` to quit. Final counts are printed to the terminal:

```
[DONE] Processed 1800 frames
       Total IN : 23
       Total OUT: 19
```

## Configuration

All parameters are in `config.py`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `MODEL` | `yolov8n.pt` | Swap to `yolov8s.pt` for higher accuracy |
| `VEHICLE_CLASSES` | `[2,3,5,7]` | COCO IDs: car / motorcycle / bus / truck |
| `DEFAULT_LINE` | `(50,360,1230,360)` | Counting line in pixels; overridden by `--line` |
| `TRACK_CONF` | `0.3` | Minimum detection confidence for tracking |

## How Line Crossing Works

The cross product of the line vector **L** and the vector from the line start to the object centroid **P** determines which side the object is on. A sign flip between frames registers one crossing event; the direction is determined by which side the object came from:

```
side = (lx2-lx1)*(cy-ly1) - (ly2-ly1)*(cx-lx1)

+1 → -1 : IN  (crossing downward)
-1 → +1 : OUT (crossing upward)
```

This approach naturally prevents double-counting when a vehicle lingers near the line.

## Dataset

Any traffic video works as input. For annotated benchmark data, see [UA-DETRAC](https://detrac-db.rit.albany.edu/) (registration required), which provides labeled vehicle detection and tracking sequences for both highway and intersection scenarios.
