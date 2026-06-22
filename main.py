"""
Vehicle tracking + virtual line crossing counter.

Usage:
    python main.py --source video.mp4
    python main.py --source video.mp4 --line 0,360,1280,360 --output out.mp4
    python main.py --source 0                          # webcam

The --line argument is "x1,y1,x2,y2" in pixel coords of the input frame.
"""

import argparse
import sys
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO

import config
from line_counter import LineCounter


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--source", required=True, help="Video file path or webcam index")
    p.add_argument("--line", default=None,
                   help="Counting line as x1,y1,x2,y2 (default from config.py)")
    p.add_argument("--output", default=None, help="Save output to this path (optional)")
    p.add_argument("--model", default=config.MODEL)
    p.add_argument("--no-display", action="store_true", help="Skip GUI window")
    return p.parse_args()


def draw_line(frame: np.ndarray, counter: LineCounter):
    cv2.line(frame, (counter.x1, counter.y1), (counter.x2, counter.y2),
             config.LINE_COLOR, config.THICKNESS + 1)
    # Small endpoint dots
    for pt in [(counter.x1, counter.y1), (counter.x2, counter.y2)]:
        cv2.circle(frame, pt, 5, config.LINE_COLOR, -1)


def draw_counts(frame: np.ndarray, counter: LineCounter):
    in_count  = counter.counts[config.LABEL_IN]
    out_count = counter.counts[config.LABEL_OUT]
    cv2.putText(frame, f"IN:  {in_count}", (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, config.IN_COLOR, 2)
    cv2.putText(frame, f"OUT: {out_count}", (10, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 1.0, config.OUT_COLOR, 2)


def draw_boxes(frame: np.ndarray, boxes, counter: LineCounter):
    """Draw bounding boxes + IDs + crossing labels."""
    for box in boxes:
        x1, y1, x2, y2 = map(int, box.xyxy[0])
        tid = int(box.id[0]) if box.id is not None else -1
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        color = config.BOX_COLOR
        label = f"ID:{tid}"

        if tid in counter.crossed_this_frame:
            direction = counter.crossed_this_frame[tid]
            color = config.IN_COLOR if direction == config.LABEL_IN else config.OUT_COLOR
            label += f" {direction}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, config.THICKNESS)
        cv2.putText(frame, label, (x1, y1 - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, config.FONT_SCALE, color, config.THICKNESS)
        # Centroid dot
        cv2.circle(frame, (cx, cy), 3, color, -1)


def main():
    args = parse_args()

    # Parse counting line
    if args.line:
        coords = list(map(int, args.line.split(",")))
        lx1, ly1, lx2, ly2 = coords
    else:
        lx1, ly1, lx2, ly2 = config.DEFAULT_LINE

    counter = LineCounter(lx1, ly1, lx2, ly2)

    # Open video source
    src = int(args.source) if args.source.isdigit() else args.source
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        sys.exit(f"Cannot open source: {args.source}")

    w  = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h  = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25

    writer = None
    if args.output:
        fourcc = cv2.VideoWriter_fourcc(*config.FOURCC)
        writer = cv2.VideoWriter(args.output, fourcc, fps, (w, h))

    model = YOLO(args.model)

    print(f"[INFO] Source : {args.source}  ({w}x{h} @ {fps:.1f} fps)")
    print(f"[INFO] Line   : ({lx1},{ly1}) → ({lx2},{ly2})")
    print("[INFO] Press 'q' to quit.\n")

    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        counter.reset_frame()

        results = model.track(
            frame,
            persist=True,
            classes=config.VEHICLE_CLASSES,
            conf=config.TRACK_CONF,
            iou=config.TRACK_IOU,
            tracker=config.TRACKER,
            verbose=False,
        )

        boxes = results[0].boxes
        if boxes is not None and boxes.id is not None:
            for box in boxes:
                tid = int(box.id[0])
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
                direction = counter.update(tid, cx, cy)
                if direction:
                    print(f"  Frame {frame_idx:05d} | ID {tid:4d} crossed → {direction}  "
                          f"[IN={counter.counts[config.LABEL_IN]}  "
                          f"OUT={counter.counts[config.LABEL_OUT]}]")

            draw_boxes(frame, boxes, counter)

        draw_line(frame, counter)
        draw_counts(frame, counter)

        if writer:
            writer.write(frame)

        if not args.no_display:
            cv2.imshow("Vehicle Tracker", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

        frame_idx += 1

    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()

    print(f"\n[DONE] Processed {frame_idx} frames")
    print(f"       Total IN : {counter.counts[config.LABEL_IN]}")
    print(f"       Total OUT: {counter.counts[config.LABEL_OUT]}")


if __name__ == "__main__":
    main()
