"""
All tunable parameters in one place.
Line is defined as two points in pixel coordinates (x, y).
Adjust LINE_START / LINE_END to match your video's counting zone.
"""

# YOLOv8 model — 'yolov8n.pt' is fastest; swap to 'yolov8s.pt' for more accuracy
MODEL = "yolov8n.pt"

# COCO class IDs for vehicles: car=2, motorcycle=3, bus=5, truck=7
VEHICLE_CLASSES = [2, 3, 5, 7]

# ByteTrack params (passed to ultralytics tracker)
TRACKER = "bytetrack.yaml"
TRACK_CONF = 0.3   # min detection confidence
TRACK_IOU  = 0.5   # NMS IoU threshold

# Virtual counting line — overridden by --line CLI flag
# Format: (x1, y1, x2, y2)  in pixels of the output frame
DEFAULT_LINE = (50, 360, 1230, 360)

# Direction labels: objects crossing from top→bottom are "IN", bottom→top are "OUT"
LABEL_IN  = "IN"
LABEL_OUT = "OUT"

# Visualization
BOX_COLOR     = (0, 255, 0)    # BGR green for bounding boxes
LINE_COLOR    = (0, 0, 255)    # BGR red for counting line
IN_COLOR      = (255, 200, 0)  # BGR cyan-ish for IN count text
OUT_COLOR     = (0, 165, 255)  # BGR orange for OUT count text
FONT_SCALE    = 0.6
THICKNESS     = 2

# Output video codec
FOURCC = "mp4v"
