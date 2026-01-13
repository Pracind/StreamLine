import json
import os
from pathlib import Path
from functools import partial

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
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

        self._updating = False

        self.timeline_path = TIMELINE_PATH
        if not self.timeline_path.exists():
            raise RuntimeError("timeline.json not found. Run pipeline first.")

        raw = json.loads(self.timeline_path.read_text(encoding="utf-8"))
        if isinstance(raw, dict) and "timeline" in raw:
            self.timeline = raw["timeline"]
        else:
            self.timeline = raw

        # UI
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setEditTriggers(QTableWidget.AllEditTriggers)
        layout.addWidget(self.table)

        self.detail = QLabel("Select a row to inspect")
        layout.addWidget(self.detail)

        self.open_btn = QPushButton("Open Clip")
        self.open_btn.clicked.connect(self.open_clip)
        layout.addWidget(self.open_btn)

        # Reorder buttons
        btn_row = QHBoxLayout()

        self.up_btn = QPushButton("↑ Move Up")
        self.up_btn.clicked.connect(self.move_up)
        btn_row.addWidget(self.up_btn)

        self.down_btn = QPushButton("↓ Move Down")
        self.down_btn.clicked.connect(self.move_down)
        btn_row.addWidget(self.down_btn)

        layout.addLayout(btn_row)

        self.populate_table()

        self.table.itemChanged.connect(self.on_trim_edited)
        self.table.selectionModel().selectionChanged.connect(self.on_row_selected)

    # ----------------------------
    # Table
    # ----------------------------

    def populate_table(self):
        self._updating = True
        self.table.clear()

        headers = ["#", "Time", "Start Trim (s)", "End Trim (s)", "Enabled"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(self.timeline))

        for row, entry in enumerate(self.timeline):
            # Index (read-only)
            idx_item = QTableWidgetItem(str(row + 1))
            idx_item.setFlags(idx_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 0, idx_item)

            # Time range (read-only)
            time_item = QTableWidgetItem(
                f'{self._fmt(entry["start_time"])}–{self._fmt(entry["end_time"])}'
            )
            time_item.setFlags(time_item.flags() & ~Qt.ItemIsEditable)
            self.table.setItem(row, 1, time_item)

            # Start trim
            start_trim = entry.get("trim_start_offset", 0.0)
            start_item = QTableWidgetItem(f"{start_trim:.2f}")
            start_item.setFlags(start_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(row, 2, start_item)

            # End trim
            end_trim = entry.get("trim_end_offset", 0.0)
            end_item = QTableWidgetItem(f"{end_trim:.2f}")
            end_item.setFlags(end_item.flags() | Qt.ItemIsEditable)
            self.table.setItem(row, 3, end_item)

            # Enabled checkbox
            enabled = entry.get("enabled", True)
            checkbox = QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(partial(self.on_enabled_toggled, row))
            self.table.setCellWidget(row, 4, checkbox)

        self._updating = False

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

        checkbox = self.table.cellWidget(row, 4)
        if checkbox and not checkbox.isChecked():
            self.detail.setText("This clip is disabled")
            return

        clip_index = row
        clip = DATA_DIR / "output" / "clips" / f"highlight_{clip_index:03d}.mp4"

        if not clip.exists():
            self.detail.setText(f"Clip not found:\n{clip}")
            return

        try:
            os.startfile(str(clip))
        except Exception as e:
            self.detail.setText(f"Failed to open clip:\n{e}")

    # ----------------------------
    # Checkbox handler
    # ----------------------------

    def on_enabled_toggled(self, row: int, state: int):
        enabled = state == Qt.CheckState.Checked
        self.timeline[row]["enabled"] = enabled
        self.save_timeline()
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
    # Trim edit handler
    # ----------------------------

    def on_trim_edited(self, item: QTableWidgetItem):
        if self._updating:
            return

        row = item.row()
        col = item.column()

        if col not in (2, 3):
            return

        entry = self.timeline[row]

        try:
            value = float(item.text())
            if value < 0:
                raise ValueError
        except ValueError:
            self.detail.setText("Trim must be a non-negative number")
            self.refresh_row(row)
            return

        try:
            start_trim = float(self.table.item(row, 2).text())
            end_trim = float(self.table.item(row, 3).text())
        except (TypeError, ValueError):
            self.refresh_row(row)
            return

        original_duration = entry["end_time"] - entry["start_time"]
        trimmed_duration = original_duration - start_trim - end_trim

        MIN_CLIP_SECONDS = 3.0

        if trimmed_duration <= 0:
            self.detail.setText("Trim removes entire clip")
            self.refresh_row(row)
            return

        if trimmed_duration < MIN_CLIP_SECONDS:
            self.detail.setText(
                f"Clip must be at least {MIN_CLIP_SECONDS:.1f}s after trimming"
            )
            self.refresh_row(row)
            return

        entry["trim_start_offset"] = start_trim
        entry["trim_end_offset"] = end_trim
        self.save_timeline()

        self.detail.setText(
            f"Clip {row + 1} trimmed: {trimmed_duration:.2f}s remaining"
        )

    def refresh_row(self, row: int):
        entry = self.timeline[row]
        start_trim = entry.get("trim_start_offset", 0.0)
        end_trim = entry.get("trim_end_offset", 0.0)

        self._updating = True
        self.table.item(row, 2).setText(f"{start_trim:.2f}")
        self.table.item(row, 3).setText(f"{end_trim:.2f}")
        self._updating = False

    # ----------------------------
    # Reordering
    # ----------------------------

    def move_up(self):
        row = self.table.currentRow()
        if row <= 0:
            return
        self.swap_rows(row, row - 1)

    def move_down(self):
        row = self.table.currentRow()
        if row < 0 or row >= self.table.rowCount() - 1:
            return
        self.swap_rows(row, row + 1)

    def swap_rows(self, r1: int, r2: int):
        # Swap in-memory model
        self.timeline[r1], self.timeline[r2] = self.timeline[r2], self.timeline[r1]

        # Update order_index
        self.timeline[r1]["order_index"] = r1
        self.timeline[r2]["order_index"] = r2

        self._updating = True

        # Swap text cells (not widgets)
        for col in range(self.table.columnCount()):
            if col == 4:
                continue  # handled separately
            i1 = self.table.takeItem(r1, col)
            i2 = self.table.takeItem(r2, col)
            self.table.setItem(r1, col, i2)
            self.table.setItem(r2, col, i1)

        # Rebuild checkboxes from model (prevents disappearing)
        for row in (r1, r2):
            enabled = self.timeline[row].get("enabled", True)
            checkbox = QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(partial(self.on_enabled_toggled, row))
            self.table.setCellWidget(row, 4, checkbox)

        # Fix index display
        self.table.item(r1, 0).setText(str(r1 + 1))
        self.table.item(r2, 0).setText(str(r2 + 1))

        self._updating = False

        self.table.setCurrentCell(r2, 0)
        self.save_timeline()
        self.detail.setText(f"Moved clip {r1 + 1} {'up' if r2 < r1 else 'down'}")

    # ----------------------------
    # Helpers
    # ----------------------------

    @staticmethod
    def _fmt(sec: float) -> str:
        total = int(sec)
        return f"{total // 60:02d}:{total % 60:02d}"
