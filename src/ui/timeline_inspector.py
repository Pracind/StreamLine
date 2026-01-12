import json
import os
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QCheckBox
)
from PySide6.QtCore import Qt

from infra.config import DATA_DIR
from highlights.highlight_merger import TIMELINE_PATH


class TimelineInspector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Timeline Inspector")
        self.resize(900, 600)

        self.timeline_path = TIMELINE_PATH
        if not self.timeline_path.exists():
            raise RuntimeError("timeline.json not found. Run pipeline first.")

        raw = json.loads(self.timeline_path.read_text(encoding="utf-8"))

        # Handle v2 timeline schema
        if isinstance(raw, dict) and "timeline" in raw:
            self.timeline = raw["timeline"]
        else:
            self.timeline = raw

        # UI
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.detail = QLabel("Select a row to inspect")
        layout.addWidget(self.detail)

        self.open_btn = QPushButton("Open Clip")
        self.open_btn.clicked.connect(self.open_clip)
        layout.addWidget(self.open_btn)

        self.populate_table()

    # ----------------------------
    # Table
    # ----------------------------

    def populate_table(self):
        self.table.clear()

        headers = ["#", "Time", "Enabled"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.timeline))

        for row, entry in enumerate(self.timeline):
            # Index
            self.table.setItem(row, 0, QTableWidgetItem(str(row + 1)))

            # Time range
            time_item = QTableWidgetItem(
                f'{self._fmt(entry["start_time"])}–{self._fmt(entry["end_time"])}'
            )
            self.table.setItem(row, 1, time_item)

            # Enabled checkbox
            enabled = entry.get("enabled", True)
            checkbox = QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(
                partial(self.on_enabled_toggled, row)
            )
            self.table.setCellWidget(row, 2, checkbox)

        self.table.selectionModel().selectionChanged.connect(
            self.on_row_selected
        )

    # ----------------------------
    # Row selection
    # ----------------------------

    def on_row_selected(self):
        row = self.table.currentRow()
        if row < 0:
            return

        self.detail.setText(f"Clip {row + 1}")

    # ----------------------------
    # Open clip
    # ----------------------------

    def open_clip(self):
        row = self.table.currentRow()
        if row < 0:
            return

        # UI is the source of truth
        checkbox = self.table.cellWidget(row, 2)
        if checkbox and not checkbox.isChecked():
            self.detail.setText("⚠️ This clip is disabled")
            return

        clip_index = row
        clip = DATA_DIR / "output" / "clips" / f"highlight_{clip_index:03d}.mp4"

        if not clip.exists():
            self.detail.setText(f"❌ Clip not found:\n{clip}")
            return

        try:
            os.startfile(str(clip))
        except Exception as e:
            self.detail.setText(f"❌ Failed to open clip:\n{e}")

    # ----------------------------
    # Checkbox handler
    # ----------------------------

    def on_enabled_toggled(self, row: int, state: int):
        enabled = state == Qt.CheckState.Checked

        # Update in-memory model
        self.timeline[row]["enabled"] = enabled

        # Persist
        self.save_timeline()

        # Keep row selected
        self.table.setCurrentCell(row, 0)

        self.detail.setText(f"Clip {row+1} {'ENABLED' if enabled else 'DISABLED'}")

    # ----------------------------
    # Persistence
    # ----------------------------

    def save_timeline(self):
        obj = {
            "schema_version": 2,
            "timeline": self.timeline
        }
        self.timeline_path.write_text(
            json.dumps(obj, indent=2),
            encoding="utf-8"
        )

    # ----------------------------
    # Helpers
    # ----------------------------

    @staticmethod
    def _fmt(sec: float) -> str:
        total = int(sec)
        return f"{total // 60:02d}:{total % 60:02d}"
