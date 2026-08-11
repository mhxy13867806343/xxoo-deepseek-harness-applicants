from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.data_loader import (data_store, INTENT_LABELS, IDENTITY_LABELS, fmt_num, filter_developers)
from gui.components.widgets import SearchBox, PagerWidget, DeveloperCard

class DevelopersView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ''
        self.intent = 'all'
        self.identity = 'all'
        self.has_project = 'all'
        self.page = 1
        self.PAGE_SIZE = 24
        
        self.filtered_devs = []

        self._setup_ui()
        
        self.debounce_timer = QTimer(self)
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.setInterval(200)
        self.debounce_timer.timeout.connect(self._apply_filters)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(8)
        
        kicker = QLabel("DEVELOPERS")
        kicker.setStyleSheet("color: #e3b341; font-family: 'Menlo', 'Courier New'; font-size: 11px; letter-spacing: 1px;")
        header_layout.addWidget(kicker)
        
        title = QLabel("开发者目录")
        title.setStyleSheet("color: #ece5d6; font-size: 22px; font-weight: bold;")
        header_layout.addWidget(title)
        
        desc = QLabel("以开发者为中心。「未确认」表示来源未显式给出 GitHub 身份，不是数据错误。")
        desc.setStyleSheet("color: #9aa7ba; font-size: 13px;")
        desc.setWordWrap(True)
        header_layout.addWidget(desc)
        
        main_layout.addLayout(header_layout)

        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(12)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索 X / GitHub / 姓名 / 摘录…")
        self.search_input.setStyleSheet("""
            QLineEdit {
                background-color: #101827;
                color: #ece5d6;
                border: 1px solid #2d3748;
                border-radius: 20px;
                padding: 8px 16px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 1px solid #e3b341;
            }
        """)
        self.search_input.textChanged.connect(self._on_search_changed)
        toolbar.addWidget(self.search_input, stretch=1)
        
        self.intent_combo = QComboBox()
        self.intent_combo.setStyleSheet(self._combo_style())
        for label, val in [('全部意图','all'), ('强报名','strong_application'), ('报名','application'), ('仅兴趣','interest_only'), ('仅主页','profile_only'), ('灌水/评论','noise_or_comment'), ('机器人','bot'), ('未知','unknown')]:
            self.intent_combo.addItem(label, val)
        self.intent_combo.currentIndexChanged.connect(self._on_combo_changed)
        toolbar.addWidget(self.intent_combo)
        
        self.identity_combo = QComboBox()
        self.identity_combo.setStyleSheet(self._combo_style())
        for label, val in [('全部身份','all'), ('显式确认','explicit'), ('来源映射','mapped'), ('未确认','unconfirmed')]:
            self.identity_combo.addItem(label, val)
        self.identity_combo.currentIndexChanged.connect(self._on_combo_changed)
        toolbar.addWidget(self.identity_combo)
        
        self.has_project_combo = QComboBox()
        self.has_project_combo.setStyleSheet(self._combo_style())
        for label, val in [('全部','all'), ('有代表项目','yes'), ('无代表项目','no')]:
            self.has_project_combo.addItem(label, val)
        self.has_project_combo.currentIndexChanged.connect(self._on_combo_changed)
        toolbar.addWidget(self.has_project_combo)
        
        main_layout.addLayout(toolbar)

        # Result meta
        self.meta_label = QLabel("共 0 位开发者")
        self.meta_label.setStyleSheet("color: #67758c; font-family: 'Menlo', 'Courier New'; font-size: 12px;")
        main_layout.addWidget(self.meta_label)

        # Scrollable grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QWidget#scroll_content {
                background: transparent;
            }
        """)
        
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.grid_layout = QGridLayout(self.scroll_content)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area, stretch=1)

        # Pager
        self.pager = PagerWidget()
        self.pager.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.pager, alignment=Qt.AlignCenter)

    def _combo_style(self):
        return """
            QComboBox {
                background-color: #101827;
                color: #ece5d6;
                border: 1px solid #2d3748;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 13px;
                min-width: 100px;
            }
            QComboBox:focus {
                border: 1px solid #e3b341;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox QAbstractItemView {
                background-color: #101827;
                color: #ece5d6;
                selection-background-color: #2d3748;
            }
        """

    def _on_search_changed(self, text):
        self.query = text.strip()
        self.page = 1
        self.debounce_timer.start()

    def _on_combo_changed(self):
        self.intent = self.intent_combo.currentData()
        self.identity = self.identity_combo.currentData()
        self.has_project = self.has_project_combo.currentData()
        self.page = 1
        self._apply_filters()

    def _on_page_changed(self, page):
        self.page = page
        self._apply_filters()

    def refresh(self):
        self._apply_filters()

    def _apply_filters(self):
        self.filtered_devs = filter_developers(
            data_store.developers,
            query=self.query,
            intent=self.intent,
            identity=self.identity,
            has_project=self.has_project
        )
        
        total = len(self.filtered_devs)
        self.meta_label.setText(f"共 {fmt_num(total)} 位开发者")
        
        self.pager.update_state(total, self.PAGE_SIZE, self.page)
        
        start_idx = (self.page - 1) * self.PAGE_SIZE
        end_idx = start_idx + self.PAGE_SIZE
        devs_slice = self.filtered_devs[start_idx:end_idx]
        
        self._rebuild_cards(devs_slice)

    def _rebuild_cards(self, devs_slice):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        for i, dev in enumerate(devs_slice):
            row = i // 3
            col = i % 3
            card = DeveloperCard(dev)
            card.clicked.connect(lambda checked, d=dev: self.navigate_to.emit('developer_detail', {'x': d.get('x', '')}))
            self.grid_layout.addWidget(card, row, col)
