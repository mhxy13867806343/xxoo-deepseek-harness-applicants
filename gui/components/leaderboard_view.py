from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.data_loader import data_store, CATS, LANG_COLORS, fmt_num, fmt_date, cat_of, sort_projects
from gui.components.widgets import ChipRow, PagerWidget, BadgeLabel

class LeaderboardView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cat = ''
        self.sort = 'stars'
        self.ds_only = False
        self.page = 1
        self.PAGE_SIZE = 50

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # 1. Page header
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        kicker = QLabel("LEADERBOARD")
        kicker.setStyleSheet("color: #e3b341; font-family: 'Menlo', 'Courier New'; font-size: 11px; letter-spacing: 1px;")
        
        title = QLabel("项目排行榜")
        title.setStyleSheet("color: #ece5d6; font-size: 22px; font-weight: bold;")
        
        desc = QLabel("浏览所有的开源项目，按照 Starts、更新时间等排序，发现热门智能体应用。")
        desc.setStyleSheet("color: #9aa7ba; font-size: 14px;")
        
        header_layout.addWidget(kicker)
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        layout.addLayout(header_layout)

        # 2. Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)

        self.sort_group = QButtonGroup(self)
        self.sort_group.setExclusive(True)
        
        self.btn_sort_stars = QPushButton("按 Stars")
        self.btn_sort_stars.setCheckable(True)
        self.btn_sort_stars.setChecked(True)
        self.btn_sort_updated = QPushButton("最近更新")
        self.btn_sort_updated.setCheckable(True)
        self.btn_sort_created = QPushButton("上线时间")
        self.btn_sort_created.setCheckable(True)

        self.sort_group.addButton(self.btn_sort_stars, 0)
        self.sort_group.addButton(self.btn_sort_updated, 1)
        self.sort_group.addButton(self.btn_sort_created, 2)
        
        self.sort_group.buttonClicked.connect(self._on_sort_changed)

        for btn in [self.btn_sort_stars, self.btn_sort_updated, self.btn_sort_created]:
            btn.setCursor(Qt.PointingHandCursor)
            toolbar.addWidget(btn)

        self.chk_ds_only = QCheckBox("仅 DeepSeek 相关")
        self.chk_ds_only.setCursor(Qt.PointingHandCursor)
        self.chk_ds_only.setStyleSheet("color: #ece5d6;")
        self.chk_ds_only.stateChanged.connect(self._on_ds_changed)
        toolbar.addWidget(self.chk_ds_only)

        toolbar.addStretch()

        self.lbl_count = QLabel("0 results")
        self.lbl_count.setStyleSheet("color: #67758c; font-family: 'Menlo', 'Courier New'; font-size: 12px;")
        toolbar.addWidget(self.lbl_count)
        
        layout.addLayout(toolbar)

        # 3. Category chips
        self.chips = ChipRow()
        self.chips.chip_clicked.connect(self.set_category)
        layout.addWidget(self.chips)

        # 4. QTableWidget
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["#", "项目", "Stars", "语言", "赛道", "报名者", "上线", "更新"])
        self.table.horizontalHeader().setVisible(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setShowGrid(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setFocusPolicy(Qt.NoFocus)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        self.table.setColumnWidth(0, 50)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        for i, width in [(2, 80), (3, 80), (4, 100), (5, 100), (6, 90), (7, 90)]:
            header.setSectionResizeMode(i, QHeaderView.Fixed)
            self.table.setColumnWidth(i, width)

        self.table.setStyleSheet('''
            QTableWidget {
                background-color: #101827;
                color: #ece5d6;
                gridline-color: rgba(158, 178, 205, 0.10);
                border: 1px solid rgba(158, 178, 205, 0.10);
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 4px;
                border-bottom: 1px solid rgba(158, 178, 205, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(227, 179, 65, 0.1);
            }
            QHeaderView::section {
                background-color: #141e2f;
                color: #9aa7ba;
                padding: 4px;
                border: none;
                border-bottom: 1px solid rgba(158, 178, 205, 0.10);
                font-weight: bold;
            }
        ''')
        
        self.table.cellClicked.connect(self._on_table_clicked)
        layout.addWidget(self.table, 1)

        # 5. PagerWidget
        self.pager = PagerWidget()
        self.pager.page_changed.connect(self._on_page_changed)
        layout.addWidget(self.pager)

    def refresh(self):
        # Populate chips
        cat_stats = data_store.stats.get('category_stats', {})
        def _cnt(v):
            if isinstance(v, dict):
                return v.get('count', 0)
            return v if isinstance(v, (int, float)) else 0
        sorted_cats = sorted(cat_stats.items(), key=lambda x: _cnt(x[1]), reverse=True)
        
        chip_items = [("all", "全部", "")]
        for c, val in sorted_cats:
            count = _cnt(val)
            if c in CATS:
                chip_items.append((c, CATS[c]["zh"], str(count)))
        
        self.chips.set_chips(chip_items)
        self.chips.set_active(self.cat if self.cat else "all")
        
        self._apply_filters()

    def set_category(self, cat_id):
        if cat_id == "all":
            cat_id = ""
        self.cat = cat_id
        self.page = 1
        self.chips.set_active(cat_id if cat_id else "all")
        self._apply_filters()

    def _on_sort_changed(self, btn):
        if btn == self.btn_sort_stars:
            self.sort = 'stars'
        elif btn == self.btn_sort_updated:
            self.sort = 'updated'
        elif btn == self.btn_sort_created:
            self.sort = 'created'
        self.page = 1
        self._apply_filters()

    def _on_ds_changed(self, state):
        self.ds_only = (state == Qt.Checked)
        self.page = 1
        self._apply_filters()
        
    def _on_page_changed(self, new_page):
        self.page = new_page
        self._apply_filters()

    def _on_table_clicked(self, row, col):
        item = self.table.item(row, 1)
        if item:
            repo_id = item.data(Qt.UserRole) or item.text()
            proj = data_store.get_project(repo_id)
            if proj:
                self.navigate_to.emit('project_detail', proj)
            else:
                self.navigate_to.emit('project_detail', {'name': repo_id})

    def _apply_filters(self):
        projects = data_store.projects
        
        if self.cat:
            projects = [p for p in projects if (p.get('category') or p.get('cat')) == self.cat]
            
        if self.ds_only:
            projects = [p for p in projects if p.get('deepseek_native', False) or p.get('ds_related', False) or p.get('relevance') == 'strong']
            
        projects = sort_projects(projects, self.sort)
        
        total_count = len(projects)
        self.lbl_count.setText(f"{total_count} results")
        
        start_idx = (self.page - 1) * self.PAGE_SIZE
        end_idx = start_idx + self.PAGE_SIZE
        page_projects = projects[start_idx:end_idx]
        
        self.pager.set_total(total_count, self.PAGE_SIZE, self.page)
        
        self.table.setRowCount(len(page_projects))
        
        for row, proj in enumerate(page_projects):
            # Rank
            rank = start_idx + row + 1
            item_rank = QTableWidgetItem(str(rank))
            item_rank.setTextAlignment(Qt.AlignCenter)
            if rank == 1:
                item_rank.setForeground(QColor("#e3b341"))
                item_rank.setFont(QFont("Menlo", 12, QFont.Bold))
            elif rank == 2:
                item_rank.setForeground(QColor("#b9c6d6"))
                item_rank.setFont(QFont("Menlo", 12, QFont.Bold))
            elif rank == 3:
                item_rank.setForeground(QColor("#c08a5a"))
                item_rank.setFont(QFont("Menlo", 12, QFont.Bold))
            else:
                item_rank.setForeground(QColor("#67758c"))
                item_rank.setFont(QFont("Menlo", 10))
            
            # Project name
            full_name = proj.get('name') or proj.get('repo_id') or proj.get('repo') or 'Unknown'
            item_name = QTableWidgetItem(full_name)
            item_name.setData(Qt.UserRole, full_name)
            
            # Stars
            stars = proj.get('stars', 0)
            item_stars = QTableWidgetItem(fmt_num(stars))
            item_stars.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item_stars.setFont(QFont("Menlo"))
            
            # Language
            lang = proj.get('language') or 'Unknown'
            color = LANG_COLORS.get(lang, '#9aa7ba')
            item_lang = QTableWidgetItem(f"● {lang}")
            item_lang.setForeground(QColor(color))
            
            # Category
            cat_info = cat_of(proj)
            cat_name = cat_info.get('zh', '未知') if isinstance(cat_info, dict) else str(cat_info)
            item_cat = QTableWidgetItem(cat_name)
            item_cat.setForeground(QColor("#9aa7ba"))
            
            # Applicant
            applicant = proj.get('applicant_x') or proj.get('applicant_github') or proj.get('applicant') or 'Unknown'
            item_applicant = QTableWidgetItem(applicant)
            
            # Created / Updated
            item_created = QTableWidgetItem(fmt_date(proj.get('created_at')))
            item_created.setFont(QFont("Menlo"))
            item_created.setForeground(QColor("#9aa7ba"))
            item_updated = QTableWidgetItem(fmt_date(proj.get('updated_at')))
            item_updated.setFont(QFont("Menlo"))
            item_updated.setForeground(QColor("#9aa7ba"))
            
            self.table.setItem(row, 0, item_rank)
            self.table.setItem(row, 1, item_name)
            self.table.setItem(row, 2, item_stars)
            self.table.setItem(row, 3, item_lang)
            self.table.setItem(row, 4, item_cat)
            self.table.setItem(row, 5, item_applicant)
            self.table.setItem(row, 6, item_created)
            self.table.setItem(row, 7, item_updated)
