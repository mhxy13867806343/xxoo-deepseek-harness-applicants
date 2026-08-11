"""
Harness Index — Project Detail View
Displays full project metrics, description, GitHub link, and metadata.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QGridLayout, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices, QFont

from core.data_loader import data_store, CATS, fmt_num, fmt_date, cat_of
from gui.components.widgets import BadgeLabel, MetricCard


def fmt_release(rel):
    if not rel:
        return "—"
    if isinstance(rel, dict):
        tag = rel.get("tag_name") or rel.get("name") or rel.get("published_at")
        if tag:
            return str(tag)[:20]
        return "已发布"
    if isinstance(rel, str):
        rel_str = rel.strip()
        if rel_str.startswith("{") and ("tag_name" in rel_str or "html_url" in rel_str):
            import ast, re
            try:
                parsed = ast.literal_eval(rel_str)
                if isinstance(parsed, dict):
                    return fmt_release(parsed)
            except Exception:
                pass
            tag_match = re.search(r"['\"]tag_name['\"]\s*:\s*['\"]([^'\"]+)['\"]", rel_str)
            if tag_match:
                return tag_match.group(1)[:20]
            name_match = re.search(r"['\"]name['\"]\s*:\s*['\"]([^'\"]+)['\"]", rel_str)
            if name_match:
                return name_match.group(1)[:20]
            return "已发布"
        return rel_str[:20]
    return str(rel)[:20]


class ProjectDetailView(QWidget):
    """Detailed view for an individual project."""
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.project_data = {}
        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        container = QWidget()
        container.setStyleSheet("background: transparent;")
        self.content_layout = QVBoxLayout(container)
        self.content_layout.setContentsMargins(40, 32, 40, 40)
        self.content_layout.setSpacing(24)

        scroll.setWidget(container)
        main_layout.addWidget(scroll)

    def set_project(self, project_info):
        """Set or reload project data."""
        if isinstance(project_info, str):
            proj = data_store.get_project(project_info)
            if proj:
                self.project_data = proj
            else:
                self.project_data = {"name": project_info}
        elif isinstance(project_info, dict):
            name = project_info.get("name") or project_info.get("repo_id") or project_info.get("repo")
            found = data_store.get_project(name) if name else None
            self.project_data = found if found else project_info
        else:
            self.project_data = {}

        self.refresh()

    def refresh(self):
        """Rebuild view content."""
        # Clear layout
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                while item.layout().count():
                    sub_item = item.layout().takeAt(0)
                    if sub_item.widget():
                        sub_item.widget().deleteLater()

        proj = self.project_data
        if not proj:
            empty_lbl = QLabel("未找到相关项目信息")
            empty_lbl.setStyleSheet("color: #9aa7ba; font-size: 16px;")
            self.content_layout.addWidget(empty_lbl)
            return

        # 1. Back button
        back_btn = QPushButton("← 返回目录")
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
        back_btn.clicked.connect(lambda: self.navigate_to.emit("projects", {}))
        self.content_layout.addWidget(back_btn)

        # 2. Badges Row
        badges_layout = QHBoxLayout()
        badges_layout.setSpacing(10)

        # Category
        cat_info = cat_of(proj)
        cat_zh = cat_info.get("zh", "未分类") if isinstance(cat_info, dict) else str(cat_info)
        badges_layout.addWidget(BadgeLabel(cat_zh, "blue"))

        # Harness/DS badge
        if proj.get("deepseek_native") or proj.get("is_deepseek_native"):
            badges_layout.addWidget(BadgeLabel("DeepSeek 原生", "gold"))
        elif proj.get("relevance") == "strong" or proj.get("ds_related"):
            badges_layout.addWidget(BadgeLabel("Harness 高相关", "gold"))

        # License badge
        license_str = proj.get("license") or "未指定"
        badges_layout.addWidget(BadgeLabel(license_str, "gray"))

        badges_layout.addStretch()
        self.content_layout.addLayout(badges_layout)

        # 3. Project Name & Description
        name = proj.get("name") or proj.get("repo_id") or proj.get("repo") or "Unknown"
        title_lbl = QLabel(name)
        title_lbl.setStyleSheet("color: #f7f2e6; font-size: 36px; font-weight: 700; font-family: 'Avenir Next', 'Helvetica Neue', sans-serif;")
        title_lbl.setWordWrap(True)
        self.content_layout.addWidget(title_lbl)

        desc = proj.get("description") or "暂无详细描述信息。"
        desc_lbl = QLabel(desc)
        desc_lbl.setStyleSheet("color: #9aa7ba; font-size: 15px; line-height: 1.5;")
        desc_lbl.setWordWrap(True)
        self.content_layout.addWidget(desc_lbl)

        # Description Source tag
        desc_src = proj.get("description_source") or "GitHub repository description"
        src_lbl = QLabel(f"简介来源: {desc_src}")
        src_lbl.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New';")
        self.content_layout.addWidget(src_lbl)

        # 4. Action Button (GitHub 仓库 ↗)
        repo_url = proj.get("url") or proj.get("html_url") or f"https://github.com/{name}"
        gh_btn = QPushButton("GitHub 仓库 ↗")
        gh_btn.setCursor(Qt.PointingHandCursor)
        gh_btn.setFixedSize(140, 42)
        gh_btn.setStyleSheet("""
            QPushButton {
                background-color: #e3b341;
                color: #101827;
                font-weight: 600;
                font-size: 14px;
                border-radius: 21px;
                border: none;
            }
            QPushButton:hover {
                background-color: #f0c558;
            }
        """)
        gh_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(repo_url)))
        self.content_layout.addWidget(gh_btn)
        self.content_layout.addSpacing(10)

        # 5. KPI Metric Grid (2 rows x 4 columns matching Image 3)
        grid_layout = QGridLayout()
        grid_layout.setSpacing(16)

        stars = proj.get("stars", 0)
        forks = proj.get("forks", 0)
        lang = proj.get("language") or "未指定"
        created_at = fmt_date(proj.get("created_at")) or "—"
        updated_at = fmt_date(proj.get("pushed_at") or proj.get("updated_at")) or "—"
        latest_rel = fmt_release(proj.get("latest_release"))
        owner_type = proj.get("owner_type") or ("组织" if "/" in name else "个人")
        if owner_type == "User": owner_type = "个人"
        elif owner_type == "Organization": owner_type = "组织"

        metrics_items = [
            (fmt_num(stars), "Stars"),
            (fmt_num(forks), "Forks"),
            (lang, "主语言"),
            (license_str, "许可证"),
            (created_at, "上线时间"),
            (updated_at, "最后更新"),
            (latest_rel, "最新 Release"),
            (owner_type, "Owner 类型"),
        ]

        for i, (val, lbl) in enumerate(metrics_items):
            card = MetricCard(val, lbl)
            row = i // 4
            col = i % 4
            grid_layout.addWidget(card, row, col)

        self.content_layout.addLayout(grid_layout)

        # 6. README Excerpt if available
        readme = proj.get("readme_excerpt")
        if readme:
            self.content_layout.addSpacing(16)
            readme_card = QFrame()
            readme_card.setStyleSheet("""
                QFrame {
                    background-color: #101827;
                    border: 1px solid rgba(158, 178, 205, 0.12);
                    border-radius: 12px;
                    padding: 20px;
                }
            """)
            rc_layout = QVBoxLayout(readme_card)
            rc_layout.setSpacing(12)

            rc_title = QLabel("README 摘要")
            rc_title.setStyleSheet("color: #ece5d6; font-size: 16px; font-weight: bold;")
            rc_layout.addWidget(rc_title)

            rc_text = QLabel()
            rc_text.setStyleSheet("color: #9aa7ba; font-size: 13px; line-height: 1.6;")
            rc_text.setWordWrap(True)
            rc_text.setTextFormat(Qt.MarkdownText)
            rc_text.setText(str(readme))
            rc_layout.addWidget(rc_text)

            self.content_layout.addWidget(readme_card)

        self.content_layout.addStretch()
