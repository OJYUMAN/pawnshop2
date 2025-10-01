from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QSpacerItem, QSizePolicy
from PySide6.QtCore import Qt
from PySide6.QtGui import QShortcut, QKeySequence

try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
    QT_PDF_AVAILABLE = True
except Exception:
    QPdfDocument = None
    QPdfView = None
    QT_PDF_AVAILABLE = False

# บังคับให้ไม่ใช้ Qt PDF ภายในแอปเสมอ และเปิดด้วยโปรแกรมภายนอกแทน
QT_PDF_AVAILABLE = False


class PDFPreviewDialog(QDialog):
    def __init__(self, pdf_path: str, parent=None, window_title: str = "ตัวอย่างเอกสาร PDF"):
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.setModal(True)
        self.resize(900, 700)

        self._pdf_path = pdf_path
        self._zoom_factor = 1.0
        self._current_page = 0

        layout = QVBoxLayout(self)

        if QT_PDF_AVAILABLE:
            self._doc = QPdfDocument(self)
            load_status = self._doc.load(pdf_path)

            self._view = QPdfView(self)
            self._view.setDocument(self._doc)
            # แสดงแบบหน้าต่อหน้าเพื่อความคมชัดและควบคุมการซูมได้ง่าย
            self._view.setPageMode(QPdfView.PageMode.SinglePage)
            self._view.setZoomMode(QPdfView.ZoomMode.FitToWidth)

            # แถบควบคุม
            controls = QHBoxLayout()
            self.prev_btn = QPushButton("◀")
            self.next_btn = QPushButton("▶")
            self.page_label = QLabel("หน้า 1 / {}".format(max(1, self._doc.pageCount())))
            self.zoom_out_btn = QPushButton("-")
            self.zoom_in_btn = QPushButton("+")
            self.fit_width_btn = QPushButton("พอดีกว้าง")
            self.fit_page_btn = QPushButton("พอดีหน้า")
            self.reset_zoom_btn = QPushButton("100%")

            self.prev_btn.clicked.connect(self._go_prev_page)
            self.next_btn.clicked.connect(self._go_next_page)
            self.zoom_in_btn.clicked.connect(self._zoom_in)
            self.zoom_out_btn.clicked.connect(self._zoom_out)
            self.fit_width_btn.clicked.connect(self._fit_width)
            self.fit_page_btn.clicked.connect(self._fit_page)
            self.reset_zoom_btn.clicked.connect(self._reset_zoom)

            controls.addWidget(self.prev_btn)
            controls.addWidget(self.next_btn)
            controls.addWidget(self.page_label)
            controls.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
            controls.addWidget(self.zoom_out_btn)
            controls.addWidget(self.zoom_in_btn)
            controls.addWidget(self.fit_width_btn)
            controls.addWidget(self.fit_page_btn)
            controls.addWidget(self.reset_zoom_btn)

            layout.addLayout(controls)
            layout.addWidget(self._view, 1)

            # ปรับเริ่มต้นให้คมชัดขึ้น
            self._fit_width()
            self._update_page_label()

            # คีย์ลัดสำหรับซูม
            QShortcut(QKeySequence.ZoomIn, self, activated=self._zoom_in)
            QShortcut(QKeySequence.ZoomOut, self, activated=self._zoom_out)
            QShortcut(QKeySequence("Ctrl+0"), self, activated=self._reset_zoom)
            QShortcut(QKeySequence.MoveToPreviousPage, self, activated=self._go_prev_page)
            QShortcut(QKeySequence.MoveToNextPage, self, activated=self._go_next_page)
        else:
            fallback_label = QLabel("ไม่สามารถแสดงตัวอย่างภายในแอปได้ (QtPdf ไม่พร้อมใช้งาน)\nจะเปิดด้วยโปรแกรมอ่าน PDF ภายนอกแทน", self)
            fallback_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(fallback_label, 1)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignRight)

        self.save_btn = QPushButton("บันทึก...")
        self.cancel_btn = QPushButton("ยกเลิก")

        self.save_btn.clicked.connect(self._accept)
        self.cancel_btn.clicked.connect(self.reject)

        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.cancel_btn)
        layout.addLayout(buttons_layout)

        if not QT_PDF_AVAILABLE:
            try:
                # เปิดด้วยโปรแกรมอ่าน PDF เริ่มต้นของระบบ เพื่อให้ผู้ใช้ดูตัวอย่างก่อน
                import subprocess
                import platform
                if platform.system() == "Windows":
                    os_startfile = getattr(__import__("os"), "startfile", None)
                    if os_startfile:
                        os_startfile(pdf_path)
                elif platform.system() == "Darwin":
                    subprocess.Popen(["open", pdf_path])
                else:
                    subprocess.Popen(["xdg-open", pdf_path])
            except Exception:
                pass

    def _accept(self):
        self.accept()

    # ----- Controls -----
    def _update_page_label(self):
        try:
            total = max(1, self._doc.pageCount())
            self.page_label.setText(f"หน้า {self._current_page + 1} / {total}")
        except Exception:
            pass

    def _go_prev_page(self):
        try:
            if self._current_page > 0:
                self._current_page -= 1
                self._view.setPage(self._current_page)
                self._update_page_label()
        except Exception:
            pass

    def _go_next_page(self):
        try:
            total = max(1, self._doc.pageCount())
            if self._current_page < total - 1:
                self._current_page += 1
                self._view.setPage(self._current_page)
                self._update_page_label()
        except Exception:
            pass

    def _apply_custom_zoom(self):
        try:
            self._view.setZoomMode(QPdfView.ZoomMode.Custom)
            # จำกัดช่วงซูมเพื่อป้องกันแตกหรือเล็กเกินไป
            self._zoom_factor = max(0.25, min(4.0, self._zoom_factor))
            self._view.setZoomFactor(self._zoom_factor)
        except Exception:
            pass

    def _zoom_in(self):
        self._zoom_factor *= 1.15
        self._apply_custom_zoom()

    def _zoom_out(self):
        self._zoom_factor /= 1.15
        self._apply_custom_zoom()

    def _reset_zoom(self):
        self._zoom_factor = 1.0
        self._apply_custom_zoom()

    def _fit_width(self):
        try:
            self._view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        except Exception:
            pass

    def _fit_page(self):
        try:
            self._view.setZoomMode(QPdfView.ZoomMode.FitInView)
        except Exception:
            pass


