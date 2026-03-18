import cv2
from ultralytics import YOLO

VEHICLE_CLASSES = {2, 3, 5, 7}  # car, motorcycle, bus, truck (COCO class IDs)

class VehicleDetector:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")

    def detect(self, frame):
        results = self.model(frame, verbose=False)[0]
        detections = []
        vehicle_count = 0

        for box in results.boxes:
            cls = int(box.cls[0])
            if cls not in VEHICLE_CLASSES:
                continue
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            conf = float(box.conf[0])
            label = f"{results.names[cls]} {conf:.2f}"
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 212, 255), 2)
            cv2.putText(frame, label, (x1, y1 - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 212, 255), 1)
            detections.append((x1, y1, x2 - x1, y2 - y1))

        # HUD overlay
        cv2.rectangle(frame, (0, 0), (240, 36), (2, 11, 24), -1)
        cv2.putText(frame, f"AURA | Vehicles: {vehicle_count}", (8, 24),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 212, 255), 1)

        return frame, vehicle_count, detections
