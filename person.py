import cv2
import time
from datetime import datetime
from pytz import timezone
from ultralytics import YOLO

class PeopleCounter:
    def __init__(self, model_path="yolov8n.pt"):
        self.model = YOLO(model_path)
        self.people_data = {}  # {id: {"entry": datetime, "exit": datetime, "stay": float}}
        self.total_count = 0

    def track_people(self, frame):
        tz = timezone("Asia/Bangkok")
        now_th = datetime.now(tz)
        current_time = time.time()

        # ตรวจจับเฉพาะคน (class 0)
        results = self.model.track(frame, persist=True, classes=[0])
        annotated_frame = results[0].plot()

        ids = []
        if results[0].boxes.id is not None:
            ids = results[0].boxes.id.cpu().numpy()

            for pid in ids:
                if pid not in self.people_data:
                    # คนใหม่เข้าเฟรม
                    self.people_data[pid] = {
                        "entry": now_th,
                        "exit": None,
                        "stay": 0.0,
                        "last_seen": current_time
                    }
                    self.total_count += 1
                else:
                    # คนเดิมยังอยู่ในเฟรม
                    stay_time = current_time - self.people_data[pid]["last_seen"]
                    self.people_data[pid]["stay"] += stay_time
                    self.people_data[pid]["last_seen"] = current_time
                    self.people_data[pid]["exit"] = None  # ยังไม่ออก

        # ตรวจสอบว่าคนไหนออกจากเฟรมแล้ว
        existing_ids = set(ids)
        for pid in list(self.people_data.keys()):
            if pid not in existing_ids:
                if self.people_data[pid]["exit"] is None:
                    self.people_data[pid]["exit"] = now_th

        # ----------------------------- #
        # ส่วนแสดงผลบนจอ
        # ----------------------------- #
        cv2.putText(
            annotated_frame,
            f"Thailand Time: {now_th.strftime('%H:%M:%S')}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2,
        )

        cv2.putText(
            annotated_frame,
            f"Total People Detected: {self.total_count}",
            (20, 60),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2,
        )

        y_offset = 100
        for pid, data in list(self.people_data.items())[-5:]:  # แสดงแค่ 5 คนล่าสุด
            entry_str = data["entry"].strftime("%H:%M:%S") if data["entry"] else "-"
            exit_str = data["exit"].strftime("%H:%M:%S") if data["exit"] else "-"
            stay_str = f"{data['stay']:.1f}s"

            info = f"ID:{int(pid)} | In:{entry_str} | Out:{exit_str} | Stay:{stay_str}"
            cv2.putText(
                annotated_frame,
                info,
                (20, y_offset),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2,
            )
            y_offset += 25

        return annotated_frame


# ----------------------------- #
# ใช้งานจริงกับกล้องเว็บแคม
# ----------------------------- #
def main():
    cap = cv2.VideoCapture(0)
    counter = PeopleCounter()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = counter.track_people(frame)
        cv2.imshow("People Counter & Time Tracker (Thailand)", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
