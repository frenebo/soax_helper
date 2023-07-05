
from PyQt6.QtWidgets import (
    QMainWindow,
)

class MainWindow(QMainWindow):
    def __init__(self, workdir, useStandIns=False):
        super().__init__()

        self.setWindowTitle("Dmd Acquisition Tool")

        topVLayout = QVBoxLayout()
        topLevelVWidget = QWidget()
        topLevelVWidget.setLayout(topVLayout)

        self.setCentralWidget(topLevelVWidget)