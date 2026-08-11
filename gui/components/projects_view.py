import math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.data_loader import (data_store, CATS, fmt_num, fmt_k, cat_of, sort_projects, filter_projects, LANG_COLORS)
from gui.components.widgets import SearchBox, ChipRow, PagerWidget, ProjectCard

class ProjectsView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.query = ''
        self.cat = ''
        self.lang = ''
        self.sort = 'stars'
        self.ds_only = False
        self.high_only = False
        self.home_only = False
        self.page = 1
        self.PAGE_SIZE = 24
        
        self.search_timer = QTimer(self)
        self.search_timer.setSingleShot(True)
        self.search_timer.setInterval(200)
        self.search_timer.timeout.connect(self._on_search_timeout)
        
        self._init_ui()
        
    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)
        
        # 1. Header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(5)
        
        kicker = QLabel("PROJECTS")
        kicker.setStyleSheet("color: #e3b341; font-weight: bold; font-size: 12px; letter-spacing: 2px;")
        
        title = QLabel("项目目录")
        title.setStyleSheet("color: #ece5d6; font-weight: bold; font-size: 28px;")
        
        desc = QLabel("浏览所有的智能体框架、工具和相关项目。")
        desc.setStyleSheet("color: #9aa7ba; font-size: 14px;")
        
        header_layout.addWidget(kicker)
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        main_layout.addLayout(header_layout)
        
        # 2. Toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setSpacing(10)
        
        self.search_input = SearchBox()
        self.search_input.setPlaceholderText("搜索项目名、描述、报名者…")
        self.search_input.textChanged.connect(self._on_search_changed)
        
        self.lang_combo = QComboBox()
        self.lang_combo.setStyleSheet("""
            QComboBox {
                background-color: #101827;
                color: #ece5d6;
                border: 1px solid #2d3748;
                border-radius: 4px;
                padding: 4px 8px;
            }
            QComboBox::drop-down { border: none; }
        """)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(['Stars 高→低', '最近更新', '上线时间', '名称 A→Z'])
        self.sort_combo.setStyleSheet(self.lang_combo.styleSheet())
        self.sort_combo.currentIndexChanged.connect(self._on_sort_changed)
        
        self.cb_ds = QCheckBox("DeepSeek")
        self.cb_ds.setStyleSheet("color: #ece5d6;")
        self.cb_ds.stateChanged.connect(self._on_filters_changed)
        
        self.cb_high = QCheckBox("高相关")
        self.cb_high.setStyleSheet("color: #ece5d6;")
        self.cb_high.stateChanged.connect(self._on_filters_changed)
        
        self.cb_home = QCheckBox("有主页")
        self.cb_home.setStyleSheet("color: #ece5d6;")
        self.cb_home.stateChanged.connect(self._on_filters_changed)
        
        toolbar_layout.addWidget(self.search_input, 1)
        toolbar_layout.addWidget(self.lang_combo)
        toolbar_layout.addWidget(self.sort_combo)
        toolbar_layout.addWidget(self.cb_ds)
        toolbar_layout.addWidget(self.cb_high)
        toolbar_layout.addWidget(self.cb_home)
        
        main_layout.addLayout(toolbar_layout)
        
        # 3. ChipRow
        self.chip_row = ChipRow()
        self.chip_row.chip_clicked.connect(self._on_cat_changed)
        main_layout.addWidget(self.chip_row)
        
        # 4. Result Meta
        self.meta_label = QLabel()
        self.meta_label.setStyleSheet("color: #67758c; font-family: 'Menlo', 'Courier New'; font-size: 12px;")
        main_layout.addWidget(self.meta_label)
        
        # 5. Scrollable Card Grid
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("QScrollArea { background: transparent; } QWidget#gridContainer { background: transparent; }")
        
        self.grid_container = QWidget()
        self.grid_container.setObjectName("gridContainer")
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setAlignment(Qt.AlignTop)
        
        self.scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(self.scroll_area, 1)
        
        # 6. Pager
        self.pager = PagerWidget()
        self.pager.page_changed.connect(self._on_page_changed)
        main_layout.addWidget(self.pager, 0, Qt.AlignCenter)
        
    def refresh(self):
        # Update combo boxes
        langs = list(data_store.stats.get('language_stats', {}).keys())
        self.lang_combo.blockSignals(True)
        self.lang_combo.clear()
        self.lang_combo.addItem("所有语言", "")
        for l in sorted([x for x in langs if x and x != '(none)']):
            self.lang_combo.addItem(l, l)
        if '(none)' in langs:
            self.lang_combo.addItem("未指定语言", "(none)")
        
        idx = self.lang_combo.findData(self.lang)
        if idx >= 0:
            self.lang_combo.setCurrentIndex(idx)
        else:
            self.lang_combo.setCurrentIndex(0)
            self.lang = ""
        self.lang_combo.blockSignals(False)
        
        # Update chips
        cat_stats = data_store.stats.get('category_stats', {})
        chip_items = [("all", "全部", "")]
        for c_id, val in cat_stats.items():
            count = val.get('count', 0) if isinstance(val, dict) else val
            c_info = cat_of(c_id)
            c_zh = c_info.get('zh', c_id) if isinstance(c_info, dict) else str(c_info)
            if c_id in CATS:
                chip_items.append((c_id, c_zh, str(count)))
        
        self.chip_row.set_chips(chip_items)
        self.chip_row.set_active(self.cat if self.cat else "all")
        
        self._apply_filters()
        
    def _on_search_changed(self, text):
        self.query = text.strip()
        self.search_timer.start()
        
    def _on_search_timeout(self):
        self.page = 1
        self._apply_filters()
        
    def _on_lang_changed(self, idx):
        if idx >= 0:
            self.lang = self.lang_combo.itemData(idx) or ""
        else:
            self.lang = ""
        self.page = 1
        self._apply_filters()
        
    def _on_sort_changed(self, idx):
        sort_map = {
            0: 'stars',
            1: 'updated',
            2: 'created',
            3: 'name'
        }
        self.sort = sort_map.get(idx, 'stars')
        self.page = 1
        self._apply_filters()
        
    def _on_filters_changed(self, state):
        self.ds_only = self.cb_ds.isChecked()
        self.high_only = self.cb_high.isChecked()
        self.home_only = self.cb_home.isChecked()
        self.page = 1
        self._apply_filters()
        
    def _on_cat_changed(self, cat_id):
        self.cat = '' if cat_id == 'all' else cat_id
        self.page = 1
        self._apply_filters()
        
    def _on_page_changed(self, page):
        self.page = page
        self._apply_filters()
        self.scroll_area.verticalScrollBar().setValue(0)
        
    def _apply_filters(self):
        # 1. Filter
        filtered = filter_projects(
            data_store.projects,
            query=self.query,
            cat=self.cat,
            lang=self.lang,
            ds_only=self.ds_only,
            high_only=self.high_only,
            home_only=self.home_only
        )
        
        # 2. Sort
        sorted_projects = sort_projects(filtered, by=self.sort)
        
        total = len(sorted_projects)
        total_pages = math.ceil(total / self.PAGE_SIZE) if total > 0 else 1
        if self.page > total_pages:
            self.page = total_pages
            
        start_idx = (self.page - 1) * self.PAGE_SIZE
        end_idx = start_idx + self.PAGE_SIZE
        slice_projects = sorted_projects[start_idx:end_idx]
        
        self.meta_label.setText(f"找到 {total} 个项目 (第 {self.page}/{total_pages} 页)")
        self.pager.set_total(total, self.PAGE_SIZE, self.page)
        
        self._rebuild_cards(slice_projects)
        
    def _rebuild_cards(self, projects_slice):
        # Clear grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
                
        # Rebuild
        for i, proj in enumerate(projects_slice):
            card = ProjectCard(proj)
            card.clicked.connect(self._on_card_clicked)
            col = i % 3
            row = i // 3
            self.grid_layout.addWidget(card, row, col)
            
    def _on_card_clicked(self):
        card = self.sender()
        if card and hasattr(card, 'project_data'):
            self.navigate_to.emit('project_detail', card.project_data)
