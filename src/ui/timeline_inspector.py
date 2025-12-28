import json
import subprocess
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel
)
from PySide6.QtCore import Qt

from infra.config import OUTPUT_DIR, DATA_DIR


class TimelineInspector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timeline Inspector")
        self.resize(900, 600)

        timeline_path = OUTPUT_DIR / "timeline.json"
        if not timeline_path.exists():
            raise RuntimeError("timeline.json not found. Run pipeline first.")

        self.timeline = json.loads(timeline_path.read_text())

        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.detail = QLabel("Select a row to inspect")
        layout.addWidget(self.detail)

        self.open_btn = QPushButton("Open Clip")
        self.open_btn.clicked.connect(self.open_clip)
        layout.addWidget(self.open_btn)

        self.populate_table()

    def populate_table(self):
        headers = ["#", "Time", "A", "T", "C", "F"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.timeline))

        for row, entry in enumerate(self.timeline):
            self.table.setItem(row, 0, QTableWidgetItem(str(row)))
            self.table.setItem(
                row, 1,
                QTableWidgetItem(
                    f'{self._fmt(entry["start_sec"])}–{self._fmt(entry["end_sec"])}'
                )
            )
            self.table.setItem(row, 2, QTableWidgetItem(f'{entry["audio"]:.2f}'))
            self.table.setItem(row, 3, QTableWidgetItem(f'{entry["text"]:.2f}'))
            self.table.setItem(row, 4, QTableWidgetItem(f'+{entry["chat"]:.2f}'))
            self.table.setItem(row, 5, QTableWidgetItem(f'{entry["final"]:.2f}'))

            if entry["highlight"]:
                for col in range(6):
                    self.table.item(row, col).setBackground(Qt.yellow)

        self.table.selectionModel().selectionChanged.connect(
            self.on_row_selected
        )

    def on_row_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return
        entry = self.timeline[row]
        self.detail.setText(
            f"Reason: {entry.get('reason', '—')}"
        )

    def open_clip(self):
        row = self.table.currentRow()
        if row < 0:
            return

        clip = DATA_DIR / "output" / "clips" / f"highlight_{row:03d}.mp4"
        if clip.exists():
            subprocess.Popen([str(clip)], shell=True)

    @staticmethod
    def _fmt(sec: int) -> str:
        return f"{sec // 60:02d}:{sec % 60:02d}"
