from ultralytics import YOLO
import cv2
import pyttsx3
from datetime import datetime
import time

# ------------------------
# ระบบเสียง
# ------------------------
engine = pyttsx3.init('sapi5')  # ใช้ SAPI5 สำหรับ Windows
engine.setProperty('rate', 150)  # ปรับความเร็วพูด

last_speak_time = 0  # เวลา last speak
SPEAK_INTERVAL = 1  # วินาที หน่วงเวลาเพื่อไม่ให้เสียงซ้อน

def speak_time():
    global last_speak_time
    now = time.time()
    if now - last_speak_time < SPEAK_INTERVAL:
        return  # ถ้าเพิ่งพูดไปแล้ว ให้ข้าม
    last_speak_time = now

    current_time = datetime.now()
    text = f"รถผ่านเวลา {current_time.hour} นาฬิกา {current_time.minute} นาที {current_time.second} วินาที"
    print(text)  # ดู log ใน console ด้วย
    engine.say(text)
    engine.runAndWait()

# ------------------------
# โหลดโมเดล YOLO
# ------------------------
model = YOLO("yolov8n.pt")  # โหลด YOLOv8 Nano
# model = YOLO("yolov8n.pt")  # ใช้โมเดลอื่นได้ตามต้องการ

# ------------------------
# เปิดกล้อง
# ------------------------
cap = cv2.VideoCapture(0)  # 0 = กล้องคอมพิวเตอร์
# cap = cv2.VideoCapture("video.mp4")  # ใช้คลิปวิดีโอจากไฟล์ก็ได้

if not cap.isOpened():
    print("❌ ไม่สามารถเปิดกล้องหรือไฟล์วิดีโอได้")
    exit()

# ------------------------
# วนลูปตรวจจับรถ
# ------------------------
while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame, stream=True)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            if cls in [2,3,5,7]:  # รถทุกประเภท: car, motorcycle, bus, truck
                x1, y1, x2, y2 = [int(v) for v in box.xyxy[0]]

                # วาดกรอบรถ
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
                cv2.putText(frame, "Car", (x1, y1-10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)

                # พูดเวลา
                speak_time()

    cv2.imshow("Real-Time Car Detection with Voice", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
