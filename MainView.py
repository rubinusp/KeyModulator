# 1.Standard Modules
import logging
import sys

# 2. Extension Modules
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

# 3. Local Modules
from KeyModulator import KeyModulator

DEVELOP = True


class MainView(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        self.setWindowTitle("Key Modulator")
        self.resize(800, 850)
        self.setWindowFlags(Qt.Dialog | Qt.CustomizeWindowHint | Qt.WindowTitleHint)

        # Shifter Property
        self.keyModulator = KeyModulator(frame_len=12000, overlap=0.75)
        self.inFile = ""
        self.outFile = ""
        self.shift = 0

        # UI Components
        self.inputText = None
        self.fileText = None
        self.outputText = None
        self.openButton = None
        self.outputTextEdit = None

        self.keyText = None
        self.keySlider = None
        self.shiftText = None
        self.buttonBox = None

        self.progressTextEdit = None
        self.proc = None

        # Logger
        self.logger = None

        self._setup_ui()
        self._setup_logger()

    class LogHandler(logging.Handler):
        def __init__(self, parent):
            super().__init__()

            self.parent = parent
        
        def emit(self, record):
            self.parent.progressTextEdit.append(record.getMessage())
            self.parent.progressTextEdit.repaint()

    def _setup_logger(self):

        self.logger = logging.getLogger("KeyModulator")
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(self.LogHandler(self))

    def _setup_ui(self):

        # IO Component
        self.inputText = QLabel("Input File: ")
        self.outputText = QLabel("Name: ")

        self.fileText = QLabel("...")

        self.openButton = QPushButton("Open")
        self.openButton.clicked.connect(self._open)

        self.outputTextEdit = QLineEdit()
        self.outputTextEdit.setAlignment(Qt.AlignCenter)

        ioGrid = QGridLayout()
        ioGrid.addWidget(self.inputText, 0, 0)
        ioGrid.addWidget(self.fileText, 0, 1)
        ioGrid.addWidget(self.openButton, 0, 2)
        ioGrid.addWidget(self.outputText, 1, 0)
        ioGrid.addWidget(self.outputTextEdit, 1, 1, 1, 1)

        ioGroupBox = QGroupBox("Input/Output")
        ioGroupBox.setLayout(ioGrid)

        self.keyText = QLabel("Key: ")
        self.keySlider = QSlider(Qt.Horizontal)
        self.keySlider.setMinimum(-7)
        self.keySlider.setMaximum(7)
        self.keySlider.setSingleStep(1)     # Using arrow key
        self.keySlider.setPageStep(1)
        self.keySlider.setTickPosition(self.shift)
        self.keySlider.valueChanged.connect(self._set_key_shift)

        self.shiftText = QLabel(str(self.shift))
        self.shiftText.setAlignment(Qt.AlignCenter)

        controlLayout = QGridLayout()
        controlLayout.addWidget(self.keyText, 0, 0)
        controlLayout.addWidget(self.keySlider, 1, 0)
        controlLayout.addWidget(self.shiftText, 1, 1)

        controlGroupBox = QGroupBox("Control")
        controlGroupBox.setLayout(controlLayout)

        self.progressTextEdit = QTextEdit()
        self.progressTextEdit.resize(self.progressTextEdit.width(), 200)

        # Create standard button box
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, Qt.Horizontal)

        # Add button signal
        self.buttonBox.accepted.connect(self._shift)
        self.buttonBox.rejected.connect(self.reject)

        # configure dialog layout
        mainLayout = QVBoxLayout()
        mainLayout.addWidget(ioGroupBox)
        mainLayout.addWidget(controlGroupBox)
        mainLayout.addWidget(self.progressTextEdit)
        mainLayout.addWidget(self.buttonBox)

        # Set dialog layout
        self.setLayout(mainLayout)

        if DEVELOP:
            self.keySlider.setTickPosition(-5)
            self.outputTextEdit.setText("homura_instrumental_-5")

    def _set_key_shift(self):

        try:
            self.shift = self.keySlider.sliderPosition()
            self.shiftText.setText(str(self.shift))
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowModality(Qt.WindowModal)
            msg.setText(str(e))
            msg.exec_()

    def _shift(self):

        try:
            self.progressTextEdit.clear()

            self.outFile = f"{self.outputTextEdit.text()}.wav"
            self.keyModulator.read(self.inFile)
            self.keyModulator.shift(self.shift)
            self.keyModulator.write(self.outFile)
            self._on_success()
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowModality(Qt.WindowModal)
            msg.setText(str(e))
            msg.exec_()

    def _open(self):

        # save unsaved changes if needed
        try:
            file, format = QFileDialog.getOpenFileName(self)
            if file != "":
                self.fileText.setText(f"...{file[-15:]}")
                self.inFile = file
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowModality(Qt.WindowModal)
            msg.setText(str(e))
            msg.exec_()

    def _on_success(self):
        return


def main():

    app = QApplication(sys.argv)
    QCoreApplication.setOrganizationName("Gordon Poon")
    QCoreApplication.setApplicationName("Key Modulator")

    main_view = MainView()
    main_view.show()
    app.exec_()


if __name__ == "__main__":
    main()