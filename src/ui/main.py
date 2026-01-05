import sys
import traceback
from enum import Enum
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QFileDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QRadioButton,
    QButtonGroup,
    QProgressBar,
    QCheckBox,
    QSlider,
    QInputDialog,
    QComboBox
)


from PySide6.QtCore import Qt, QThread, Signal

from pipeline.pipeline_runner import run_pipeline_from_ui
from ui.timeline_inspector import TimelineInspector
from infra.config import PRESETS_DIR
from scoring.presets import load_preset
from scoring.presets import save_preset

from ui.input_modes import InputMode


# ─────────────────────────────────────────────
# Background worker
# ─────────────────────────────────────────────

class PipelineWorker(QThread):
    finished = Signal()
    error = Signal(str)
    progress = Signal(int, int, str)

    def __init__(
        self,
        input_value,
        input_mode: InputMode,
        chat_enabled: bool,
        chat_weight: float,
    ):
        super().__init__()
        self.input_value = input_value
        self.input_mode = input_mode
        self.chat_enabled = chat_enabled
        self.chat_weight = chat_weight

    def run(self):
        try:
            run_pipeline_from_ui(
                input_value=self.input_value,
                input_mode=self.input_mode,
                chat_enabled=self.chat_enabled,
                chat_weight=self.chat_weight,
                progress_callback=self.emit_progress,
            )
        except Exception:
            tb = traceback.format_exc()
            print(">>> PIPELINE ERROR <<<")
            print(tb)
            self.error.emit(tb)
            return

        self.finished.emit()

    def emit_progress(self, step: int, total: int, message: str):
        self.progress.emit(step, total, message)


# ─────────────────────────────────────────────
# Main window
# ─────────────────────────────────────────────

class VODEngineWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("VOD-Engine")
        self.setMinimumSize(800, 520)

        self.input_mode = InputMode.LOCAL
        self.selected_video: Path | None = None

        # ─── UI elements ───────────────────────

        self.title_label = QLabel("VOD-Engine")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 24px; font-weight: bold;")

        self.status_label = QLabel("Select an input to begin")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)

        # Input mode radios
        self.radio_local = QRadioButton("Local Video")
        self.radio_url = QRadioButton("Twitch URL")
        self.radio_id = QRadioButton("Twitch VOD ID")
        self.radio_local.setChecked(True)

        self.radio_group = QButtonGroup(self)
        self.radio_group.addButton(self.radio_local)
        self.radio_group.addButton(self.radio_url)
        self.radio_group.addButton(self.radio_id)

        self.radio_local.toggled.connect(lambda: self.set_input_mode(InputMode.LOCAL))
        self.radio_url.toggled.connect(lambda: self.set_input_mode(InputMode.TWITCH_URL))
        self.radio_id.toggled.connect(lambda: self.set_input_mode(InputMode.TWITCH_ID))
        
        # Inputs
        self.pick_button = QPushButton("Select .mp4 file")
        self.pick_button.clicked.connect(self.open_file_picker)

        self.twitch_url_input = QLineEdit()
        self.twitch_url_input.setPlaceholderText("https://www.twitch.tv/videos/…")
        self.twitch_url_input.setVisible(False)
        self.twitch_url_input.textChanged.connect(self.update_start_enabled)

        self.twitch_id_input = QLineEdit()
        self.twitch_id_input.setPlaceholderText("2650407881")
        self.twitch_id_input.setVisible(False)
        self.twitch_id_input.textChanged.connect(self.update_start_enabled)

        self.preset_dropdown = QComboBox()
        self.preset_dropdown.addItem("— No preset —")

        for p in PRESETS_DIR.glob("*.json"):
            self.preset_dropdown.addItem(p.stem)

        self.load_preset_button = QPushButton("Load Preset")
        self.save_preset_button = QPushButton("Save Preset")

        self.load_preset_button.clicked.connect(self.load_selected_preset)
        self.save_preset_button.clicked.connect(self.save_current_preset)


        # Action buttons
        self.start_button = QPushButton("Start Highlight Generation")
        self.start_button.setEnabled(False)
        self.start_button.clicked.connect(self.start_pipeline)

        self.chat_checkbox = QCheckBox("Enable chat influence")
        self.chat_checkbox.setChecked(True)

        self.timeline_button = QPushButton("View Timeline")
        self.timeline_button.setEnabled(False)
        self.timeline_button.clicked.connect(self.open_timeline)

        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)

        # SLider
        self.chat_weight_label = QLabel("Chat weight: 1.00")

        self.chat_weight_slider = QSlider(Qt.Horizontal)
        self.chat_weight_slider.setMinimum(0)
        self.chat_weight_slider.setMaximum(200)
        self.chat_weight_slider.setValue(100)  # 1.0
        self.chat_weight_slider.setTickInterval(25)
        self.chat_weight_slider.setTickPosition(QSlider.TicksBelow)

        

        self.chat_weight_slider.valueChanged.connect(
            lambda v: self.chat_weight_label.setText(f"Chat weight: {v/100:.2f}")
        )

        # ─── Layout ────────────────────────────

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.radio_local)
        radio_layout.addWidget(self.radio_url)
        radio_layout.addWidget(self.radio_id)

        layout = QVBoxLayout()
        layout.addStretch()
        layout.addWidget(self.title_label)
        layout.addSpacing(16)
        layout.addWidget(self.status_label)
        layout.addSpacing(12)
        layout.addLayout(radio_layout)
        layout.addWidget(self.pick_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.twitch_url_input)
        layout.addWidget(self.twitch_id_input)
        layout.addSpacing(20)
        layout.addWidget(self.chat_checkbox, alignment=Qt.AlignCenter)
        layout.addWidget(self.chat_weight_label, alignment=Qt.AlignCenter)
        layout.addWidget(self.chat_weight_slider)
        layout.addWidget(self.start_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.timeline_button, alignment=Qt.AlignCenter)
        layout.addWidget(self.progress_bar)
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(self.preset_dropdown)
        preset_layout.addWidget(self.load_preset_button)
        preset_layout.addWidget(self.save_preset_button)

        layout.addLayout(preset_layout)

        layout.addStretch()

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    # ─────────────────────────────────────────
    # UI logic
    # ─────────────────────────────────────────

    def set_input_mode(self, mode: InputMode):
        self.input_mode = mode
        self.selected_video = None

        self.pick_button.setVisible(mode == InputMode.LOCAL)
        self.twitch_url_input.setVisible(mode == InputMode.TWITCH_URL)
        self.twitch_id_input.setVisible(mode == InputMode.TWITCH_ID)

        self.start_button.setEnabled(False)
        self.status_label.setText("Select an input to begin")

    def update_start_enabled(self):
        if self.input_mode == InputMode.TWITCH_URL:
            self.start_button.setEnabled(bool(self.twitch_url_input.text().strip()))
        elif self.input_mode == InputMode.TWITCH_ID:
            self.start_button.setEnabled(self.twitch_id_input.text().isdigit())

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
        self.status_label.setText(f"Selected:\n{self.selected_video}")
        self.start_button.setEnabled(True)

    def on_chat_weight_change(self, value):
        weight = value / 100.0
        self.chat_weight_label.setText(f"Chat weight: {weight:.2f}")

    def load_selected_preset(self):
        name = self.preset_dropdown.currentText()
        if not name or name == "— No preset —":
            return

        preset = load_preset(name)

        # Sync UI from preset
        self.chat_checkbox.setChecked(preset["enable_chat_influence"])
        self.chat_weight_slider.setValue(int(preset["chat_weight"] * 100))

        self.status_label.setText(f"Loaded preset: {name}")



    def save_current_preset(self):
        name, ok = QInputDialog.getText(self, "Save Preset", "Preset name:")
        if not ok or not name:
            return

        # Sync UI → config
        import infra.config as config
        config.ENABLE_CHAT_INFLUENCE = self.chat_checkbox.isChecked()
        config.CHAT_WEIGHT = self.chat_weight_slider.value() / 100.0

        save_preset(name)
        print("here")

        # 🔹 Update dropdown if new
        if self.preset_dropdown.findText(name) == -1:
            self.preset_dropdown.addItem(name)
            self.preset_dropdown.setCurrentText(name)

        self.status_label.setText(f"Preset '{name}' saved")


    # ─────────────────────────────────────────
    # Pipeline control
    # ─────────────────────────────────────────

    def start_pipeline(self):
        if self.input_mode == InputMode.LOCAL:
            input_value = self.selected_video
        elif self.input_mode == InputMode.TWITCH_URL:
            input_value = self.twitch_url_input.text().strip()
        else:
            input_value = self.twitch_id_input.text().strip()

        chat_enabled = self.chat_checkbox.isChecked()
        chat_weight = self.chat_weight_slider.value() / 100.0

        self.start_button.setEnabled(False)
        self.timeline_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_label.setText("Processing…")

        self.worker = PipelineWorker(
            input_value=input_value,
            input_mode=self.input_mode,
            chat_enabled=chat_enabled,
            chat_weight=chat_weight,
        )

        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.pipeline_finished)
        self.worker.error.connect(self.pipeline_error)
        self.worker.start()

    def update_progress(self, step: int, total: int, message: str):
        percent = int((step / total) * 100)
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
        QApplication.processEvents()

    def pipeline_finished(self):
        self.progress_bar.setValue(100)
        self.status_label.setText("✅ Highlight generation complete")
        self.start_button.setEnabled(True)
        self.timeline_button.setEnabled(True)

    def pipeline_error(self, message: str):
        self.progress_bar.setVisible(False)
        self.status_label.setText(f"❌ Error:\n{message}")
        self.start_button.setEnabled(True)

    

    # ─────────────────────────────────────────
    # Timeline
    # ─────────────────────────────────────────

    def open_timeline(self):
        self.timeline_window = TimelineInspector()
        self.timeline_window.show()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def run():
    app = QApplication(sys.argv)
    window = VODEngineWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
