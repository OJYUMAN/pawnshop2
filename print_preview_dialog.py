# -*- coding: utf-8 -*-
"""
Print Preview + Full A4 OR Half-A4 Continuous (top/bottom split)
- Preview: Qt PDF (PySide6 + pyside6-addons)
- Print: Qt PrintSupport (force paper, fit-to-page, 1 page/sheet)
- Half-A4 continuous: ผ่าหน้า A4 เป็น 2 หน้า (บน/ล่าง) ต่อกันเป็น A4
- NEW:
  * Scale % (ขยายทั้งหน้าเพื่อให้ตัวหนังสือใหญ่ขึ้น & กินพื้นที่มากขึ้น)
  * Margins (mm) ซ้าย/ขวา/บน/ล่าง — ลดพื้นที่ว่างให้น้อยลง อ่านชัด
  * Overlap / Feed gap / แยก 2 งาน / หมุนครึ่งล่าง (สำหรับเครื่องต่อเนื่อง)
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QComboBox, QGroupBox,
    QRadioButton, QButtonGroup, QMessageBox, QFileDialog, QSpacerItem, QSizePolicy,
    QScrollArea, QLineEdit, QCheckBox
)
from PySide6.QtCore import Qt, QSize, QSizeF, QMarginsF, QUrl, QRectF
from PySide6.QtGui import QPainter, QTransform

import os, glob, platform, tempfile, subprocess

# ---------- PDF Preview ----------
try:
    from PySide6.QtPdf import QPdfDocument
    from PySide6.QtPdfWidgets import QPdfView
    QT_PDF_AVAILABLE = True
except ImportError:
    QPdfDocument = None
    QPdfView = None
    QT_PDF_AVAILABLE = False

# ---------- Print Support ----------
try:
    from PySide6.QtPrintSupport import QPrinter, QPrinterInfo
    from PySide6.QtGui import QPageLayout, QPageSize
    QT_PRINT_AVAILABLE = True
except ImportError:
    QPrinter = QPrinterInfo = QPageLayout = QPageSize = None
    QT_PRINT_AVAILABLE = False


HALF_A4_W_MM = 210.0
HALF_A4_H_MM = 148.5
A4_H_MM = 297.0


class PrintPreviewDialog(QDialog):
    def __init__(self, parent=None, contract_type="pawn",
                 pdf_generator_func=None,
                 contract_data=None, customer_data=None, product_data=None,
                 original_contract_data=None, shop_data=None, font_size_multiplier=None):
        super().__init__(parent)

        self.contract_type = contract_type
        self.pdf_generator_func = pdf_generator_func
        self.contract_data = contract_data or {}
        self.customer_data = customer_data or {}
        self.product_data = product_data or {}
        self.original_contract_data = original_contract_data or {}
        self.shop_data = shop_data or {}
        
        # Store font_size_multiplier if provided, otherwise load from config
        if font_size_multiplier is not None:
            self.font_size_multiplier = font_size_multiplier
        else:
            try:
                from shop_config_loader import load_shop_config
                shop_config = load_shop_config() or {}
                font_size_percent = shop_config.get('font_size_percent', 100)
                self.font_size_multiplier = font_size_percent / 100.0
            except Exception:
                self.font_size_multiplier = 1.0

        self.temp_pdf_path = None
        self.printers = []

        self.setWindowTitle("พรีวิวและเลือกการปริ้น - " + ("สัญญาฝากขาย" if contract_type == 'pawn' else "สัญญาไถ่คืน"))
        self.resize(1100, 760)
        self.setModal(True)

        self._build_ui()
        self._load_printers()
        self._generate_preview()

    # ---------------- UI ----------------
    def _build_ui(self):
        layout = QVBoxLayout(self)

        title = QLabel("พรีวิวเอกสาร" + ("สัญญาฝากขาย" if self.contract_type == 'pawn' else "สัญญาไถ่คืน"))
        title.setStyleSheet("QLabel{font-size:18px;font-weight:700;color:#2c3e50;padding:8px;background:#ecf0f1;border-radius:6px}")
        layout.addWidget(title)

        # Preview
        preview_group = QGroupBox("ตัวอย่างเอกสาร")
        pv = QVBoxLayout(preview_group)
        self.preview_area = QScrollArea()
        self.preview_area.setWidgetResizable(True)
        self.preview_area.setMinimumHeight(430)
        self.preview_area.setStyleSheet("QScrollArea{border:2px solid #bdc3c7;border-radius:6px;background:#F3F4F6}")
        self.preview_label = QLabel("กำลังสร้างตัวอย่างเอกสาร...")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("QLabel{color:#7f8c8d;padding:24px}")
        self.preview_area.setWidget(self.preview_label)
        pv.addWidget(self.preview_area)
        layout.addWidget(preview_group)

        # Print options
        print_group = QGroupBox("ตัวเลือกการปริ้น")
        pl = QVBoxLayout(print_group)
        self.opt_group = QButtonGroup(self)

        self.print_radio = QRadioButton("ปริ้นกับเครื่องปริ้น")
        self.print_radio.setChecked(True)
        self.opt_group.addButton(self.print_radio, 0)
        pl.addWidget(self.print_radio)

        # --- Row 1: printer + mode ---
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Printer:"))
        self.printer_combo = QComboBox(); self.printer_combo.setMinimumWidth(260)
        row1.addWidget(self.printer_combo)

        row1.addWidget(QLabel("โหมดกระดาษ:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "A4 เต็มแผ่น (210×297 mm)",
            "ต่อเนื่อง ครึ่ง A4 (210×148.5 mm) → 2 หน้า/แผ่น A4"
        ])
        # Set default paper mode from configuration
        self._set_default_paper_mode()
        row1.addWidget(self.mode_combo)

        row1.addWidget(QLabel("Scale %:"))
        self.scale_percent = QLineEdit("115"); self.scale_percent.setFixedWidth(70)
        row1.addWidget(self.scale_percent)

        row1.addWidget(QLabel("Overlap (มม.):"))
        self.overlap_mm = QLineEdit("0"); self.overlap_mm.setFixedWidth(70)
        row1.addWidget(self.overlap_mm)

        row1.addWidget(QLabel("Feed gap (มม.):"))
        self.feedgap_mm = QLineEdit("0"); self.feedgap_mm.setFixedWidth(70)
        row1.addWidget(self.feedgap_mm)

        row1.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        pl.addLayout(row1)

        # --- Row 2: margins + toggles
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Margins (mm) L:"))
        self.m_left = QLineEdit("1"); self.m_left.setFixedWidth(60)
        row2.addWidget(self.m_left)
        row2.addWidget(QLabel("R:"))
        self.m_right = QLineEdit("1"); self.m_right.setFixedWidth(60)
        row2.addWidget(self.m_right)
        row2.addWidget(QLabel("T:"))
        self.m_top = QLineEdit("1"); self.m_top.setFixedWidth(60)
        row2.addWidget(self.m_top)
        row2.addWidget(QLabel("B:"))
        self.m_bottom = QLineEdit("1"); self.m_bottom.setFixedWidth(60)
        row2.addWidget(self.m_bottom)

        self.chk_separate_jobs = QCheckBox("แยกเป็น 2 งานพิมพ์")
        self.chk_rotate_bottom = QCheckBox("หมุนครึ่งล่าง 180°")
        row2.addWidget(self.chk_separate_jobs)
        row2.addWidget(self.chk_rotate_bottom)

        row2.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        pl.addLayout(row2)

        # Save as PDF
        self.pdf_radio = QRadioButton("บันทึกเป็นไฟล์ PDF")
        self.opt_group.addButton(self.pdf_radio, 1)
        pl.addWidget(self.pdf_radio)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("ตำแหน่งไฟล์:"))
        self.pdf_path_edit = QLineEdit()
        self.pdf_path_edit.setPlaceholderText("เลือกตำแหน่งบันทึกไฟล์ PDF...")
        row3.addWidget(self.pdf_path_edit)
        b = QPushButton("เลือก..."); b.clicked.connect(self._browse_pdf_location)
        row3.addWidget(b)
        pl.addLayout(row3)
        layout.addWidget(print_group)

        # Buttons
        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.refresh_btn = QPushButton("รีเฟรชตัวอย่าง"); self.refresh_btn.clicked.connect(self._generate_preview); btns.addWidget(self.refresh_btn)
        self.print_btn = QPushButton("ปริ้น/บันทึก"); self.print_btn.clicked.connect(self._execute); btns.addWidget(self.print_btn)
        cancel = QPushButton("ยกเลิก"); cancel.clicked.connect(self.reject); btns.addWidget(cancel)
        layout.addLayout(btns)

    # ---------------- Preview ----------------
    def _load_printers(self):
        try:
            if QT_PRINT_AVAILABLE:
                for info in QPrinterInfo.availablePrinters():
                    name = info.printerName()
                    if name:
                        self.printers.append(name)
                        self.printer_combo.addItem(name)

            if not self.printers:
                if platform.system() == "Windows":
                    ps = ["powershell","-NoProfile","-Command","Get-Printer | Select-Object -ExpandProperty Name"]
                    r = subprocess.run(ps, capture_output=True, text=True, encoding="utf-8")
                    if r.returncode == 0 and r.stdout:
                        for line in r.stdout.splitlines():
                            name = line.strip()
                            if name: self.printers.append(name); self.printer_combo.addItem(name)
                else:
                    r = subprocess.run(["lpstat","-p"], capture_output=True, text=True)
                    if r.returncode == 0:
                        for line in r.stdout.splitlines():
                            if line.startswith("printer "):
                                name = line.split()[1]; self.printers.append(name); self.printer_combo.addItem(name)

            if not self.printers:
                self.printer_combo.addItem("ไม่พบเครื่องปริ้น"); self.print_radio.setEnabled(False)
        except Exception as e:
            print("load printers error:", e)
            self.printer_combo.addItem("ไม่สามารถโหลดรายการเครื่องปริ้น"); self.print_radio.setEnabled(False)

    def _set_default_paper_mode(self):
        """Set default paper mode from shop configuration"""
        try:
            from shop_config_loader import load_shop_config
            shop_config = load_shop_config()
            default_mode = shop_config.get('default_paper_mode', 1)  # Default to Half-A4 continuous
            self.mode_combo.setCurrentIndex(default_mode)
        except Exception as e:
            print("Error loading paper mode setting:", e)
            # Default to Half-A4 continuous (index 1)
            self.mode_combo.setCurrentIndex(1)

    def _generate_preview(self):
        try:
            self.preview_label.setText("กำลังสร้างตัวอย่างเอกสาร...")
            self.print_btn.setEnabled(False)
            t = tempfile.NamedTemporaryFile(suffix=".pdf", delete=False); self.temp_pdf_path = t.name; t.close()

            if self.pdf_generator_func:
                if self.contract_type == "pawn":
                    self.pdf_generator_func(
                        contract_data=self.contract_data, customer_data=self.customer_data,
                        product_data=self.product_data, shop_data=self.shop_data,
                        output_file=self.temp_pdf_path,
                        font_size_multiplier=self.font_size_multiplier
                    )
                else:
                    # For redemption contracts, use original_contract_data for contract info
                    # but merge with redemption data for amounts
                    if self.contract_type == "redemption" and self.original_contract_data:
                        # Merge original contract data with redemption data
                        merged_contract_data = {
                            **self.original_contract_data,
                            'total_redemption': self.contract_data.get('redemption_amount', 0),
                            'redemption_date': self.contract_data.get('redemption_date', ''),
                            'signed_date': self.contract_data.get('redemption_date', '')
                        }
                        self.pdf_generator_func(
                            contract_data=merged_contract_data, customer_data=self.customer_data,
                            product_data=self.product_data, shop_data=self.shop_data,
                            output_file=self.temp_pdf_path,
                            font_size_multiplier=self.font_size_multiplier
                        )
                    else:
                        self.pdf_generator_func(
                            contract_data=self.contract_data, customer_data=self.customer_data,
                            product_data=self.product_data, shop_data=self.shop_data,
                            output_file=self.temp_pdf_path,
                            font_size_multiplier=self.font_size_multiplier
                        )
            else:
                # ตัวอย่าง minimal
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import mm
                c = canvas.Canvas(self.temp_pdf_path, pagesize=A4)
                c.setFont("Helvetica", 13)
                c.drawString(18*mm, 280*mm, "ตัวอย่างสัญญา (A4) – Preview only")
                c.rect(12*mm, 28*mm, 186*mm, 244*mm)
                c.showPage(); c.save()

            if not os.path.exists(self.temp_pdf_path) or os.path.getsize(self.temp_pdf_path) == 0:
                raise RuntimeError("ไฟล์ PDF ว่างเปล่า")

            self._show_preview()
        except Exception as e:
            self.preview_label.setText("เกิดข้อผิดพลาดในการสร้างตัวอย่าง: " + str(e))
        finally:
            self.print_btn.setEnabled(True)

    def _show_preview(self):
        if not QT_PDF_AVAILABLE or not (QPdfDocument and QPdfView):
            if platform.system() == "Windows":
                os.startfile(self.temp_pdf_path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", self.temp_pdf_path])
            else:
                subprocess.Popen(["xdg-open", self.temp_pdf_path])
            self.preview_label.setText("เปิดตัวอย่างด้วยโปรแกรมอ่าน PDF ภายนอกแล้ว")
            return

        try:
            self.pdf_document = QPdfDocument()
            used_set_source = False
            try:
                self.pdf_document.setSource(QUrl.fromLocalFile(self.temp_pdf_path))
                used_set_source = True
            except Exception:
                pass
            if not used_set_source:
                self.pdf_document.load(self.temp_pdf_path)

            self.pdf_view = QPdfView()
            self.pdf_view.setDocument(self.pdf_document)
            self.preview_area.takeWidget()
            self.preview_area.setWidget(self.pdf_view)
            self.pdf_view.setZoomMode(QPdfView.ZoomMode.FitToWidth)
        except Exception as e:
            self.preview_label.setText("ไม่สามารถแสดงพรีวิว PDF ได้: " + str(e))

    # ---------------- Print ----------------
    def _execute(self):
        try:
            if not self.temp_pdf_path or not os.path.exists(self.temp_pdf_path):
                QMessageBox.warning(self, "แจ้งเตือน", "ไม่พบไฟล์เอกสารที่จะปริ้น")
                return

            if self.print_radio.isChecked():
                name = self.printer_combo.currentText()
                if not name or name == "ไม่พบเครื่องปริ้น":
                    QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกเครื่องปริ้น")
                    return

                if QT_PRINT_AVAILABLE:
                    self._print_via_qt(name)
                else:
                    self._print_fallback(name)
            else:
                out = self.pdf_path_edit.text().strip()
                if not out:
                    QMessageBox.warning(self, "แจ้งเตือน", "กรุณาเลือกตำแหน่งบันทึกไฟล์ PDF")
                    return
                import shutil; shutil.copy2(self.temp_pdf_path, out)

            QMessageBox.information(self, "สำเร็จ", "ดำเนินการเสร็จสิ้น")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "ผิดพลาด", "เกิดข้อผิดพลาด: " + str(e))

    def _print_via_qt(self, printer_name: str):
        """พิมพ์แบบคมชัด: เรนเดอร์ภาพตาม 'ขนาดปลายทาง' แล้วค่อยวาด (ไม่อัปสเกลภาพ)"""
        if not (QPrinter and QPrinterInfo and QPageLayout and QPageSize):
            self._print_fallback(printer_name); return

        # map printer
        target = None
        for info in QPrinterInfo.availablePrinters():
            if info.printerName() == printer_name:
                target = info; break

        mode = self.mode_combo.currentIndex()      # 0=A4, 1=Half-A4 continuous
        separate_jobs = self.chk_separate_jobs.isChecked()
        rotate_bottom = self.chk_rotate_bottom.isChecked()

        # parse numeric inputs
        def _f(txt, default=0.0):
            try: return float(txt.strip())
            except: return default

        scale_pct   = max(10.0, _f(self.scale_percent.text(), 115.0)) / 100.0
        overlap_mm  = max(0.0, _f(self.overlap_mm.text(),   0.0))
        feedgap_mm  = max(0.0, _f(self.feedgap_mm.text(),   0.0))
        m_left      = max(0.0, _f(self.m_left.text(),       1.0))
        m_right     = max(0.0, _f(self.m_right.text(),      1.0))
        m_top       = max(0.0, _f(self.m_top.text(),        1.0))
        m_bottom    = max(0.0, _f(self.m_bottom.text(),     1.0))

        # load PDF
        doc = getattr(self, "pdf_document", None)
        if not doc and QT_PDF_AVAILABLE and QPdfDocument:
            doc = QPdfDocument()
            try:
                doc.setSource(QUrl.fromLocalFile(self.temp_pdf_path))
            except Exception:
                doc.load(self.temp_pdf_path)
        if not doc:
            raise RuntimeError("ไม่พบเอกสาร PDF สำหรับพิมพ์")

        page_count = doc.pageCount()
        if page_count <= 0:
            raise RuntimeError("ไฟล์ PDF ไม่มีหน้า")

        # ตั้งค่าหน้ากระดาษ
        if mode == 0:
            qps = QPageSize(QPageSize.A4); page_h_mm = 297.0
        else:
            qps = QPageSize(QSizeF(210.0, 148.5), QPageSize.Millimeter, "HalfA4"); page_h_mm = 148.5

        def _new_printer():
            pr = QPrinter(QPrinter.HighResolution)
            if target: pr.setPrinterName(target.printerName())
            pr.setPageLayout(QPageLayout(qps, QPageLayout.Portrait, QMarginsF(0,0,0,0)))
            pr.setFullPage(True); pr.setResolution(300)
            return pr

        if mode == 0:
            # ---------- A4 เต็มแผ่น ----------
            pr = _new_printer()
            pa = QPainter(pr)
            try:
                trg = pr.pageRect(QPrinter.DevicePixel)
                for p in range(page_count):
                    if p > 0: pr.newPage()

                    # ขนาดพื้นที่วาดจริงหลังหัก margins/feedgap (A4 ไม่ใช้ feedgap)
                    px_per_mm = trg.height() / page_h_mm
                    padL = int(m_left   * px_per_mm)
                    padR = int(m_right  * px_per_mm)
                    padT = int(m_top    * px_per_mm)
                    padB = int(m_bottom * px_per_mm)
                    dest = trg.adjusted(padL, padT, -padR, -padB)

                    # *** เรนเดอร์ตามขนาดปลายทาง × scale_pct × supersample (ปรับตามสเกล) ***
                    # สำหรับสเกล 120% ขึ้นไป ใช้ supersample สูงขึ้น
                    if scale_pct >= 1.2:
                        oversample = 5.0  # สเกล 120%+ ใช้ 5x supersample
                    else:
                        oversample = 4.0  # สเกลต่ำกว่า ใช้ 4x supersample
                    
                    render_w = int(dest.width()  * scale_pct * oversample)
                    render_h = int(dest.height() * scale_pct * oversample)
                    full_img = self._render_page_supersampled(doc, p, render_w, render_h)

                    # วาดแบบไม่อัปสเกลเกิน (ถ้าต้องย่อจะคม)
                    self._draw_fit_from_srcimg(pa, full_img, dest)
            finally:
                pa.end()
            return

        # ---------- Half-A4 ต่อเนื่อง: ผ่าหน้า A4 เป็น 2 ----------
        for p in range(page_count):
            # เตรียมเครื่องพิมพ์ (แยกงาน/งานเดียว)
            if separate_jobs:
                # งาน 1: ครึ่งบน
                pr1 = _new_printer(); pa1 = QPainter(pr1)
                # งาน 2: ครึ่งล่าง
                pr2 = _new_printer(); pa2 = QPainter(pr2)
            else:
                pr = _new_printer(); pa = QPainter(pr)

            # ขนาดพื้นที่วาดจริงของ Half-A4
            target_rect = (pr1.pageRect(QPrinter.DevicePixel) if separate_jobs else pr.pageRect(QPrinter.DevicePixel))
            px_per_mm = target_rect.height() / page_h_mm

            padL = int(m_left   * px_per_mm)
            padR = int(m_right  * px_per_mm)
            padT = int(m_top    * px_per_mm)
            padB = int(m_bottom * px_per_mm)

            # feedgap: เผื่อช่องว่างบน/ล่างระหว่างแผ่น
            feed_px = int(feedgap_mm * ( (297.0 if mode==0 else 148.5) and (target_rect.height()/page_h_mm) ))

            dest_top    = target_rect.adjusted(padL, padT, -padR, -(padB + feed_px))
            dest_bottom = target_rect.adjusted(padL, padT + feed_px, -padR, -padB)

            # ****** เรนเดอร์ "ทั้งหน้า A4 ต้นฉบับ" ให้ใหญ่ตาม scale แล้วค่อย "ครอป" ครึ่งบน/ล่าง ******
            # กำหนดขนาดเรนเดอร์รวม: สูง ≈ 2 × ครึ่ง A4 (ให้พอครอป) + supersample ปรับตามสเกล
            if scale_pct >= 1.2:
                oversample = 5.0  # สเกล 120%+ ใช้ 5x supersample
            else:
                oversample = 4.0  # สเกลต่ำกว่า ใช้ 4x supersample
                
            render_full_w = int(max(dest_top.width(), dest_bottom.width()) * scale_pct * oversample)
            render_full_h = int((dest_top.height() + dest_bottom.height()) * scale_pct * oversample) + int(px_per_mm*10)

            full_img = self._render_page_supersampled(doc, p, render_full_w, render_full_h)

            # คำนวณครึ่งบน/ล่าง (รวม overlap)
            A4_px_per_mm = full_img.height() / 297.0
            overlap_px   = int(overlap_mm * A4_px_per_mm)
            half_h       = full_img.height() // 2

            top_src    = QRectF(0, 0, full_img.width(),       half_h + overlap_px)
            bottom_src = QRectF(0, half_h - overlap_px, full_img.width(), half_h + overlap_px)

            if separate_jobs:
                # บน
                self._draw_fit_from_srcimg(pa1, full_img, dest_top,    src_rect=top_src)
                pa1.end()
                # ล่าง
                self._draw_fit_from_srcimg(pa2, full_img, dest_bottom, src_rect=bottom_src, rotate180=self.chk_rotate_bottom.isChecked())
                pa2.end()
            else:
                # บน
                self._draw_fit_from_srcimg(pa, full_img, dest_top, src_rect=top_src)
                pr.newPage()
                # ล่าง
                self._draw_fit_from_srcimg(pa, full_img, dest_bottom, src_rect=bottom_src, rotate180=self.chk_rotate_bottom.isChecked())
                pa.end()

    # ---- helpers ----
    def _render_page(self, doc: QPdfDocument, page_index: int, width_px: int, height_px: int):
        try:
            return doc.render(page_index, QSize(width_px, height_px))
        except TypeError:
            return doc.render(page_index, QSizeF(float(width_px), float(height_px)))

    def _render_page_supersampled(self, doc: QPdfDocument, page_index: int, target_w: int, target_h: int):
        """
        เรนเดอร์หน้า PDF ให้ 'ใหญ่กว่าขนาดปลายทาง' (supersample) เพื่อความคม
        - target_w/target_h คือขนาดปลายทาง × scale × oversample ที่คำนวณไว้แล้ว
        """
        # กันพลาดขั้นต่ำ + เพิ่มความละเอียดขั้นต่ำสำหรับความคม
        target_w = max(300, int(target_w))
        target_h = max(300, int(target_h))
        
        # เพิ่มความละเอียดสำหรับสเกล 120% ขึ้นไป
        if target_w > 2000 or target_h > 2000:
            # สำหรับสเกลใหญ่ ให้เพิ่มความละเอียดอีก 50% เพื่อความคมชัด
            target_w = int(target_w * 1.5)
            target_h = int(target_h * 1.5)
        
        try:
            return doc.render(page_index, QSize(target_w, target_h))
        except TypeError:
            return doc.render(page_index, QSizeF(float(target_w), float(target_h)))

    def _draw_fit_from_srcimg(self, painter: QPainter, img, dest_rect, src_rect: QRectF=None, rotate180: bool=False):
        """
        วาดภาพให้ 'พอดีพื้นที่' โดย **ไม่ขยายเกิน** (ไม่ทำให้แตก)
        - ถ้าภาพใหญ่กว่าพื้นที่ → ย่อ (คม)
        - ถ้าภาพเล็กกว่าพื้นที่ → ขยายเล็กน้อยได้ แต่โค้ดเราพยายามเรนเดอร์ให้ใหญ่ตั้งแต่แรกอยู่แล้ว
        """
        if src_rect is None:
            src_rect = QRectF(0, 0, img.width(), img.height())

        s_w, s_h = src_rect.width(), src_rect.height()
        d_w, d_h = dest_rect.width(), dest_rect.height()

        scale = min(d_w / s_w, d_h / s_h)
        draw_w, draw_h = s_w * scale, s_h * scale
        dx = dest_rect.x() + (d_w - draw_w) / 2
        dy = dest_rect.y() + (d_h - draw_h) / 2

        # ตั้งค่า rendering hints สำหรับความคมชัด
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.setRenderHint(QPainter.SmoothPixmapTransform, True)
        painter.setRenderHint(QPainter.TextAntialiasing, True)
        painter.setRenderHint(QPainter.LosslessImageRendering, True)

        if rotate180:
            from PySide6.QtGui import QTransform
            cx, cy = dx + draw_w/2, dy + draw_h/2
            tr = QTransform()
            tr.translate(cx, cy); tr.rotate(180); tr.translate(-cx, -cy)
            painter.setTransform(tr, combine=False)
            painter.drawImage(QRectF(dx, dy, draw_w, draw_h), img, src_rect)
            painter.resetTransform()
        else:
            painter.drawImage(QRectF(dx, dy, draw_w, draw_h), img, src_rect)

    def _draw_fit(self, painter: QPainter, img, target_rect,
                  src_rect: QRectF=None, page_h_mm: float=297.0,
                  margins_mm=(0,0,0,0), scale: float=1.0,
                  rotate180: bool=False, extra_top_blank: float=0.0, extra_bottom_blank: float=0.0):
        """
        วาดแบบ fit-to-page + margins (mm) + Scale% + เผื่อช่องว่างบน/ล่าง (px)
        """
        if src_rect is None:
            src_rect = QRectF(0, 0, img.width(), img.height())

        # mm -> px ตามความสูงหน้ากระดาษจริง
        px_per_mm = target_rect.height() / page_h_mm
        ml, mt, mr, mb = margins_mm
        pad_left = ml * px_per_mm
        pad_right = mr * px_per_mm
        pad_top = mt * px_per_mm + extra_top_blank
        pad_bottom = mb * px_per_mm + extra_bottom_blank

        # พื้นที่วาดหลังหัก margins/gaps
        dest_x = target_rect.x() + pad_left
        dest_y = target_rect.y() + pad_top
        dest_w = target_rect.width() - (pad_left + pad_right)
        dest_h = target_rect.height() - (pad_top + pad_bottom)
        if dest_w <= 0 or dest_h <= 0:
            return  # margins ใหญ่เกิน

        # อัตราส่วน + scale%
        s_w, s_h = src_rect.width(), src_rect.height()
        base_scale = min(dest_w / s_w, dest_h / s_h)
        final_scale = base_scale * max(0.1, scale)

        # ไม่ให้ล้นขอบ (ถ้าผู้ใช้ใส่ Scale % สูงมาก)
        draw_w = min(dest_w, s_w * final_scale)
        draw_h = min(dest_h, s_h * final_scale)
        dx = dest_x + (dest_w - draw_w) / 2
        dy = dest_y + (dest_h - draw_h) / 2

        if rotate180:
            cx, cy = dx + draw_w/2, dy + draw_h/2
            tr = QTransform()
            tr.translate(cx, cy); tr.rotate(180); tr.translate(-cx, -cy)
            painter.setTransform(tr, combine=False)
            painter.drawImage(QRectF(dx, dy, draw_w, draw_h), img, src_rect)
            painter.resetTransform()
        else:
            painter.drawImage(QRectF(dx, dy, draw_w, draw_h), img, src_rect)

    def _print_fallback(self, printer_name: str):
        mode = self.mode_combo.currentIndex()
        if platform.system() == "Windows":
            sumatra = self._find_sumatra()
            paper = "A4" if mode == 0 else "A5"  # แนะนำตั้ง User Defined 210×148.5 ในไดรเวอร์สำหรับ half A4
            if sumatra and os.path.exists(sumatra):
                cmd = [
                    sumatra, "-print-to", printer_name,
                    "-print-settings", f"paper={paper},portrait,fit",
                    self.temp_pdf_path
                ]
                subprocess.run(cmd, check=True); return
            acro = self._find_acrobat()
            if acro and os.path.exists(acro):
                subprocess.run([acro, "/t", self.temp_pdf_path, printer_name], check=True); return
            os.startfile(self.temp_pdf_path)
            QMessageBox.information(self, "พิมพ์ผ่านแอปเริ่มต้น",
                                    "เปิดด้วยโปรแกรมเริ่มต้นแล้ว กรุณาเลือกขนาดกระดาษให้ตรง และ 1 page per sheet")
        else:
            media = "A4" if mode == 0 else "A5"
            subprocess.run([
                "lpr", "-P", printer_name,
                "-o", f"media={media}",
                "-o", "fit-to-page",
                "-o", "number-up=1",
                "-o", "sides=one-sided",
                self.temp_pdf_path
            ], check=True)

    @staticmethod
    def _find_sumatra():
        envs = [
            os.path.join(os.environ.get('PROGRAMFILES', r'C:\Program Files'), 'SumatraPDF', 'SumatraPDF.exe'),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'), 'SumatraPDF', 'SumatraPDF.exe'),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'SumatraPDF', 'SumatraPDF.exe'),
        ] + [os.path.join(p, 'SumatraPDF.exe') for p in os.environ.get('PATH', '').split(os.pathsep)]
        for c in envs:
            if c and os.path.exists(c): return c
        return None

    @staticmethod
    def _find_acrobat():
        pf = os.environ.get('PROGRAMFILES', r'C:\Program Files')
        pfx86 = os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)')
        pats = [
            os.path.join(pf, 'Adobe', 'Acrobat Reader*', 'Reader', 'AcroRd32.exe'),
            os.path.join(pfx86, 'Adobe', 'Acrobat Reader*', 'Reader', 'AcroRd32.exe'),
            os.path.join(pf, 'Adobe', 'Acrobat*', 'Acrobat', 'Acrobat.exe'),
            os.path.join(pfx86, 'Adobe', 'Acrobat*', 'Acrobat', 'Acrobat.exe'),
        ]
        for p in pats:
            m = glob.glob(p)
            if m:
                m.sort(reverse=True)
                return m[0]
        return None

    # ------------- misc helpers -------------
    def _browse_pdf_location(self):
        contract_type_name = "pawn_contract" if self.contract_type == 'pawn' else "redemption_contract"
        contract_number = self.contract_data.get('contract_number', 'unknown')
        default = f"{contract_type_name}_{contract_number}.pdf"
        path, _ = QFileDialog.getSaveFileName(self, "เลือกตำแหน่งบันทึกไฟล์ PDF", default, "PDF Files (*.pdf)")
        if path: self.pdf_path_edit.setText(path)

    def cleanup(self):
        try:
            if hasattr(self, 'pdf_document') and self.pdf_document: self.pdf_document.close()
        except: pass
        try:
            if self.temp_pdf_path and os.path.exists(self.temp_pdf_path): os.unlink(self.temp_pdf_path)
        except: pass

    def closeEvent(self, e):
        self.cleanup(); e.accept()


# ---------- helper ----------
def show_print_preview(parent, contract_type, pdf_generator_func,
                       contract_data, customer_data, product_data,
                       original_contract_data=None, shop_data=None, font_size_multiplier=None):
    dlg = PrintPreviewDialog(
        parent=parent, contract_type=contract_type,
        pdf_generator_func=pdf_generator_func,
        contract_data=contract_data, customer_data=customer_data,
        product_data=product_data, original_contract_data=original_contract_data,
        shop_data=shop_data, font_size_multiplier=font_size_multiplier
    )
    ok = dlg.exec_()
    dlg.cleanup()
    return ok == QDialog.Accepted