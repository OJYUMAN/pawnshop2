# -*- coding: utf-8 -*-
import os
import tempfile
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QMessageBox
)


class WebcamCaptureDialog(QDialog):
    """Dialog แสดงกล้องแบบพรีวิว พร้อมปุ่ม ถ่าย/ถ่ายใหม่/บันทึก/ยกเลิก"""

    def __init__(self, parent=None, camera_indices=(0, 1, 2)):
        super().__init__(parent)
        self.setWindowTitle("ถ่ายรูปจากกล้อง")
        self.resize(900, 650)

        self._cv2 = None  # lazy import
        self._cap = None
        self._timer = None
        self._current_frame = None
        self._is_captured = False
        self._captured_path = ""
        self._camera_indices = camera_indices

        self._setup_ui()
        self._init_camera()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        # พรีวิวภาพ
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 1px solid #E5EAF2; background: #FAFAFA")
        self.preview_label.setMinimumSize(800, 500)
        layout.addWidget(self.preview_label)

        # ปุ่มควบคุม
        btn_row = QHBoxLayout()

        self.btn_capture = QPushButton("ถ่ายภาพ")
        self.btn_capture.clicked.connect(self._on_capture)
        btn_row.addWidget(self.btn_capture)

        self.btn_retake = QPushButton("ถ่ายใหม่")
        self.btn_retake.clicked.connect(self._on_retake)
        self.btn_retake.setEnabled(False)
        btn_row.addWidget(self.btn_retake)

        self.btn_save = QPushButton("บันทึกรูป")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_save.setEnabled(False)
        btn_row.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("ยกเลิก")
        self.btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(self.btn_cancel)

        layout.addLayout(btn_row)

    def _init_camera(self):
        try:
            try:
                import cv2
                self._cv2 = cv2
            except Exception:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบบรรณานุกรม OpenCV (opencv-python)\nกรุณาติดตั้งก่อน: pip install opencv-python")
                self.reject()
                return

            # ลองหลาย index
            for idx in self._camera_indices:
                cap = self._cv2.VideoCapture(idx)
                if cap.isOpened():
                    self._cap = cap
                    break
                cap.release()

            if self._cap is None:
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่สามารถเปิดกล้องได้")
                self.reject()
                return

            self._timer = QTimer(self)
            self._timer.timeout.connect(self._read_frame)
            self._timer.start(30)
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"เกิดข้อผิดพลาดในการเปิดกล้อง: {str(e)}")
            self.reject()

    def _read_frame(self):
        if self._is_captured:
            return
        if not self._cap:
            return
        ok, frame = self._cap.read()
        if not ok:
            return
        self._current_frame = frame
        self._update_preview(frame)

    def _update_preview(self, frame):
        # แปลง BGR -> RGB แล้วเป็น QImage
        rgb = self._cv2.cvtColor(frame, self._cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        bytes_per_line = ch * w
        qimg = QImage(rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        scaled = qimg.scaled(self.preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(QPixmap.fromImage(scaled))

    def _on_capture(self):
        if self._current_frame is None:
            return
        self._is_captured = True
        self.btn_capture.setEnabled(False)
        self.btn_retake.setEnabled(True)
        self.btn_save.setEnabled(True)

    def _on_retake(self):
        self._is_captured = False
        self.btn_capture.setEnabled(True)
        self.btn_retake.setEnabled(False)
        self.btn_save.setEnabled(False)

    def _on_save(self):
        if self._current_frame is None:
            return
        try:
            # 1) บันทึกชั่วคราว
            ts = datetime.now().strftime('%Y%m%d_%H%M%S')
            temp_out = os.path.join(tempfile.gettempdir(), f'webcam_capture_{ts}.jpg')
            self._cv2.imwrite(temp_out, self._current_frame)

            # 2) คัดลอกเข้าสู่โฟลเดอร์ product_images เพื่อให้ "บันทึกแล้วจริง"
            try:
                from app_services import copy_product_image as svc_copy_product_image
                final_path = svc_copy_product_image(temp_out)
            except Exception:
                # หากคัดลอกไม่ได้ ให้ใช้ temp ไฟล์
                final_path = temp_out

            self._captured_path = final_path
            self._safe_close(accept=True)
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", f"บันทึกรูปไม่ได้: {str(e)}")

    def reject(self):
        self._safe_close(accept=False)

    def _safe_close(self, accept: bool):
        try:
            if self._timer:
                self._timer.stop()
        except Exception:
            pass
        try:
            if self._cap:
                self._cap.release()
        except Exception:
            pass
        try:
            import cv2 as _cv
            _cv.destroyAllWindows()
        except Exception:
            pass
        if accept:
            super().accept()
        else:
            super().reject()

    def get_captured_path(self) -> str:
        return self._captured_path

    def closeEvent(self, event):
        try:
            if self._timer:
                self._timer.stop()
        except Exception:
            pass
        try:
            if self._cap:
                self._cap.release()
        except Exception:
            pass
        super().closeEvent(event)


