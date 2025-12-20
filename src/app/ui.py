import sys
from pathlib import Path
from src.pipeline.pipeline_runner import run_pipeline_from_ui
from PySide6.QtWidgets import QProgressBar

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
)
from PySide6.QtCore import Qt
from PySide6.QtCore import QThread, Signal


class PipelineWorker(QThread):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int, int, str)

    def __init__(self, input_video):
        super().__init__()
        self.input_video = input_video

    def run(self):
        try:
            run_pipeline_from_ui(
                self.input_video,
                progress_callback=self.emit_progress,
            )
        except Exception as e:
            print(">>> PIPELINE ERROR <<<", flush=True)
            print(e, flush=True)
            self.error.emit(str(e))
            return
        
        self.finished.emit()

    def emit_progress(self, step: int, total: int, message: str):
        self.progress.emit(step, total, message)


class VODEngineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VOD-Engine")
        self.setMinimumSize(800, 500)

        self.selected_video: Path | None = None

        # UI elements
        self.title_label = QLabel("VOD-Engine", self)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.file_label = QLabel("No video selected", self)
        self.file_label.setAlignment(Qt.AlignCenter)
        self.file_label.setWordWrap(True)

        self.pick_button = QPushButton("Select VOD (.mp4)", self)
        self.pick_button.clicked.connect(self.open_file_picker)


        self.start_button = QPushButton("Start Highlight Generation", self)
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_pipeline)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)

        # Layout
        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addSpacing(20)
        layout.addWidget(self.file_label)
        layout.addSpacing(20)
        layout.addWidget(self.pick_button, alignment=Qt.AlignCenter)
        layout.addStretch()
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def open_file_picker(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select VOD",
            "",
            "Video Files (*.mp4)",
        )

        if not file_path:
            return

        self.selected_video = Path(file_path)
        self.file_label.setText(f"Selected:\n{self.selected_video}")
        self.start_button.setEnabled(True)

    
    def start_pipeline(self):
        if not self.selected_video:
            return

        self.start_button.setEnabled(False)
        self.pick_button.setEnabled(False)
        self.file_label.setText("Processing… check console/logs for progress")

        self.worker = PipelineWorker(self.selected_video)
        self.worker.finished.connect(self.pipeline_finished)
        self.worker.error.connect(self.pipeline_error)
        self.worker.progress.connect(self.update_progress)
        self.worker.start()

    def pipeline_finished(self):
        self.file_label.setText("✅ Highlight generation complete")
        self.pick_button.setEnabled(True)
        self.start_button.setEnabled(True)

    def pipeline_error(self, message: str):
        self.file_label.setText(f"❌ Error:\n{message}")
        self.pick_button.setEnabled(True)
        self.start_button.setEnabled(True)

    def update_progress(self, step: int, total: int, message: str):
        percent = int((step / total) * 100)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(percent)
        self.file_label.setText(message)

        QApplication.processEvents()

    def pipeline_finished(self):
        self.progress_bar.setValue(100)
        self.file_label.setText("✅ Highlight generation complete")
        self.pick_button.setEnabled(True)
        self.start_button.setEnabled(True)

    def pipeline_error(self, message: str):
        self.progress_bar.setVisible(False)
        self.file_label.setText(f"❌ Error:\n{message}")
        self.pick_button.setEnabled(True)
        self.start_button.setEnabled(True)


def run():
    app = QApplication(sys.argv)
    window = VODEngineWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
