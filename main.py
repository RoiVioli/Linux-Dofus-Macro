import sys
import json
import subprocess
import time
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QLineEdit, QPushButton,
                             QFrame, QScrollArea, QGraphicsDropShadowEffect,
                             QSizePolicy, QMessageBox)
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor
from pynput import keyboard


CONFIG_DIR  = Path.home() / ".config" / "dofusswitch"
CONFIG_FILE = CONFIG_DIR  / "config.json"


def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    return {}


def save_config(data):
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except:
        pass


def get_dofus_windows():
    windows = []
    try:
        result = subprocess.run(["wmctrl", "-l", "-p"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=4)
            if len(parts) >= 5 and "dofus" in parts[4].lower():
                windows.append({"wid": parts[0], "pid": parts[2]})
    except:
        pass
    return windows


def focus_window(wid):
    subprocess.Popen(["wmctrl", "-i", "-a", wid])


def close_window(wid):
    subprocess.Popen(["wmctrl", "-i", "-c", wid])


def apply_shadow(widget, blur=20, offset_y=4, alpha=40):
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setBlurRadius(blur)
    shadow.setOffset(0, offset_y)
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)


class HotkeyLineEdit(QLineEdit):
    PLACEHOLDER = "Configurer une macro"

    def __init__(self, current_val="", parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.key_str = current_val
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setFixedHeight(34)
        self._refresh_text()

    def _refresh_text(self):
        self.setText(self.key_str if self.key_str else self.PLACEHOLDER)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        if not self.key_str:
            self.setText("")

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self._refresh_text()

    def keyPressEvent(self, event):
        key = event.key()
        if key in [Qt.Key.Key_Control, Qt.Key.Key_Shift,
                   Qt.Key.Key_Alt, Qt.Key.Key_Meta]:
            return
        mods  = event.modifiers()
        parts = []
        if mods & Qt.KeyboardModifier.ControlModifier: parts.append("<ctrl>")
        if mods & Qt.KeyboardModifier.AltModifier:     parts.append("<alt>")
        if mods & Qt.KeyboardModifier.ShiftModifier:   parts.append("<shift>")
        text = event.text().lower()
        if Qt.Key.Key_F1 <= key <= Qt.Key.Key_F12:
            parts.append(f"f{key - Qt.Key.Key_F1 + 1}")
        elif key == Qt.Key.Key_Space:
            parts.append("<space>")
        elif key == Qt.Key.Key_Escape:
            self.key_str = ""
            self._refresh_text()
            self.editingFinished.emit()
            self.clearFocus()
            return
        elif text:
            parts.append(text)
        else:
            return
        self.key_str = "+".join(parts)
        self._refresh_text()
        self.editingFinished.emit()
        self.clearFocus()


class GroupBadge(QPushButton):
    def __init__(self, group="A", parent=None):
        super().__init__(parent)
        self.group = group
        self.setObjectName("GroupBadge")
        self.setFixedSize(90, 30)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._refresh()

    def _refresh(self):
        self.setText(f"Groupe  {self.group}")
        self.setProperty("group", self.group)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def toggle(self):
        self.group = "B" if self.group == "A" else "A"
        self._refresh()
        return self.group


# (icon_next, icon_prev, title, description, accent_color)
MACRO_DEFS = [
    ("⟳", "⟲", "Cycle total",    "Toutes les fenetres\nselon l'ordre defini", "#7dd3fc"),
    ("A",  "A",  "Cycle groupe A", "Uniquement les\ncomptes du groupe A",       "#38bdf8"),
    ("B",  "B",  "Cycle groupe B", "Uniquement les\ncomptes du groupe B",       "#fb923c"),
]


class MacroCard(QFrame):
    def __init__(self, icon_next, icon_prev, title, description,
                 accent_color, hk_next="", hk_prev="", parent=None):
        super().__init__(parent)
        self.setObjectName("MacroCard")
        apply_shadow(self, blur=18, offset_y=5, alpha=35)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        accent_bar = QFrame()
        accent_bar.setFixedHeight(4)
        accent_bar.setStyleSheet(
            f"background-color: {accent_color}; border-radius: 0px;"
            f"border-top-left-radius: 16px; border-top-right-radius: 16px;"
        )
        outer.addWidget(accent_bar)

        inner = QVBoxLayout()
        inner.setContentsMargins(16, 12, 16, 14)
        inner.setSpacing(10)

        top_row = QHBoxLayout()
        top_row.setSpacing(12)

        icon_lbl = QLabel(icon_next)
        icon_lbl.setObjectName("MacroIcon")
        icon_lbl.setFixedSize(40, 40)
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet(
            f"color: {accent_color}; font-size: 18px; font-weight: 900;"
            f"background-color: rgba(255,255,255,0.04); border-radius: 10px;"
        )

        title_col = QVBoxLayout()
        title_col.setSpacing(3)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("MacroTitle")
        desc_lbl  = QLabel(description)
        desc_lbl.setObjectName("MacroDesc")
        desc_lbl.setWordWrap(True)
        title_col.addWidget(title_lbl)
        title_col.addWidget(desc_lbl)

        top_row.addWidget(icon_lbl)
        top_row.addLayout(title_col, 1)
        inner.addLayout(top_row)

        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setStyleSheet("background-color: #1e3050; border: none;")
        divider.setFixedHeight(1)
        inner.addWidget(divider)

        next_row = QHBoxLayout()
        next_row.setSpacing(8)
        next_arrow = QLabel("▶")
        next_arrow.setStyleSheet(f"color: {accent_color}; font-size: 11px;")
        next_arrow.setFixedWidth(14)
        next_lbl = QLabel("SUIVANT")
        next_lbl.setObjectName("MacroHkLabel")
        next_row.addWidget(next_arrow)
        next_row.addWidget(next_lbl)
        next_row.addStretch()

        self.hk_edit = HotkeyLineEdit(hk_next)
        self.hk_edit.setObjectName("MacroHkEdit")

        prev_row = QHBoxLayout()
        prev_row.setSpacing(8)
        prev_arrow = QLabel("◀")
        prev_arrow.setStyleSheet(f"color: {accent_color}; font-size: 11px;")
        prev_arrow.setFixedWidth(14)
        prev_lbl = QLabel("PRECEDENT")
        prev_lbl.setObjectName("MacroHkLabel")
        prev_row.addWidget(prev_arrow)
        prev_row.addWidget(prev_lbl)
        prev_row.addStretch()

        self.hk_prev_edit = HotkeyLineEdit(hk_prev)
        self.hk_prev_edit.setObjectName("MacroHkPrevEdit")

        inner.addLayout(next_row)
        inner.addWidget(self.hk_edit)
        inner.addLayout(prev_row)
        inner.addWidget(self.hk_prev_edit)
        outer.addLayout(inner)


class AccountRow(QFrame):
    def __init__(self, win, config_data, on_update, on_focus, parent=None):
        super().__init__(parent)
        self.win       = win
        self.pid       = win["pid"]
        self.on_update = on_update
        self.setObjectName("AccountRow")
        self.setFixedHeight(78)
        apply_shadow(self, blur=14, offset_y=3, alpha=30)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 0, 12, 0)
        layout.setSpacing(10)
        layout.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        order_frame = QFrame()
        order_frame.setObjectName("OrderFrame")
        order_frame.setFixedSize(52, 52)
        ov = QVBoxLayout(order_frame)
        ov.setContentsMargins(0, 2, 0, 2)
        ov.setSpacing(0)
        ov.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_up = QPushButton("▲")
        self.btn_up.setObjectName("OrderArrow")
        self.btn_up.setFixedHeight(16)
        self.btn_up.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.order_label = QLabel(str(config_data.get("order", 1)))
        self.order_label.setObjectName("OrderValue")
        self.order_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.order_label.setFixedHeight(22)

        self.btn_down = QPushButton("▼")
        self.btn_down.setObjectName("OrderArrow")
        self.btn_down.setFixedHeight(16)
        self.btn_down.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        ov.addWidget(self.btn_up)
        ov.addWidget(self.order_label)
        ov.addWidget(self.btn_down)

        self.btn_up.clicked.connect(lambda: self._change_order(+1))
        self.btn_down.clicked.connect(lambda: self._change_order(-1))

        pid_col = QVBoxLayout()
        pid_col.setSpacing(4)
        pid_col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pid_chip = QLabel(f"PID {self.pid}")
        pid_chip.setObjectName("MetaChip")
        pid_chip.setFixedWidth(80)
        pid_chip.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_close = QPushButton("✕ Fermer")
        btn_close.setObjectName("CloseBtn")
        btn_close.setFixedWidth(80)
        btn_close.setFixedHeight(20)
        btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_close.setToolTip("Close this Dofus window")
        btn_close.clicked.connect(self._close_window)

        pid_col.addWidget(pid_chip)
        pid_col.addWidget(btn_close)

        def vsep():
            s = QFrame()
            s.setFrameShape(QFrame.Shape.VLine)
            s.setStyleSheet("color: #1e3050; background-color: #1e3050;")
            s.setFixedWidth(1)
            return s

        name_edit = QLineEdit(config_data.get("name", f"Compte {self.pid}"))
        name_edit.setObjectName("AccountNameEdit")
        name_edit.setPlaceholderText("Account name")
        name_edit.setFixedHeight(36)
        name_edit.textChanged.connect(lambda t: self.on_update(self.pid, "name", t))

        self.group_badge = GroupBadge(config_data.get("group", "A"))
        self.group_badge.clicked.connect(self._toggle_group)

        self.hk_edit = HotkeyLineEdit(config_data.get("hk", ""))
        self.hk_edit.setObjectName("HotkeyEdit")
        self.hk_edit.setFixedWidth(200)
        self.hk_edit.editingFinished.connect(
            lambda: self.on_update(self.pid, "hk", self.hk_edit.key_str)
        )

        btn_eye = QPushButton()
        btn_eye.setObjectName("EyeBtn")
        btn_eye.setFixedSize(38, 38)
        btn_eye.setToolTip("Preview / bring to front")
        btn_eye.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_eye.setStyleSheet("""
            QPushButton {
                background-color: #0e2236;
                color: #5090c0;
                border: 1px solid #1a3858;
                border-radius: 10px;
                font-family: "Segoe UI Emoji", "Noto Emoji", "DejaVu Sans", sans-serif;
                font-size: 18px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #1a3a5c;
                color: #a8d8f8;
                border-color: #3a80b8;
            }
        """)
        btn_eye.setText("\U0001F441")
        btn_eye.clicked.connect(lambda: on_focus(self.win["wid"]))

        btn_focus = QPushButton("Focus")
        btn_focus.setObjectName("FocusBtn")
        btn_focus.setFixedSize(76, 38)
        btn_focus.setToolTip("Switch to this window")
        btn_focus.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_focus.clicked.connect(lambda: on_focus(self.win["wid"]))

        layout.addWidget(order_frame)
        layout.addWidget(vsep())
        layout.addLayout(pid_col)
        layout.addWidget(vsep())
        layout.addWidget(name_edit, 1)
        layout.addWidget(self.group_badge)
        layout.addWidget(vsep())
        layout.addWidget(self.hk_edit)
        layout.addWidget(vsep())
        layout.addWidget(btn_eye)
        layout.addWidget(btn_focus)

    def _change_order(self, delta):
        new_val = max(1, min(99, int(self.order_label.text()) + delta))
        self.order_label.setText(str(new_val))
        self.on_update(self.pid, "order", new_val)

    def _toggle_group(self):
        new_grp = self.group_badge.toggle()
        self.on_update(self.pid, "group", new_grp)

    def _close_window(self):
        close_window(self.win["wid"])


class DofusSwitchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DofusSwitch — Team Manager")
        self.setMinimumSize(820, 560)

        self.config           = load_config()
        self.hotkeys_listener = None
        self.last_switch_time = 0
        self.windows          = []
        self._indices         = {"TOTAL": 0, "A": 0, "B": 0}

        self._apply_stylesheet()
        self._build_ui()
        self.refresh()
        QTimer.singleShot(0, self._auto_resize)

    def _auto_resize(self):
        """Recalculate ideal window height based on detected accounts and resize."""
        screen = QApplication.primaryScreen().availableGeometry()

        HEADER_H         = 110
        MACROS_H         = 320
        FOOTER_H         = 62
        PADDING_V        = 16 * 2 + 14 * 2 + 10 * 2
        SECTION_HEADER_H = 40
        ROW_H            = 78
        ROW_GAP          = 8
        n                = len(self.windows)

        accounts_h = 80 if n == 0 else SECTION_HEADER_H + n * ROW_H + (n - 1) * ROW_GAP
        ideal_h    = HEADER_H + MACROS_H + accounts_h + FOOTER_H + PADDING_V

        new_h = max(600, min(ideal_h, screen.height() - 80))
        new_w = min(max(self.width(), 900), screen.width() - 80)

        self.resize(new_w, new_h)
        self.move(
            screen.x() + (screen.width()  - new_w) // 2,
            screen.y() + (screen.height() - new_h) // 2,
        )

    def _apply_stylesheet(self):
        self.setStyleSheet("""
            QMainWindow, QWidget {
                background-color: #08111f;
                color: #d6deeb;
                font-family: "DejaVu Sans", "Noto Sans", sans-serif;
                font-size: 13px;
            }
            #HeaderBg { background: transparent; border: none; }
            #AppTitle { color: #f0f6ff; font-size: 26px; font-weight: 900; letter-spacing: 1px; }
            #AppEyebrow { color: #5da8d4; font-size: 11px; font-weight: 700; letter-spacing: 2px; }
            #StatusPill {
                background-color: #0e2236; color: #6ee7b7;
                border: 1px solid #1e4a38; border-radius: 12px;
                padding: 5px 12px; font-size: 11px; font-weight: 700;
            }
            #WinCountLbl { color: #5a7a9a; font-size: 11px; }
            #StatCard { background-color: transparent; border: 1px solid #1c3050; border-radius: 14px; }
            #StatValue { color: #f0f6ff; font-size: 26px; font-weight: 900; }
            #StatLabel { color: #6a8aaa; font-size: 10px; font-weight: 700; letter-spacing: 1.5px; }
            #BodyWrap { background-color: #090f1b; }
            #SectionBlock { background-color: transparent; border: 1px solid #1a2d44; border-radius: 20px; }
            #SectionLabel { color: #e8f2ff; font-size: 16px; font-weight: 800; }
            #MacroCard { background-color: transparent; border: 1px solid #1e3254; border-radius: 16px; }
            #MacroTitle { color: #e8f2ff; font-size: 13px; font-weight: 800; }
            #MacroDesc { color: #7a9ab8; font-size: 11px; }
            #MacroHkLabel { color: #4a6a88; font-size: 10px; font-weight: 700; letter-spacing: 1.2px; }
            #MacroHkEdit {
                background-color: #08111f; color: #c8e8ff;
                border: 1px solid #1e3560; border-radius: 9px;
                padding: 6px 10px; font-size: 12px; font-weight: 700;
            }
            #MacroHkEdit:focus { border: 1px solid #7dd3fc; }
            #MacroHkPrevEdit {
                background-color: #08111f; color: #b0c8e0;
                border: 1px solid #1a2e50; border-radius: 9px;
                padding: 6px 10px; font-size: 12px; font-weight: 700;
            }
            #MacroHkPrevEdit:focus { border: 1px solid #7dd3fc; }
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: transparent; width: 8px; }
            QScrollBar::handle:vertical { background: #1e3254; border-radius: 4px; min-height: 20px; }
            QScrollBar::handle:vertical:hover { background: #3a6090; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
            #AccountRow { background-color: #0e1929; border: 1px solid #1a2d44; border-radius: 16px; }
            #AccountRow:hover { border-color: #2a4870; background-color: #111f33; }
            #OrderFrame { background-color: #08111f; border: 1px solid #1a2d44; border-radius: 12px; }
            #OrderArrow { background: transparent; color: #3a5880; border: none; font-size: 9px; padding: 0; }
            #OrderArrow:hover { color: #7dd3fc; background-color: #132033; border-radius: 6px; }
            #OrderValue { color: #7dd3fc; font-weight: 900; font-size: 17px; }
            #MetaChip {
                background-color: #0d1828; color: #4a7090;
                border: 1px solid #1a3050; border-radius: 8px;
                padding: 4px 8px; font-size: 10px; font-weight: 700;
            }
            #AccountNameEdit {
                background-color: #08111f; color: #e8f2ff;
                border: 1px solid #1a2e48; border-radius: 10px;
                padding: 6px 12px; font-size: 13px; font-weight: 600;
            }
            #AccountNameEdit:focus { border-color: #7dd3fc; }
            #GroupBadge { border-radius: 9px; font-size: 11px; font-weight: 800; }
            #GroupBadge[group="A"] { background-color: #0e2540; color: #7dd3fc; border: 1px solid #1e4870; }
            #GroupBadge[group="A"]:hover { background-color: #152e50; }
            #GroupBadge[group="B"] { background-color: #2d1a08; color: #fdba74; border: 1px solid #6a3810; }
            #GroupBadge[group="B"]:hover { background-color: #3a2010; }
            #HotkeyEdit {
                background-color: #08111f; color: #c8e8ff;
                border: 1px solid #1e3560; border-radius: 9px;
                padding: 5px 10px; font-size: 12px; font-weight: 700;
            }
            #HotkeyEdit:focus { border-color: #7dd3fc; }
            #CloseBtn {
                background-color: #2a0e0e; color: #e06060;
                border: 1px solid #5a1e1e; border-radius: 6px;
                font-size: 10px; font-weight: 700; padding: 0;
            }
            #CloseBtn:hover { background-color: #5a1e1e; color: #ffaaaa; border-color: #c04040; }
            #EyeBtn { background-color: #0e2236; color: #5090c0; border: 1px solid #1a3858; border-radius: 10px; font-size: 18px; padding: 0; }
            #EyeBtn:hover { background-color: #1a3a5c; color: #a8d8f8; border-color: #3a80b8; }
            #FocusBtn { background-color: #1a5a8a; color: #ffffff; border: none; border-radius: 10px; font-size: 12px; font-weight: 800; }
            #FocusBtn:hover { background-color: #2270aa; }
            #FooterBar { background-color: #07101d; border-top: 1px solid #162030; }
            #FooterNote { color: #3a5a78; font-size: 11px; }
            #RefreshBtn {
                background-color: #0e2236; color: #a8d0f0;
                border: 1px solid #1e3858; border-radius: 10px;
                padding: 9px 18px; font-size: 12px; font-weight: 800;
            }
            #RefreshBtn:hover { border-color: #7dd3fc; color: #e0f4ff; }
            #SaveBtn {
                background-color: #0e2820; color: #6ee7b7;
                border: 1px solid #1e4838; border-radius: 10px;
                padding: 9px 18px; font-size: 12px; font-weight: 800;
            }
            #SaveBtn:hover { border-color: #3ecf8e; color: #b6fde0; }
            #CloseAllBtn {
                background-color: #2a0e0e; color: #e06060;
                border: 1px solid #5a1e1e; border-radius: 10px;
                padding: 9px 18px; font-size: 12px; font-weight: 800;
            }
            #CloseAllBtn:hover { background-color: #5a1e1e; color: #ffaaaa; border-color: #c04040; }
            QMessageBox { background-color: #0e1929; color: #e8f2ff; }
            QMessageBox QLabel { color: #e8f2ff; font-size: 13px; }
            QMessageBox QPushButton {
                background-color: #0e2236; color: #a8d0f0;
                border: 1px solid #1e3858; border-radius: 8px;
                padding: 6px 16px; font-size: 12px; font-weight: 700; min-width: 80px;
            }
            QMessageBox QPushButton:hover { border-color: #7dd3fc; color: #e0f4ff; }
            #EmptyCard { background-color: #0e1929; border: 1px dashed #1e3858; border-radius: 16px; }
            #EmptyTitle { color: #e8f2ff; font-size: 16px; font-weight: 800; }
            #EmptyState { color: #4a6a8a; font-size: 12px; }
        """)

    def _build_ui(self):
        root = QWidget()
        self.setCentralWidget(root)
        ml = QVBoxLayout(root)
        ml.setContentsMargins(0, 0, 0, 0)
        ml.setSpacing(0)

        header = QFrame()
        header.setObjectName("HeaderBg")
        header.setFixedHeight(110)
        hl = QHBoxLayout(header)
        hl.setContentsMargins(24, 0, 24, 0)
        hl.setSpacing(24)

        tb = QVBoxLayout()
        tb.setSpacing(3)
        eyebrow = QLabel("TEAM MANAGER")
        eyebrow.setObjectName("AppEyebrow")
        title = QLabel("DofusSwitch")
        title.setObjectName("AppTitle")
        tb.addWidget(eyebrow)
        tb.addWidget(title)
        hl.addLayout(tb)
        hl.addStretch(1)

        self.stat_windows = self._make_stat_card("0", "FENETRES")
        self.stat_group_a = self._make_stat_card("0", "GROUPE A")
        self.stat_group_b = self._make_stat_card("0", "GROUPE B")
        for sc in [self.stat_windows, self.stat_group_a, self.stat_group_b]:
            hl.addWidget(sc)
        hl.addStretch(1)

        sb = QVBoxLayout()
        sb.setSpacing(6)
        sb.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.status_pill = QLabel("Aucun raccourci actif")
        self.status_pill.setObjectName("StatusPill")
        self.win_count_lbl = QLabel("Aucune fenetre detectee")
        self.win_count_lbl.setObjectName("WinCountLbl")
        self.win_count_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
        sb.addWidget(self.status_pill, 0, Qt.AlignmentFlag.AlignRight)
        sb.addWidget(self.win_count_lbl)
        hl.addLayout(sb)
        ml.addWidget(header)

        body = QWidget()
        body.setObjectName("BodyWrap")
        bl = QVBoxLayout(body)
        bl.setContentsMargins(18, 16, 18, 16)
        bl.setSpacing(14)

        macros_section = QFrame()
        macros_section.setObjectName("SectionBlock")
        msl = QVBoxLayout(macros_section)
        msl.setContentsMargins(18, 14, 18, 16)
        msl.setSpacing(12)
        msl.addWidget(self._section_title("Macros globales"))

        macros_row = QHBoxLayout()
        macros_row.setSpacing(12)
        g = self.config.get("global", {})

        self.cycle_card   = MacroCard(*MACRO_DEFS[0], g.get("cycle_hk", ""),   g.get("cycle_prev_hk", ""))
        self.group_a_card = MacroCard(*MACRO_DEFS[1], g.get("group_a_hk", ""), g.get("group_a_prev_hk", ""))
        self.group_b_card = MacroCard(*MACRO_DEFS[2], g.get("group_b_hk", ""), g.get("group_b_prev_hk", ""))

        for card in [self.cycle_card, self.group_a_card, self.group_b_card]:
            card.hk_edit.editingFinished.connect(self.update_global_hks)
            card.hk_prev_edit.editingFinished.connect(self.update_global_hks)
            macros_row.addWidget(card)
        msl.addLayout(macros_row)
        bl.addWidget(macros_section)

        accounts_section = QFrame()
        accounts_section.setObjectName("SectionBlock")
        asl = QVBoxLayout(accounts_section)
        asl.setContentsMargins(18, 14, 18, 16)
        asl.setSpacing(10)

        accounts_header = QHBoxLayout()
        accounts_header.addWidget(self._section_title("Comptes detectes"))
        accounts_header.addStretch()
        self.btn_close_all = QPushButton("✕  Fermer tous les comptes")
        self.btn_close_all.setObjectName("CloseAllBtn")
        self.btn_close_all.setFixedHeight(34)
        self.btn_close_all.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close_all.setToolTip("Close all detected Dofus windows")
        self.btn_close_all.clicked.connect(self._confirm_close_all)
        self.btn_close_all.setEnabled(False)
        accounts_header.addWidget(self.btn_close_all)
        asl.addLayout(accounts_header)

        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.scroll_layout = QVBoxLayout(self.container)
        self.scroll_layout.setContentsMargins(0, 0, 6, 0)
        self.scroll_layout.setSpacing(8)
        self.scroll_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll.setWidget(self.container)
        asl.addWidget(self.scroll)
        bl.addWidget(accounts_section, 1)
        ml.addWidget(body, 1)

        footer = QFrame()
        footer.setObjectName("FooterBar")
        footer.setFixedHeight(62)
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(20, 0, 20, 0)
        fl.setSpacing(10)

        self.footer_note = QLabel("Les changements sont sauvegardes automatiquement.")
        self.footer_note.setObjectName("FooterNote")

        self.btn_refresh = QPushButton("↺  Actualiser")
        self.btn_refresh.setObjectName("RefreshBtn")
        self.btn_refresh.setFixedHeight(38)
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.clicked.connect(self.refresh)

        self.btn_save = QPushButton("✓  Sauvegarder")
        self.btn_save.setObjectName("SaveBtn")
        self.btn_save.setFixedHeight(38)
        self.btn_save.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save.clicked.connect(self.manual_save)

        fl.addWidget(self.footer_note)
        fl.addStretch()
        fl.addWidget(self.btn_refresh)
        fl.addWidget(self.btn_save)
        ml.addWidget(footer)

    def _section_title(self, text):
        lbl = QLabel(text)
        lbl.setObjectName("SectionLabel")
        return lbl

    def _make_stat_card(self, value, label):
        card = QFrame()
        card.setObjectName("StatCard")
        card.setFixedSize(90, 70)
        apply_shadow(card, blur=16, offset_y=4, alpha=30)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(2)
        vl = QLabel(value)
        vl.setObjectName("StatValue")
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ll = QLabel(label)
        ll.setObjectName("StatLabel")
        ll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(vl)
        lay.addWidget(ll)
        card.value_label = vl
        return card

    def _confirm_close_all(self):
        n = len(self.windows)
        if not n:
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmer la fermeture")
        msg.setText(
            f"Vous allez fermer {n} fenetre{'s' if n > 1 else ''} Dofus.\n"
            f"Les personnages non sauvegardes seront perdus."
        )
        msg.setIcon(QMessageBox.Icon.Warning)
        btn_confirm = msg.addButton("Fermer tous", QMessageBox.ButtonRole.AcceptRole)
        msg.addButton("Annuler", QMessageBox.ButtonRole.RejectRole)
        msg.exec()
        if msg.clickedButton() == btn_confirm:
            self._close_all_windows()

    def _close_all_windows(self):
        for win in self.windows:
            close_window(win["wid"])
        QTimer.singleShot(800, self.refresh)

    def refresh(self):
        while self.scroll_layout.count():
            item = self.scroll_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self.windows = get_dofus_windows()
        self.btn_close_all.setEnabled(len(self.windows) > 0)

        if not self.windows:
            empty_card = QFrame()
            empty_card.setObjectName("EmptyCard")
            el = QVBoxLayout(empty_card)
            el.setContentsMargins(20, 20, 20, 20)
            el.setSpacing(6)
            et = QLabel("Aucune fenetre Dofus detectee")
            et.setObjectName("EmptyTitle")
            et.setAlignment(Qt.AlignmentFlag.AlignCenter)
            es = QLabel("Lancez le jeu puis cliquez sur Actualiser.")
            es.setObjectName("EmptyState")
            es.setAlignment(Qt.AlignmentFlag.AlignCenter)
            el.addWidget(et)
            el.addWidget(es)
            self.scroll_layout.addWidget(empty_card)
        else:
            for win in self.windows:
                pid  = win["pid"]
                data = self.config.get(pid, {
                    "order": 1, "name": f"Compte {pid}", "hk": "", "group": "A"
                })
                row = AccountRow(win=win, config_data=data,
                                 on_update=self.update_data, on_focus=focus_window)
                self.scroll_layout.addWidget(row)

        self._update_stats()
        QTimer.singleShot(50,  self._auto_resize)
        QTimer.singleShot(120, self.restart_hotkeys)

    def _update_stats(self):
        total   = len(self.windows)
        group_a = sum(1 for w in self.windows
                      if self.config.get(w["pid"], {}).get("group", "A") == "A")
        group_b = total - group_a
        self.stat_windows.value_label.setText(str(total))
        self.stat_group_a.value_label.setText(str(group_a))
        self.stat_group_b.value_label.setText(str(group_b))
        self.win_count_lbl.setText(
            f"{total} fenetre{'s' if total != 1 else ''} prete{'s' if total != 1 else ''}"
            if total else "Aucune fenetre detectee"
        )

    def update_data(self, pid, key, val):
        if pid not in self.config:
            self.config[pid] = {}
        self.config[pid][key] = val
        save_config(self.config)
        if key == "group": self._update_stats()
        if key == "hk":    self.restart_hotkeys()

    def update_global_hks(self):
        if "global" not in self.config:
            self.config["global"] = {}
        self.config["global"]["cycle_hk"]        = self.cycle_card.hk_edit.key_str
        self.config["global"]["cycle_prev_hk"]   = self.cycle_card.hk_prev_edit.key_str
        self.config["global"]["group_a_hk"]      = self.group_a_card.hk_edit.key_str
        self.config["global"]["group_a_prev_hk"] = self.group_a_card.hk_prev_edit.key_str
        self.config["global"]["group_b_hk"]      = self.group_b_card.hk_edit.key_str
        self.config["global"]["group_b_prev_hk"] = self.group_b_card.hk_prev_edit.key_str
        save_config(self.config)
        self.restart_hotkeys()

    def cycle_logic(self, target_group=None, direction=1):
        """Navigate through windows in sorted order. direction=1 for next, -1 for previous."""
        now = time.time()
        if now - self.last_switch_time < 0.05:
            return
        self.last_switch_time = now
        if not self.windows:
            return

        valid = [
            (self.config.get(w["pid"], {}).get("order", 99), w["wid"])
            for w in self.windows
            if target_group is None or self.config.get(w["pid"], {}).get("group", "A") == target_group
        ]
        if not valid:
            return

        valid.sort()
        key = target_group or "TOTAL"
        idx = self._indices.get(key, 0) % len(valid)

        if direction == -1:
            idx = (idx - 2) % len(valid)

        focus_window(valid[idx][1])
        self._indices[key] = (idx + 1) % len(valid)

    def restart_hotkeys(self):
        """Rebuild the global hotkey listener from current config."""
        if self.hotkeys_listener:
            try: self.hotkeys_listener.stop()
            except: pass

        mapping = {}

        for win in self.windows:
            hk = self.config.get(win["pid"], {}).get("hk")
            if hk:
                mapping[hk] = (lambda w=win["wid"]: focus_window(w))

        g = self.config.get("global", {})
        if g.get("cycle_hk"):        mapping[g["cycle_hk"]]        = lambda: self.cycle_logic(None,  1)
        if g.get("cycle_prev_hk"):   mapping[g["cycle_prev_hk"]]   = lambda: self.cycle_logic(None, -1)
        if g.get("group_a_hk"):      mapping[g["group_a_hk"]]      = lambda: self.cycle_logic("A",  1)
        if g.get("group_a_prev_hk"): mapping[g["group_a_prev_hk"]] = lambda: self.cycle_logic("A", -1)
        if g.get("group_b_hk"):      mapping[g["group_b_hk"]]      = lambda: self.cycle_logic("B",  1)
        if g.get("group_b_prev_hk"): mapping[g["group_b_prev_hk"]] = lambda: self.cycle_logic("B", -1)

        if mapping:
            self.hotkeys_listener = keyboard.GlobalHotKeys(mapping)
            self.hotkeys_listener.start()
            n = len(mapping)
            self.status_pill.setText(
                f"{n} raccourci{'s' if n > 1 else ''} actif{'s' if n > 1 else ''}"
            )
        else:
            self.status_pill.setText("Aucun raccourci actif")

    def manual_save(self):
        save_config(self.config)
        self.btn_save.setText("✓  Enregistre !")
        QTimer.singleShot(1400, lambda: self.btn_save.setText("✓  Sauvegarder"))

    def closeEvent(self, event):
        if self.hotkeys_listener:
            try: self.hotkeys_listener.stop()
            except: pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    gui = DofusSwitchApp()
    gui.show()
    sys.exit(app.exec())
