import sys
import cv2
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QPropertyAnimation
import time
from core.sound_player import SoundPlayer
from core.hand_tracker import HandTracker


def convert_cv_qt(cv_img):
    """ Convert OpenCV image (BGR) into QImage (RGB) """
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    return QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)


class NeonBorder(QtWidgets.QFrame):
    """
    A QWidget subclass that draws an animated neon gradient border.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._angle = 0
        self.setAttribute(QtCore.Qt.WA_StyledBackground, True)
        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        self._anim = QPropertyAnimation(self, b"angle")
        self._anim.setDuration(3000)
        self._anim.setStartValue(0)
        self._anim.setEndValue(360)
        self._anim.setLoopCount(-1)
        self._anim.start()

    @QtCore.pyqtProperty(int)
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        gradient = QtGui.QConicalGradient(self.rect().center(), self._angle)
        gradient.setColorAt(0, QtGui.QColor(57, 255, 20, 180))
        gradient.setColorAt(0.5, QtGui.QColor(255, 0, 231, 180))
        gradient.setColorAt(1, QtGui.QColor(57, 255, 20, 180))
        pen = QtGui.QPen(QtGui.QBrush(gradient), 8)
        pen.setCapStyle(QtCore.Qt.RoundCap)
        painter.setPen(pen)
        rect = self.rect().adjusted(4, 4, -4, -4)
        painter.drawRoundedRect(rect, 20, 20)
        super().paintEvent(event)


class MainWindow(QtWidgets.QMainWindow):
    """
    Main application window with neon-styled video feed and status.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neon Guitar Player")
        self.resize(1280, 720)
        self.setStyleSheet("background-color: #0a0a0a;")

        central = QtWidgets.QWidget()
        self.setCentralWidget(central)
        layout = QtWidgets.QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        self.neon_frame = NeonBorder()
        neon_layout = QtWidgets.QVBoxLayout(self.neon_frame)
        neon_layout.setContentsMargins(4, 4, 4, 4)
        neon_layout.setSpacing(0)
        self.video_label = QtWidgets.QLabel()
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.video_label.setStyleSheet("background-color: #000; border-radius: 16px;")
        neon_layout.addWidget(self.video_label)
        layout.addWidget(self.neon_frame, stretch=1)

        self.status_label = QtWidgets.QLabel("Ready")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet(
            "color: #39FF14; font-size: 32px; font-weight: bold;"
        )
        glow = QtWidgets.QGraphicsDropShadowEffect(blurRadius=20, xOffset=0, yOffset=0)
        glow.setColor(QtGui.QColor(57, 255, 20))
        self.status_label.setGraphicsEffect(glow)
        layout.addWidget(self.status_label)

        footer = QtWidgets.QLabel(
            '<p style="color:white; font-weight: bold;">Created By Anirban Sarkar </p><a href="https://instagram.com/bong_ani_007" style="color: #39FF14;">@bong_ani_007</a>'
        )
        footer.setAlignment(QtCore.Qt.AlignCenter)
        footer.setStyleSheet("font-size: 14px; color: #666;")
        footer.setOpenExternalLinks(True)
        layout.addWidget(footer)

        self.tracker = HandTracker(max_hands=1)
        self.sound_player = SoundPlayer(sound_dir="assets/sounds")

        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            raise RuntimeError("Unable to access camera.")
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.last_fingers = None
        self.cooldown = 0.5
        self.last_time = 0

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def update_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return
        count, processed = self.tracker.process_frame(frame)
        self.status_label.setText(f"FINGERS: {count}")

        now = time.time()
        if self.last_fingers is None or self.last_fingers != count:
            if now - self.last_time > self.cooldown:
                self.sound_player.play_sound(count)
                self.last_time = now
            self.last_fingers = count

        qt_img = convert_cv_qt(processed)
        pixmap = QtGui.QPixmap.fromImage(qt_img).scaled(
            self.video_label.width(), self.video_label.height(),
            QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pixmap)

    def closeEvent(self, event):
        self.capture.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    pal = QtGui.QPalette()
    pal.setColor(QtGui.QPalette.Window, QtGui.QColor(10, 10, 10))
    pal.setColor(QtGui.QPalette.WindowText, QtGui.QColor(57, 255, 20))
    app.setPalette(pal)

    win = MainWindow()
    win.show()
    sys.exit(app.exec_())