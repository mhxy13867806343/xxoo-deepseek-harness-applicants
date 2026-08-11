"""
Harness Index — Developer Detail View
Displays full developer metadata, GitHub/X profiles, and list of submitted projects.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea, QAbstractItemView
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QFont, QColor

from core.data_loader import (
    data_store, INTENT_LABELS, IDENTITY_LABELS, LANG_COLORS,
    fmt_num, fmt_date, cat_of
)
from gui.components.widgets import BadgeLabel, MetricCard


class DeveloperDetailView(QWidget):
    """Detailed view for an individual developer."""
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.developer_data = {}
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(40, 32, 40, 40)
        self.content_layout.setSpacing(20)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def set_developer(self, dev_info):
        """Set or reload developer data."""
        if isinstance(dev_info, str):
            dev = data_store.get_developer(dev_info)
            if dev:
                self.developer_data = dev
            else:
                self.developer_data = {"name": dev_info, "x": dev_info}
        elif isinstance(dev_info, dict):
            key = dev_info.get("x") or dev_info.get("github") or dev_info.get("name")
            found = data_store.get_developer(key) if key else None
            self.developer_data = found if found else dev_info
        else:
            self.developer_data = {}

        self.refresh()

    def refresh(self):
        """Rebuild view content."""
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()

        dev = self.developer_data
        if not dev:
            empty_lbl = QLabel("未找到相关开发者信息")
            empty_lbl.setStyleSheet("color: #9aa7ba; font-size: 16px;")
            self.content_layout.addWidget(empty_lbl)
            return

        # 1. Back button
        back_btn = QPushButton("← 返回开发者目录")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setStyleSheet("""
            QPushButton {
                color: #9aa7ba;
                background: transparent;
                border: none;
                font-size: 14px;
                text-align: left;
                padding: 0px;
            }
            QPushButton:hover {
                color: #e3b341;
            }
        """)
        back_btn.clicked.connect(lambda: self.navigate_to.emit("developers", {}))
        self.content_layout.addWidget(back_btn)

        # 2. Profile Header
        header_card = QFrame()
        header_card.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.12);
                border-radius: 12px;
                padding: 24px;
            }
        """)
        hc_layout = QHBoxLayout(header_card)
        hc_layout.setSpacing(20)

        # Avatar
        avatar_lbl = QLabel()
        avatar_lbl.setFixedSize(64, 64)
        avatar_lbl.setStyleSheet("""
            background-color: rgba(227, 179, 65, 0.12);
            color: #e3b341;
            border-radius: 32px;
            font-size: 26px;
            font-weight: bold;
        """)
        avatar_lbl.setAlignment(Qt.AlignCenter)
        name = dev.get("name") or dev.get("id", "Unknown")
        avatar_lbl.setText(name[0].upper() if name else "?")
        hc_layout.addWidget(avatar_lbl)

        # Dev Info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(6)

        title_row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setStyleSheet("color: #ece5d6; font-size: 24px; font-weight: bold;")
        title_row.addWidget(name_lbl)

        x_handle = dev.get("x")
        if x_handle:
            x_lbl = QLabel(f"@{x_handle}")
            x_lbl.setStyleSheet("color: #67758c; font-size: 14px;")
            title_row.addWidget(x_lbl)

        title_row.addStretch()
        info_layout.addLayout(title_row)

        # Badges
        badges_row = QHBoxLayout()
        badges_row.setSpacing(8)

        intent = dev.get("intent", "unknown")
        intent_text = INTENT_LABELS.get(intent, intent)
        badges_row.addWidget(BadgeLabel(intent_text, "blue"))

        identity = dev.get("identity_confidence") or dev.get("identity") or "unconfirmed"
        identity_text = IDENTITY_LABELS.get(identity, identity)
        badges_row.addWidget(BadgeLabel(identity_text, "green"))

        badges_row.addStretch()
        info_layout.addLayout(badges_row)

        # Excerpt / Bio
        excerpt = dev.get("excerpt") or dev.get("bio")
        if excerpt:
            excerpt_lbl = QLabel(excerpt)
            excerpt_lbl.setStyleSheet("color: #9aa7ba; font-size: 13px; margin-top: 4px;")
            excerpt_lbl.setWordWrap(True)
            info_layout.addWidget(excerpt_lbl)

        hc_layout.addLayout(info_layout, 1)

        # Action Buttons
        btn_col = QVBoxLayout()
        btn_col.setSpacing(8)

        gh_username = dev.get("github")
        if gh_username:
            gh_btn = QPushButton(f"GitHub (@{gh_username}) ↗")
            gh_btn.setCursor(Qt.PointingHandCursor)
            gh_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1c2638;
                    color: #ece5d6;
                    border: 1px solid rgba(158, 178, 205, 0.2);
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    border-color: #e3b341;
                    color: #e3b341;
                }
            """)
            gh_url = f"https://github.com/{gh_username}"
            gh_btn.clicked.connect(lambda checked, url=gh_url: QDesktopServices.openUrl(QUrl(url)))
            btn_col.addWidget(gh_btn)

        if x_handle:
            x_btn = QPushButton(f"X (@{x_handle}) ↗")
            x_btn.setCursor(Qt.PointingHandCursor)
            x_btn.setStyleSheet("""
                QPushButton {
                    background-color: #1c2638;
                    color: #ece5d6;
                    border: 1px solid rgba(158, 178, 205, 0.2);
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 12px;
                }
                QPushButton:hover {
                    border-color: #e3b341;
                    color: #e3b341;
                }
            """)
            x_url = f"https://x.com/{x_handle}"
            x_btn.clicked.connect(lambda checked, url=x_url: QDesktopServices.openUrl(QUrl(url)))
            btn_col.addWidget(x_btn)

        btn_col.addStretch()
        hc_layout.addLayout(btn_col)

        self.content_layout.addWidget(header_card)

        # 3. Submitted Projects Header
        projects = dev.get("projects") or []
        p_title = QLabel(f"关联项目 ({len(projects)})")
        p_title.setStyleSheet("color: #ece5d6; font-size: 18px; font-weight: bold; margin-top: 12px;")
        self.content_layout.addWidget(p_title)

        # 4. Table of Projects
        if projects:
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["项目名称", "Stars", "主语言", "赛道", "描述"])
            table.horizontalHeader().setVisible(True)
            table.verticalHeader().setVisible(False)
            table.setSelectionBehavior(QAbstractItemView.SelectRows)
            table.setSelectionMode(QAbstractItemView.SingleSelection)
            table.setShowGrid(True)
            table.setEditTriggers(QAbstractItemView.NoEditTriggers)

            header = table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(1, QHeaderView.Fixed)
            table.setColumnWidth(1, 80)
            header.setSectionResizeMode(2, QHeaderView.Fixed)
            table.setColumnWidth(2, 100)
            header.setSectionResizeMode(3, QHeaderView.Fixed)
            table.setColumnWidth(3, 120)
            header.setSectionResizeMode(4, QHeaderView.Stretch)

            table.setStyleSheet("""
                QTableWidget {
                    background-color: #101827;
                    color: #ece5d6;
                    gridline-color: rgba(158, 178, 205, 0.10);
                    border: 1px solid rgba(158, 178, 205, 0.10);
                    border-radius: 8px;
                }
                QTableWidget::item {
                    padding: 8px;
                    border-bottom: 1px solid rgba(158, 178, 205, 0.05);
                }
                QHeaderView::section {
                    background-color: #141e2f;
                    color: #9aa7ba;
                    padding: 6px;
                    border: none;
                    border-bottom: 1px solid rgba(158, 178, 205, 0.10);
                    font-weight: bold;
                }
            """)

            table.setRowCount(len(projects))
            for r, p in enumerate(projects):
                p_name = p.get("name") or "Unknown"
                item_name = QTableWidgetItem(p_name)
                item_name.setForeground(QColor("#e3b341"))

                stars = p.get("stars", 0)
                item_stars = QTableWidgetItem(fmt_num(stars))
                item_stars.setFont(QFont("Menlo"))
                item_stars.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                lang = p.get("language") or "—"
                item_lang = QTableWidgetItem(lang)

                cat_info = cat_of(p)
                cat_zh = cat_info.get("zh", "未分类") if isinstance(cat_info, dict) else str(cat_info)
                item_cat = QTableWidgetItem(cat_zh)

                desc_text = p.get("description") or "—"
                item_desc = QTableWidgetItem(desc_text)

                table.setItem(r, 0, item_name)
                table.setItem(r, 1, item_stars)
                table.setItem(r, 2, item_lang)
                table.setItem(r, 3, item_cat)
                table.setItem(r, 4, item_desc)

            table.cellClicked.connect(lambda row, col: self._on_table_clicked(table, row))
            self.content_layout.addWidget(table)
        else:
            no_p = QLabel("暂未提交关联开源项目。")
            no_p.setStyleSheet("color: #67758c; font-size: 14px;")
            self.content_layout.addWidget(no_p)

        self.content_layout.addStretch()

    def _on_table_clicked(self, table, row):
        item = table.item(row, 0)
        if item:
            p_name = item.text()
            self.navigate_to.emit("project_detail", {"name": p_name})
