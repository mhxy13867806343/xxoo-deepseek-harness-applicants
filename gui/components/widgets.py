import math
from PyQt5.QtWidgets import (
    QWidget, QFrame, QLabel, QPushButton, QLineEdit, 
    QVBoxLayout, QHBoxLayout, QLayout, QSizePolicy, QStyle, QButtonGroup
)
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFontMetrics, QCursor, QFont
from PyQt5.QtCore import Qt, pyqtSignal, QRect, QPoint, QSize

from core.data_loader import (
    data_store, CATS, INTENT_LABELS, IDENTITY_LABELS, LANG_COLORS,
    fmt_num, fmt_k, fmt_date, cat_of
)

class FlowLayout(QLayout):
    def __init__(self, parent=None, margin=-1, hSpacing=-1, vSpacing=-1):
        super().__init__(parent)
        self.m_hSpace = hSpacing
        self.m_vSpace = vSpacing
        self.setContentsMargins(margin, margin, margin, margin)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def horizontalSpacing(self):
        if self.m_hSpace >= 0:
            return self.m_hSpace
        return self.smartSpacing(QStyle.PM_LayoutHorizontalSpacing)

    def verticalSpacing(self):
        if self.m_vSpace >= 0:
            return self.m_vSpace
        return self.smartSpacing(QStyle.PM_LayoutVerticalSpacing)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self.doLayout(QRect(0, 0, width, 0), True)

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.doLayout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        margin, _, _, _ = self.getContentsMargins()
        size += QSize(2 * margin, 2 * margin)
        return size

    def doLayout(self, rect, testOnly):
        x = rect.x()
        y = rect.y()
        lineHeight = 0

        for item in self.itemList:
            spaceX = self.horizontalSpacing()
            spaceY = self.verticalSpacing()
            nextX = x + item.sizeHint().width() + spaceX
            if nextX - spaceX > rect.right() and lineHeight > 0:
                x = rect.x()
                y = y + lineHeight + spaceY
                nextX = x + item.sizeHint().width() + spaceX
                lineHeight = 0

            if not testOnly:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))

            x = nextX
            lineHeight = max(lineHeight, item.sizeHint().height())

        return y + lineHeight - rect.y()

    def smartSpacing(self, pm):
        parent = self.parent()
        if not parent:
            return -1
        elif parent.isWidgetType():
            return parent.style().pixelMetric(pm, None, parent)
        return -1


class KPIWidget(QFrame):
    def __init__(self, value: str, label: str):
        super().__init__()
        self.setFixedWidth(180)
        self.setProperty("cssClass", "kpiCard")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(4)
        
        self.num_label = QLabel(value)
        self.num_label.setObjectName("kpiNum")
        self.num_label.setProperty("cssClass", "kpiNum")
        self.num_label.setAlignment(Qt.AlignCenter)
        
        self.text_label = QLabel(label)
        self.text_label.setObjectName("kpiLabel")
        self.text_label.setProperty("cssClass", "kpiLabel")
        self.text_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.num_label)
        layout.addWidget(self.text_label)

    def set_value(self, val: str):
        self.num_label.setText(str(val))

    def set_label(self, lbl: str):
        self.text_label.setText(str(lbl))


class SearchBox(QLineEdit):
    def __init__(self, placeholder="Search..."):
        super().__init__()
        self.setObjectName("searchBox")
        self.setProperty("cssClass", "searchBox")
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)


class ChipRow(QWidget):
    chip_changed = pyqtSignal(str)
    chip_clicked = pyqtSignal(str)  # alias for compatibility

    def __init__(self, items=None, parent=None):
        super().__init__(parent)
        self._flow = FlowLayout(self, margin=0, hSpacing=8, vSpacing=8)
        self.button_group = QButtonGroup(self)
        self.button_group.setExclusive(True)
        self.button_group.buttonClicked.connect(self._on_chip_clicked)

        if items:
            self._add_items(items)

    def _add_items(self, items):
        for item in items:
            val = item[0]
            label = item[1]
            raw_count = item[2] if len(item) > 2 else None
            if raw_count is not None and str(raw_count).strip() not in ("", "-1"):
                text = f"{label} {raw_count}"
            else:
                text = label
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setProperty("cssClass", "chip")
            btn.setProperty("chipValue", val)
            btn.setStyleSheet("""
                QPushButton { background: transparent; border: 1px solid rgba(158,178,205,0.10);
                    color: #67758c; border-radius: 14px; padding: 4px 12px; font-size: 12px; }
                QPushButton:hover { border-color: rgba(158,178,205,0.22); color: #ece5d6; }
                QPushButton:checked { background: rgba(227,179,65,0.12); border-color: #e3b341; color: #e3b341; }
            """)
            btn.setCursor(Qt.PointingHandCursor)
            self.button_group.addButton(btn)
            self._flow.addWidget(btn)
            if val == "" or val == "all":
                btn.setChecked(True)

    def set_chips(self, items):
        """Dynamically set/replace chips."""
        # Clear existing
        for btn in self.button_group.buttons():
            self.button_group.removeButton(btn)
            self._flow.removeWidget(btn)
            btn.deleteLater()
        self._add_items(items)

    def set_active(self, value):
        """Set the active chip by value."""
        for btn in self.button_group.buttons():
            if btn.property("chipValue") == value:
                btn.setChecked(True)
                break

    def _on_chip_clicked(self, button):
        val = button.property("chipValue")
        self.chip_changed.emit(val)
        self.chip_clicked.emit(val)


class PagerWidget(QWidget):
    page_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)
        self.layout.setAlignment(Qt.AlignCenter)
        self.info_label = QLabel()
        self.info_label.setProperty("cssClass", "pagerInfo")
        self.buttons = []
        self.current_page = 1
        self.total_pages = 1

    def set_state(self, page: int, total_pages: int, total_items: int = 0):
        import math
        self.current_page = max(1, page)
        self.total_pages = max(1, total_pages)
        
        # Clear layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if total_items > 0:
            self.info_label = QLabel(f"共 {total_items} 条")
            self.info_label.setProperty("cssClass", "pagerInfo")
            self.layout.addWidget(self.info_label)
            self.layout.addSpacing(16)
        
        # Prev button
        prev_btn = QPushButton("←")
        prev_btn.setProperty("cssClass", "pagerBtn")
        prev_btn.setCursor(Qt.PointingHandCursor)
        prev_btn.setEnabled(page > 1)
        prev_btn.setStyleSheet("""
            QPushButton {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.15);
                color: #9aa7ba;
                border-radius: 6px;
                min-width: 32px;
                min-height: 32px;
                font-size: 13px;
            }
            QPushButton:hover { border-color: #e3b341; color: #ece5d6; }
            QPushButton:disabled { color: rgba(103, 117, 140, 0.3); border-color: rgba(158, 178, 205, 0.05); }
        """)
        prev_btn.clicked.connect(lambda: self.page_changed.emit(self.current_page - 1))
        self.layout.addWidget(prev_btn)
        
        # Page buttons (simplified logic for ...)
        for i in range(1, total_pages + 1):
            if i == 1 or i == total_pages or abs(i - page) <= 2:
                btn = QPushButton(str(i))
                btn.setCursor(Qt.PointingHandCursor)
                if i == page:
                    btn.setProperty("cssClass", "pagerBtnActive")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: rgba(227, 179, 65, 0.22);
                            border: 1px solid #e3b341;
                            color: #e3b341;
                            font-weight: bold;
                            border-radius: 6px;
                            min-width: 32px;
                            min-height: 32px;
                            font-size: 13px;
                        }
                    """)
                else:
                    btn.setProperty("cssClass", "pagerBtn")
                    btn.setStyleSheet("""
                        QPushButton {
                            background-color: #101827;
                            border: 1px solid rgba(158, 178, 205, 0.15);
                            color: #9aa7ba;
                            border-radius: 6px;
                            min-width: 32px;
                            min-height: 32px;
                            font-size: 13px;
                        }
                        QPushButton:hover { border-color: #e3b341; color: #ece5d6; }
                    """)
                btn.clicked.connect(lambda checked, p=i: self.page_changed.emit(p))
                self.layout.addWidget(btn)
            elif abs(i - page) == 3:
                lbl = QLabel("...")
                lbl.setStyleSheet("color: #67758c; padding: 0 4px;")
                lbl.setProperty("cssClass", "pagerEllipsis")
                self.layout.addWidget(lbl)
                
        # Next button
        next_btn = QPushButton("→")
        next_btn.setProperty("cssClass", "pagerBtn")
        next_btn.setCursor(Qt.PointingHandCursor)
        next_btn.setEnabled(page < total_pages)
        next_btn.setStyleSheet("""
            QPushButton {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.15);
                color: #9aa7ba;
                border-radius: 6px;
                min-width: 32px;
                min-height: 32px;
                font-size: 13px;
            }
            QPushButton:hover { border-color: #e3b341; color: #ece5d6; }
            QPushButton:disabled { color: rgba(103, 117, 140, 0.3); border-color: rgba(158, 178, 205, 0.05); }
        """)
        next_btn.clicked.connect(lambda: self.page_changed.emit(self.current_page + 1))
        self.layout.addWidget(next_btn)

    def set_total(self, total_items: int, page_size: int, page: int):
        import math
        total_pages = max(1, math.ceil(total_items / max(1, page_size)))
        self.set_state(page, total_pages, total_items)

    def update_state(self, total_items: int, page_size: int, page: int):
        self.set_total(total_items, page_size, page)

    def set_total_pages(self, total_pages: int, page: int):
        self.set_state(page, total_pages, 0)


class LangDot(QWidget):
    def __init__(self, lang: str, parent=None):
        super().__init__(parent)
        self.setFixedSize(8, 8)
        self.color_hex = LANG_COLORS.get(lang, "#9aa7ba")
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(self.color_hex)
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 8, 8)


class BadgeLabel(QLabel):
    def __init__(self, text: str, style: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("cssClass", f"badge {style}".strip())


class ProjectCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, project: dict, parent=None):
        super().__init__(parent)
        self.project_data = project
        self.setFixedHeight(160)
        self.setProperty("cssClass", "card")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        
        # Header row
        header_layout = QHBoxLayout()
        self.name_lbl = QLabel(project.get("name", ""))
        self.name_lbl.setProperty("cssClass", "cardTitle")
        
        stars = project.get("stars", 0)
        self.stars_lbl = QLabel(f"★ {fmt_k(stars)}")
        self.stars_lbl.setProperty("cssClass", "cardStars")
        
        header_layout.addWidget(self.name_lbl)
        header_layout.addStretch()
        header_layout.addWidget(self.stars_lbl)
        layout.addLayout(header_layout)
        
        # Desc
        self.desc_lbl = QLabel(project.get("description", ""))
        self.desc_lbl.setProperty("cssClass", "cardDesc")
        self.desc_lbl.setWordWrap(True)
        self.desc_lbl.setMinimumHeight(40)
        self.desc_lbl.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.desc_lbl)
        
        layout.addStretch()
        
        # Footer
        footer_layout = QHBoxLayout()
        footer_layout.setSpacing(8)
        
        lang = project.get("language", "")
        if lang:
            footer_layout.addWidget(LangDot(lang))
            lang_lbl = QLabel(lang)
            lang_lbl.setProperty("cssClass", "cardLang")
            footer_layout.addWidget(lang_lbl)
            
        cat = project.get("category", "unclassified")
        cat_zh = CATS.get(cat, {}).get("zh", cat)
        footer_layout.addWidget(BadgeLabel(cat_zh, "blue"))
        
        if project.get("deepseek_native") or project.get("is_deepseek_native"):
            footer_layout.addWidget(BadgeLabel("DS Native", "gold"))
            
        footer_layout.addStretch()
        
        applicant = project.get("applicant_x") or project.get("applicant_github") or project.get("applicant") or project.get("x_handle", "")
        if applicant:
            app_lbl = QLabel(f"@{applicant}")
            app_lbl.setProperty("cssClass", "cardApplicant")
            footer_layout.addWidget(app_lbl)
            
        layout.addLayout(footer_layout)

    def update_project(self, project: dict):
        self.project_data = project
        self.name_lbl.setText(project.get("name", ""))
        stars = project.get("stars", 0)
        self.stars_lbl.setText(f"★ {fmt_k(stars)}")
        self.desc_lbl.setText(project.get("description", ""))
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.project_data.get("name", ""))


class DeveloperCard(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, developer: dict, parent=None):
        super().__init__(parent)
        self.dev_data = developer
        self.setFixedHeight(120)
        self.setProperty("cssClass", "card")
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(12)
        
        # Avatar placeholder
        self.avatar = QLabel()
        self.avatar.setFixedSize(48, 48)
        self.avatar.setProperty("cssClass", "avatarPlaceholder")
        self.avatar.setAlignment(Qt.AlignCenter)
        name = developer.get("name") or developer.get("id", "")
        first_char = name[0].upper() if name else "?"
        self.avatar.setText(first_char)
        layout.addWidget(self.avatar)
        
        # Info col
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        # Top row: Name, handle, github
        top_row = QHBoxLayout()
        name_lbl = QLabel(name)
        name_lbl.setProperty("cssClass", "devName")
        top_row.addWidget(name_lbl)
        
        handle = developer.get("x") or developer.get("x_handle", "")
        if handle:
            handle_lbl = QLabel(f"@{handle}")
            handle_lbl.setProperty("cssClass", "devHandle")
            top_row.addWidget(handle_lbl)
        
        gh = developer.get("github") or developer.get("github_username", "")
        gh_text = f"github.com/{gh}" if gh else "GitHub 未确认"
        gh_lbl = QLabel(gh_text)
        gh_lbl.setProperty("cssClass", "devGithub")
        top_row.addWidget(gh_lbl)
        
        top_row.addStretch()
        info_layout.addLayout(top_row)
        
        # Badges row
        badges_row = QHBoxLayout()
        intent = developer.get("intent", "unknown")
        intent_text = INTENT_LABELS.get(intent, intent)
        badges_row.addWidget(BadgeLabel(intent_text, "blue"))
        
        identity = developer.get("identity_confidence") or developer.get("identity") or "unconfirmed"
        identity_text = IDENTITY_LABELS.get(identity, identity)
        badges_row.addWidget(BadgeLabel(identity_text, "green"))
        
        badges_row.addStretch()
        info_layout.addLayout(badges_row)
        
        # Excerpt
        excerpt = developer.get("excerpt") or developer.get("bio") or developer.get("description", "")
        if excerpt:
            excerpt_lbl = QLabel(excerpt)
            excerpt_lbl.setProperty("cssClass", "devExcerpt")
            metrics = QFontMetrics(excerpt_lbl.font())
            elided = metrics.elidedText(excerpt, Qt.ElideRight, 380)
            excerpt_lbl.setText(elided)
            info_layout.addWidget(excerpt_lbl)
            
        info_layout.addStretch()
        
        # Bottom right: project count + stars
        bottom_row = QHBoxLayout()
        bottom_row.addStretch()
        p_count = developer.get("project_count") or len(developer.get("projects") or [])
        projects = developer.get("projects") or []
        stars_list = [p.get("stars", 0) for p in projects if isinstance(p, dict)]
        t_stars = max(stars_list) if stars_list else developer.get("top_stars", 0)
        
        stats_lbl = QLabel(f"{p_count} Projects • Top ★ {fmt_k(t_stars)}")
        stats_lbl.setProperty("cssClass", "devStats")
        bottom_row.addWidget(stats_lbl)
        
        info_layout.addLayout(bottom_row)
        layout.addLayout(info_layout, 1)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.dev_data.get("x_handle", ""))


class BarChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.max_val = 0

    def set_data(self, items, colors=None):
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not items:
            return

        formatted_items = []
        for i, item in enumerate(items):
            if len(item) == 3:
                label_text, value, color = item
            elif len(item) == 2:
                label_text, value = item
                color = colors[i] if colors and i < len(colors) else "#82a8cf"
            else:
                continue
            formatted_items.append((label_text, value, color))

        if not formatted_items:
            return
            
        self.max_val = max(item[1] for item in formatted_items) if formatted_items else 1
        if self.max_val == 0:
            self.max_val = 1
            
        for label_text, value, color in formatted_items:
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)
            
            lbl = QLabel(str(label_text))
            lbl.setProperty("cssClass", "barLabel")
            lbl.setFixedWidth(120)
            row_layout.addWidget(lbl)
            
            bar_container = QWidget()
            bar_container.setFixedHeight(12)
            bar_layout = QHBoxLayout(bar_container)
            bar_layout.setContentsMargins(0, 0, 0, 0)
            bar_layout.setSpacing(0)
            
            bar = QFrame()
            bar.setFixedHeight(12)
            bar.setStyleSheet(f"background-color: {color}; border-radius: 2px;")
            # Proportional width logic via stretch
            pct = int((value / self.max_val) * 100)
            
            bar_layout.addWidget(bar, pct)
            bar_layout.addStretch(100 - pct)
            
            row_layout.addWidget(bar_container, 1)
            
            val_lbl = QLabel(str(value))
            val_lbl.setProperty("cssClass", "barValue")
            val_lbl.setFixedWidth(40)
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.layout.addWidget(row)


class LoadingOverlay(QFrame):
    """Sleek semi-transparent loading overlay with spinner/text."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame#loadingOverlay {
                background-color: rgba(10, 14, 23, 0.78);
                border: none;
            }
        """)
        self.setObjectName("loadingOverlay")
        self.hide()

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)

        card = QFrame()
        card.setFixedSize(300, 110)
        card.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(227, 179, 65, 0.4);
                border-radius: 14px;
            }
        """)
        c_layout = QVBoxLayout(card)
        c_layout.setAlignment(Qt.AlignCenter)
        c_layout.setSpacing(8)

        self.spinner_lbl = QLabel("🔄")
        self.spinner_lbl.setStyleSheet("font-size: 24px;")
        self.spinner_lbl.setAlignment(Qt.AlignCenter)

        self.text_lbl = QLabel("正在加载数据...")
        self.text_lbl.setStyleSheet("color: #ece5d6; font-size: 13px; font-weight: bold;")
        self.text_lbl.setAlignment(Qt.AlignCenter)

        c_layout.addWidget(self.spinner_lbl)
        c_layout.addWidget(self.text_lbl)
        layout.addWidget(card)

    def show_loading(self, text="正在加载数据..."):
        self.text_lbl.setText(text)
        if self.parent():
            self.resize(self.parent().size())
            self.raise_()
        self.show()

    def hide_loading(self):
        self.hide()


class MetricCard(QFrame):
    """Square KPI metric card matching the design of Image 3."""

    def __init__(self, value_text: str, label_text: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.12);
                border-radius: 10px;
                padding: 16px;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(6)

        val_lbl = QLabel(str(value_text))
        val_lbl.setStyleSheet("color: #ece5d6; font-size: 20px; font-weight: bold; font-family: 'Menlo', 'Courier New';")
        
        sub_lbl = QLabel(label_text)
        sub_lbl.setStyleSheet("color: #67758c; font-size: 12px;")

        layout.addWidget(val_lbl)
        layout.addWidget(sub_lbl)
