import sys
import os
import cv2
import time
import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets

from core.sound_player import SoundPlayer
from core.hand_tracker import HandTracker

def convert_cv_qt(cv_img):
    """ Convert an OpenCV image (BGR) into QImage (RGB) """
    rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    h, w, ch = rgb_image.shape
    bytes_per_line = ch * w
    q_img = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
    return q_img

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Neon Guitar Player")
        self.setGeometry(100, 100, 1280, 720)
        
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.video_label = QtWidgets.QLabel(self)
        self.video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.video_label)
        
        self.status_label = QtWidgets.QLabel("Ready", self)
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 24px; color: #39FF14;")
        self.layout.addWidget(self.status_label)
        
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
            QLabel {
                color: #39FF14;
            }
        """)
        
        self.tracker = HandTracker(max_hands=1)
        self.sound_player = SoundPlayer(sound_dir="assets/sounds")
        
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            raise RuntimeError("Error: Unable to access the camera.")
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # For debouncing sound playback
        self.last_finger_count = None
        self.sound_cooldown = 0.5  
        self.last_sound_time = 0
        
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  
        
    def update_frame(self):
        ret, frame = self.capture.read()
        if not ret:
            return

        finger_count, processed_frame = self.tracker.process_frame(frame)

        self.status_label.setText(f"Fingers: {finger_count}")

        if self.last_finger_count is None or self.last_finger_count != finger_count:
            self.sound_player.play_sound(finger_count)
            self.last_finger_count = finger_count

        qt_img = convert_cv_qt(processed_frame)
        pixmap = QtGui.QPixmap.fromImage(qt_img)
        self.video_label.setPixmap(pixmap)

        
    def closeEvent(self, event):
        self.capture.release()
        event.accept()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
