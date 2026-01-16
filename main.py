import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLabel, QSpinBox, QGroupBox, QMainWindow)
from PyQt5.QtCore import Qt, QTimer, QRectF, QPointF
from PyQt5.QtGui import QPainter, QColor, QPen, QPainterPath, QLinearGradient, QBrush, QFont

# ==========================================
# 1. Klasa Zbiornik
# ==========================================
class Zbiornik(QWidget):
    def __init__(self, nazwa, kolor, capacity=100, label_pos='top', parent=None):
        super().__init__(parent)
        self.nazwa = nazwa
        self.kolor_cieczy = kolor
        self.capacity = capacity
        self.label_pos = label_pos
        self.poziom = 0.0

        if self.label_pos == 'right':
            self.setFixedSize(240, 160)
            self.cx_offset = 60
            self.margin_top = 25
        else:
            self.setFixedSize(120, 180)
            self.cx_offset = 60
            self.margin_top = 45

        self.top_h = 20
        self.body_h = 60
        self.bot_h = 20
        self.width_top = 100
        self.width_body = 80
        self.width_bot = 40
        
        self.draw_y = self.margin_top 
        self.total_h = self.top_h + self.body_h + self.bot_h

    def setLevel(self, val):
        fraction = val / self.capacity
        self.poziom = max(0.0, min(1.0, fraction))
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        cx = self.cx_offset
        y = self.draw_y

        # NAPIS
        painter.setPen(Qt.white)
        font = painter.font()
        font.setBold(True)
        font.setPointSize(9)
        painter.setFont(font)
        text_str = f"{self.nazwa} ({int(self.poziom * self.capacity)}L)"

        if self.label_pos == 'right':
            text_rect = QRectF(120, y, 110, self.total_h)
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, text_str)
        else:
            text_rect = QRectF(0, 0, self.width(), self.margin_top - 5)
            painter.drawText(text_rect, Qt.AlignCenter, text_str)

        # KSZTAŁT
        path = QPainterPath()
        p1 = QPointF(cx - self.width_top/2, y)
        p2 = QPointF(cx + self.width_top/2, y)
        p3 = QPointF(cx + self.width_body/2, y + self.top_h)
        p4 = QPointF(cx + self.width_body/2, y + self.top_h + self.body_h)
        p5 = QPointF(cx + self.width_bot/2, y + self.total_h)
        p6 = QPointF(cx - self.width_bot/2, y + self.total_h)
        p7 = QPointF(cx - self.width_body/2, y + self.top_h + self.body_h)
        p8 = QPointF(cx - self.width_body/2, y + self.top_h)

        path.moveTo(p1); path.lineTo(p2); path.lineTo(p3); path.lineTo(p4)
        path.lineTo(p5); path.lineTo(p6); path.lineTo(p7); path.lineTo(p8)
        path.closeSubpath()

        # CIECZ
        painter.save()
        painter.setClipPath(path)
        if self.poziom > 0:
            liquid_h = self.total_h * self.poziom
            rect_liquid = QRectF(0, y + self.total_h - liquid_h, self.width(), liquid_h)
            grad = QLinearGradient(rect_liquid.topLeft(), rect_liquid.topRight())
            grad.setColorAt(0, self.kolor_cieczy.darker(130))
            grad.setColorAt(0.5, self.kolor_cieczy)
            grad.setColorAt(1, self.kolor_cieczy.darker(130))
            painter.fillRect(rect_liquid, grad)
        painter.restore()

        # OBRYS
        pen = QPen(QColor(160, 160, 160), 3)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def get_outlet_pos(self):
        return (self.x() + self.cx_offset, self.y() + self.draw_y + self.total_h)

    def get_inlet_pos(self):
        return (self.x() + self.cx_offset, self.y() + self.draw_y)
    
    def get_inlet_pos_offset(self, offset_x):
        return (self.x() + self.cx_offset + offset_x, self.y() + self.draw_y)

# ==========================================
# 2. Klasa Rura
# ==========================================
class Rura(QWidget):
    def __init__(self, punkty, parent=None):
        super().__init__(parent)
        self.punkty = punkty
        self.active = False
        self.setAttribute(Qt.WA_TransparentForMouseEvents)

    def setActive(self, state):
        if self.active != state:
            self.active = state
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        color = QColor(0, 200, 255) if self.active else QColor(80, 80, 80)
        width = 5 if self.active else 3
        
        path = QPainterPath()
        if self.punkty:
            path.moveTo(self.punkty[0][0], self.punkty[0][1])
            for p in self.punkty[1:]:
                path.lineTo(p[0], p[1])
            
        painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        painter.drawPath(path)

# ==========================================
# 3. Elementy Dynamiczne
# ==========================================
class Mieszadlo(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(80, 130) 
        self.running = False
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate)

    def setRunning(self, state):
        self.running = state
        if state: self.timer.start(30)
        else: self.timer.stop()
        self.update()

    def animate(self):
        self.angle = (self.angle + 20) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        cx = self.width() / 2
        
        # 1. Silnik
        painter.setBrush(QBrush(QColor(100, 100, 100)))
        painter.setPen(QPen(Qt.black, 1))
        painter.drawRect(int(cx - 15), 0, 30, 20)
        
        # 2. Wał
        painter.setPen(QPen(QColor(200, 200, 200), 4))
        pivot_y = 100
        painter.drawLine(int(cx), 20, int(cx), pivot_y)

        # 3. Śmigło (Krzyżak)
        painter.save()
        painter.translate(cx, pivot_y) 
        painter.rotate(self.angle)
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(Qt.yellow)
        
        length = 40
        thickness = 8
        painter.drawRect(int(-length/2), int(-thickness/2), length, thickness)
        painter.drawRect(int(-thickness/2), int(-length/2), thickness, length)
        
        painter.setBrush(Qt.black)
        painter.drawEllipse(QPointF(0, 0), 4, 4)
        
        painter.restore()


# ==========================================
# 4. Główne Okno SCADA
# ==========================================
class ScadaWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Projekt Informatyka II - SCADA")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #1e1e1e; color: white;")
        
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # PANEL
        control_panel = QGroupBox("Parametry Początkowe")
        control_panel.setMaximumHeight(60) 
        control_panel.setStyleSheet("QGroupBox { background: #2d2d2d; border-bottom: 2px solid #444; font-weight: bold; } QLabel { color: #ddd; }")
        
        hlay = QHBoxLayout()
        hlay.setContentsMargins(10, 5, 10, 5)
        
        input_style = "QSpinBox { background: white; color: black; font-weight: bold; padding: 2px; }"
        self.spinA = QSpinBox(); self.spinA.setRange(0, 100); self.spinA.setValue(80); self.spinA.setStyleSheet(input_style)
        self.spinB = QSpinBox(); self.spinB.setRange(0, 100); self.spinB.setValue(60); self.spinB.setStyleSheet(input_style)
        
        self.btnStart = QPushButton("START PROCESU")
        self.btnStart.setStyleSheet("""
            QPushButton { background-color: #0078d7; color: white; font-weight: bold; border-radius: 4px; padding: 6px; }
            QPushButton:disabled { background-color: #555; color: #aaa; }
            QPushButton:hover { background-color: #008aff; }
        """)
        self.btnStart.clicked.connect(self.start_simulation)
        
        hlay.addWidget(QLabel("Zbiornik A:"))
        hlay.addWidget(self.spinA)
        hlay.addSpacing(30)
        hlay.addWidget(QLabel("Zbiornik B:"))
        hlay.addWidget(self.spinB)
        hlay.addSpacing(30)
        hlay.addWidget(self.btnStart)
        control_panel.setLayout(hlay)
        layout.addWidget(control_panel)
        
        # KANWA
        self.canvas = QWidget()
        self.canvas.setStyleSheet("background-color: #1e1e1e;")
        layout.addWidget(self.canvas)
        
        self.init_layout_objects()
        
        self.logic_timer = QTimer()
        self.logic_timer.timeout.connect(self.process_logic)
        self.state = "IDLE"

    def init_layout_objects(self):
        # 1. Górne
        self.tankA = Zbiornik("Substrat A", QColor(255, 60, 60), label_pos='top', parent=self.canvas)
        self.tankA.move(60, 5) 
        self.tankB = Zbiornik("Substrat B", QColor(60, 100, 255), label_pos='top', parent=self.canvas)
        self.tankB.move(620, 5)

        # 2. Mieszalnik (Środek)
        self.tankMix = Zbiornik("Mieszalnik", QColor(200, 50, 200), capacity=200, label_pos='right', parent=self.canvas)
        self.tankMix.move(340, 200) 
        
        # 3. Mieszadło
        self.mixer = Mieszadlo(parent=self.canvas)
        self.mixer.move(360, 195) 

        # 4. Produkt (Dół)
        self.tankProd = Zbiornik("Produkt", QColor(40, 200, 40), capacity=200, label_pos='right', parent=self.canvas)
        self.tankProd.move(340, 400) 

        # --- RURY ---
        outA = self.tankA.get_outlet_pos()
        outB = self.tankB.get_outlet_pos()
        
        inMix_Left = self.tankMix.get_inlet_pos_offset(-40) 
        inMix_Right = self.tankMix.get_inlet_pos_offset(40)
        
        outMix = self.tankMix.get_outlet_pos()
        inProd = self.tankProd.get_inlet_pos_offset(0)

        pipe_level_y = 180

        # Rura A
        pts_A = [outA, (outA[0], pipe_level_y), (inMix_Left[0], pipe_level_y), inMix_Left]
        self.pipeA = Rura(pts_A, self.canvas)
        self.pipeA.resize(800, 600)

        # Rura B
        pts_B = [outB, (outB[0], pipe_level_y), (inMix_Right[0], pipe_level_y), inMix_Right]
        self.pipeB = Rura(pts_B, self.canvas)
        self.pipeB.resize(800, 600)

        # Rura Out
        pts_Out = [outMix, inProd]
        self.pipeOut = Rura(pts_Out, self.canvas)
        self.pipeOut.resize(800, 600)

    def start_simulation(self):
        valA = self.spinA.value()
        valB = self.spinB.value()
        self.tankA.setLevel(valA); self.tankB.setLevel(valB)
        self.tankMix.setLevel(0); self.tankProd.setLevel(0)
        self.state = "FILLING"
        self.current_A = valA; self.current_B = valB; self.current_Mix = 0; self.current_Prod = 0
        self.logic_timer.start(50)
        self.btnStart.setEnabled(False)
        self.spinA.setEnabled(False); self.spinB.setEnabled(False)

    def process_logic(self):
        rate = 0.5
        
        if self.state == "FILLING":
            self.pipeA.setActive(True); self.pipeB.setActive(True)
            pumps_working = False
            
            if self.current_A > 0: self.current_A -= rate; self.current_Mix += rate; pumps_working = True
            if self.current_B > 0: self.current_B -= rate; self.current_Mix += rate; pumps_working = True
            
            self.tankA.setLevel(self.current_A); self.tankB.setLevel(self.current_B); self.tankMix.setLevel(self.current_Mix)
            
            if not pumps_working:
                self.state = "MIXING"; self.mix_timer = 0
                self.pipeA.setActive(False); self.pipeB.setActive(False)
        
        elif self.state == "MIXING":
            self.mixer.setRunning(True)
            self.mix_timer += 1
            if self.mix_timer % 10 == 0: self.tankMix.kolor_cieczy = self.tankMix.kolor_cieczy.lighter(105); self.tankMix.update()
            
            if self.mix_timer > 60: 
                self.state = "EMPTYING"; self.mixer.setRunning(False)
        
        elif self.state == "EMPTYING":
            self.pipeOut.setActive(True)
            if self.current_Mix > 0:
                self.current_Mix -= (rate * 2); self.current_Prod += (rate * 2)
                self.tankMix.setLevel(self.current_Mix); self.tankProd.setLevel(self.current_Prod)
            else:
                self.state = "DONE"; self.pipeOut.setActive(False); self.logic_timer.stop()
                self.btnStart.setEnabled(True); self.spinA.setEnabled(True); self.spinB.setEnabled(True)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ScadaWindow()
    window.show()
    sys.exit(app.exec())