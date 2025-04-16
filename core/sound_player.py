import os
import pygame
import sys

class SoundPlayer:
    def __init__(self, sound_dir="assets/sounds"):
        # Handle PyInstaller temp extraction
        if hasattr(sys, '_MEIPASS'):
            base_path = os.path.join(sys._MEIPASS, sound_dir)
        else:
            base_path = sound_dir

        self.sound_dir = base_path
        pygame.mixer.init()

        self.note_sounds = {
            0: os.path.join(self.sound_dir, "c.wav"),
            1: os.path.join(self.sound_dir, "a.wav"),
            2: os.path.join(self.sound_dir, "c.wav"),
            3: os.path.join(self.sound_dir, "e.wav"),
            4: os.path.join(self.sound_dir, "f.wav"),
            5: os.path.join(self.sound_dir, "g.wav")
        }

        self.sounds = {}

        for key, path in self.note_sounds.items():
            if os.path.exists(path):
                self.sounds[key] = pygame.mixer.Sound(path)
            else:
                self.sounds[key] = None
                print(f"Sound file {path} not found.")

    def play_sound(self, finger_count):
        sound = self.sounds.get(finger_count)
        if sound:
            sound.play()
        else:
            print(f"No sound available for finger count: {finger_count}")
