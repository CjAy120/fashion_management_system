import sys
import speech_recognition as sr
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtWidgets import QApplication


class VoiceListener(QThread):
    smafa_detected = pyqtSignal()

    def run(self):
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        print("Adjusting for background noise...")

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)

        print("Listening... Say 'hello'")

        while True:
            try:
                with mic as source:
                    audio = recognizer.listen(source)

                text = recognizer.recognize_google(audio).lower()
                print("Heard:", text)

                if "hello" in text:
                    print("SMAFA DETECTED!")
                    self.smafa_detected.emit()

            except Exception as e:
                print("Error:", e)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    listener = VoiceListener()

    # What happens when smafa is detected
    listener.smafa_detected.connect(
        lambda: print("Voice trigger working correctly!")
    )

    listener.start()

    sys.exit(app.exec())