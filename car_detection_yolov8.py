from ultralytics import YOLO
import cv2

# โหลดโมเดล YOLOv8n (nano)
model = YOLO("yolov8n.pt")

# อ่านภาพ
image = cv2.imread("car.png")

# ตรวจจับวัตถุ
results = model(image)

# วาดกรอบเฉพาะ "รถ"
for result in results:
    for box in result.boxes:
        cls_id = int(box.cls[0])
        conf = float(box.conf[0])
        label = model.names[cls_id]

        if label == "car":
            x1, y1, x2, y2 = map(int, box.xyxy[0])

            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            cv2.putText(
                image,
                f"{label} {conf:.2f}",
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

# แสดงผล
cv2.imshow("Car Detection - YOLOv8n", image)
cv2.waitKey(0)
cv2.destroyAllWindows()
