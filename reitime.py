from ultralytics import YOLO
import cv2

# โหลดโมเดล YOLO (coco dataset)
model = YOLO("yolov8n.pt")

# เปิดกล้อง
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("❌ ไม่สามารถเปิดกล้องได้")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # รัน YOLO ตรวจจับวัตถุ
    results = model(frame, stream=True)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])  # คลาสวัตถุ
            conf = float(box.conf[0])  # ความมั่นใจ (%)

            # เฉพาะคลาสรถ
            if cls in [2, 3, 5, 7]:  
                # 2 = Car, 3 = Motorcycle, 5 = Bus, 7 = Truck

                x1, y1, x2, y2 = box.xyxy[0]

                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)),
                              (0, 255, 0), 2)

                cv2.putText(frame, f"{model.names[cls]} {conf:.2f}",
                            (int(x1), int(y1) - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            (0, 255, 0), 2)

    cv2.imshow("YOLO Real-Time Car Detection", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
