import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from core.data_loader import data_store, CATS, LANG_COLORS, TIER_META, GAP_META, fmt_num, fmt_k, fmt_date, cat_of, sort_projects
from gui.components.widgets import KPIWidget, ProjectCard, BarChartWidget, FlowLayout, BadgeLabel

class HomeView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scroll Area
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.NoFrame)
        self.scroll_area.setStyleSheet("QScrollArea { background-color: transparent; }")

        self.content_widget = QWidget()
        self.content_widget.setObjectName("HomeContent")
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setContentsMargins(40, 40, 40, 80)
        self.content_layout.setSpacing(60)

        self.scroll_area.setWidget(self.content_widget)
        main_layout.addWidget(self.scroll_area)

        # Setup sections
        self.setup_hero_section()
        self.setup_kpi_section()
        self.setup_top10_section()
        self.setup_tracks_section()
        self.setup_featured_section()
        self.setup_ecosystem_section()
        self.setup_gaps_section()

    def _create_section_header(self, kicker_text, title_text, btn_text=None, btn_target=None):
        header_layout = QVBoxLayout()
        header_layout.setSpacing(4)
        
        kicker = QLabel(kicker_text)
        kicker.setStyleSheet("color: #e3b341; font-family: 'Menlo', 'Courier New'; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        title_layout = QHBoxLayout()
        title = QLabel(title_text)
        title.setStyleSheet("color: #ece5d6; font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title)
        
        if btn_text:
            btn = QPushButton(btn_text)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("""
                QPushButton {
                    color: #9aa7ba; background: transparent; border: none; font-size: 14px;
                }
                QPushButton:hover { color: #e3b341; }
            """)
            if btn_target:
                btn.clicked.connect(lambda: self.navigate_to.emit(*btn_target))
            title_layout.addStretch()
            title_layout.addWidget(btn)
        else:
            title_layout.addStretch()

        header_layout.addWidget(kicker)
        header_layout.addLayout(title_layout)
        return header_layout

    def setup_hero_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        kicker = QLabel("COMMUNITY ARCHIVE")
        kicker.setStyleSheet("color: #e3b341; font-family: 'Menlo', 'Courier New'; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        
        title = QLabel("DeepSeek Harness\n内测报名档案库")
        title.setStyleSheet("color: #ece5d6; font-size: 36px; font-weight: bold; line-height: 1.2;")
        
        subtitle = QLabel("一场公开招募留下的生态切片：769 位报名者、712 个开源仓库...")
        subtitle.setStyleSheet("color: #9aa7ba; font-size: 16px;")
        
        btn_layout = QHBoxLayout()
        btn_primary = QPushButton("进入排行榜")
        btn_primary.setCursor(Qt.PointingHandCursor)
        btn_primary.setStyleSheet("""
            QPushButton {
                background-color: #e3b341; color: #0a0e17; font-weight: bold;
                border-radius: 4px; padding: 10px 24px; font-size: 14px;
            }
            QPushButton:hover { background-color: #f4c452; }
        """)
        btn_primary.clicked.connect(lambda: self.navigate_to.emit('leaderboard', {'cat': 'all'}))

        btn_ghost = QPushButton("浏览全部项目")
        btn_ghost.setCursor(Qt.PointingHandCursor)
        btn_ghost.setStyleSheet("""
            QPushButton {
                background-color: transparent; color: #ece5d6; font-weight: bold;
                border: 1px solid #67758c; border-radius: 4px; padding: 10px 24px; font-size: 14px;
            }
            QPushButton:hover { border-color: #ece5d6; }
        """)
        btn_ghost.clicked.connect(lambda: self.navigate_to.emit('projects', {}))
        
        btn_layout.addWidget(btn_primary)
        btn_layout.addWidget(btn_ghost)
        btn_layout.addStretch()

        warning = QLabel("社区维护的非官方档案，与 DeepSeek 无关。指标为快照时点数据，非实时。")
        warning.setStyleSheet("""
            QLabel {
                color: #9aa7ba; background-color: rgba(227, 179, 65, 0.1);
                border-left: 3px solid #e3b341; padding: 12px; font-size: 13px;
                border-top-right-radius: 4px; border-bottom-right-radius: 4px;
            }
        """)
        warning.setWordWrap(True)

        layout.addWidget(kicker)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(btn_layout)
        layout.addSpacing(16)
        layout.addWidget(warning)

        self.content_layout.addWidget(container)

    def setup_kpi_section(self):
        self.kpi_container = QWidget()
        self.kpi_layout = QHBoxLayout(self.kpi_container)
        self.kpi_layout.setSpacing(16)
        self.content_layout.addWidget(self.kpi_container)
        self.kpi_widgets = {}

        kpi_defs = [
            ('developers_count', '报名者'),
            ('unique_repos', '去重仓库'),
            ('stars_sum', 'Stars 合计'),
            ('with_github_username', '显式 GitHub 身份'),
            ('with_homepage', '解析到主页'),
            ('deepseek_native', 'DeepSeek-native 项目')
        ]
        for key, label in kpi_defs:
            w = KPIWidget(label, "0")
            self.kpi_widgets[key] = w
            self.kpi_layout.addWidget(w)

    def setup_top10_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        header = self._create_section_header('01 · TOP OF THE INDEX', 'Stars 总榜 · 前十', '完整榜单 →', ('leaderboard', {'cat': 'all'}))
        layout.addLayout(header)

        self.top10_table = QTableWidget(10, 7)
        self.top10_table.setHorizontalHeaderLabels(['#', '项目', 'Stars', '语言', '赛道', '报名者', '更新'])
        self.top10_table.horizontalHeader().setStretchLastSection(True)
        self.top10_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.top10_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.top10_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.top10_table.setShowGrid(False)
        self.top10_table.verticalHeader().setVisible(False)
        self.top10_table.cellClicked.connect(self.on_top10_clicked)
        self.top10_table.setFixedHeight(450) # Approx height for 10 rows
        
        self.top10_table.setStyleSheet("""
            QTableWidget {
                background-color: #121824;
                border: 1px solid #1e2638;
                border-radius: 8px;
                color: #ece5d6;
            }
            QHeaderView::section {
                background-color: #0a0e17;
                color: #9aa7ba;
                border: none;
                border-bottom: 1px solid #1e2638;
                padding: 8px;
                font-weight: bold;
            }
            QTableWidget::item {
                border-bottom: 1px solid #1e2638;
                padding: 8px;
            }
            QTableWidget::item:selected {
                background-color: rgba(227, 179, 65, 0.1);
            }
        """)

        layout.addWidget(self.top10_table)
        self.content_layout.addWidget(container)

    def setup_tracks_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        header = self._create_section_header('02 · TRACKS', '十八个赛道', '赛道索引 →', ('leaderboard', {'cat': 'all'}))
        layout.addLayout(header)

        self.tracks_grid = QGridLayout()
        self.tracks_grid.setSpacing(16)
        layout.addLayout(self.tracks_grid)
        self.content_layout.addWidget(container)

    def setup_featured_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        header = self._create_section_header('03 · FEATURED', '精选项目', '全量目录 →', ('projects', {}))
        layout.addLayout(header)

        self.featured_grid = QGridLayout()
        self.featured_grid.setSpacing(16)
        layout.addLayout(self.featured_grid)
        self.content_layout.addWidget(container)

    def setup_ecosystem_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        header = self._create_section_header('04 · ECOSYSTEM', '生态剖面')
        layout.addLayout(header)

        h_layout = QHBoxLayout()
        h_layout.setSpacing(24)

        # a. Language Distribution
        lang_panel = QWidget()
        lang_layout = QVBoxLayout(lang_panel)
        lang_label = QLabel("Language Distribution (Top 10)")
        lang_label.setStyleSheet("color: #9aa7ba; font-weight: bold;")
        self.lang_chart = BarChartWidget()
        lang_layout.addWidget(lang_label)
        lang_layout.addWidget(self.lang_chart)

        # b. Stars Tier strip
        tier_panel = QWidget()
        tier_layout = QVBoxLayout(tier_panel)
        tier_label = QLabel("Stars Tier")
        tier_label.setStyleSheet("color: #9aa7ba; font-weight: bold;")
        self.tier_chart = BarChartWidget()
        tier_layout.addWidget(tier_label)
        tier_layout.addWidget(self.tier_chart)

        # c. Track Volume
        track_panel = QWidget()
        track_layout = QVBoxLayout(track_panel)
        track_label = QLabel("Track Volume")
        track_label.setStyleSheet("color: #9aa7ba; font-weight: bold;")
        self.track_chart = BarChartWidget()
        track_layout.addWidget(track_label)
        track_layout.addWidget(self.track_chart)

        h_layout.addWidget(lang_panel)
        h_layout.addWidget(tier_panel)
        h_layout.addWidget(track_panel)
        
        layout.addLayout(h_layout)
        self.content_layout.addWidget(container)

    def setup_gaps_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(16)

        header = self._create_section_header('05 · HONEST GAPS', '诚实保留的缺口')
        layout.addLayout(header)

        self.gaps_flow = FlowLayout()
        layout.addLayout(self.gaps_flow)
        
        self.content_layout.addWidget(container)

    def refresh(self):
        stats = data_store.stats.get('totals', {})
        
        # KPI Update
        totals = data_store.stats.get('totals', {})
        if 'developers_count' in self.kpi_widgets:
            self.kpi_widgets['developers_count'].set_value(fmt_num(totals.get('developers', 0)))
        if 'unique_repos' in self.kpi_widgets:
            self.kpi_widgets['unique_repos'].set_value(fmt_num(totals.get('unique_repos', 0)))
        if 'stars_sum' in self.kpi_widgets:
            self.kpi_widgets['stars_sum'].set_value(fmt_k(totals.get('stars_sum', 0)))
        if 'with_github_username' in self.kpi_widgets:
            self.kpi_widgets['with_github_username'].set_value(fmt_num(totals.get('with_github_username', 0)))
        if 'with_homepage' in self.kpi_widgets:
            self.kpi_widgets['with_homepage'].set_value(fmt_num(totals.get('with_homepage', 0)))
        if 'deepseek_native' in self.kpi_widgets:
            self.kpi_widgets['deepseek_native'].set_value(fmt_num(totals.get('deepseek_native', 0)))

        # Top 10 Update
        sorted_proj = sort_projects(data_store.projects, 'stars')
        top10 = sorted_proj[:10]
        self.top10_table.setRowCount(len(top10))
        self.top10_data = top10 # store for click handler
        for r, p in enumerate(top10):
            # Rank
            rank_item = QTableWidgetItem(f"{r+1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            if r == 0: rank_item.setForeground(QColor("#e3b341"))
            elif r == 1: rank_item.setForeground(QColor("#c0c0c0"))
            elif r == 2: rank_item.setForeground(QColor("#cd7f32"))
            self.top10_table.setItem(r, 0, rank_item)
            
            # Name
            self.top10_table.setItem(r, 1, QTableWidgetItem(p.get('name', '')))
            
            # Stars
            stars = p.get('stars') or p.get('metrics', {}).get('stars', 0)
            stars_item = QTableWidgetItem(fmt_num(stars))
            stars_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top10_table.setItem(r, 2, stars_item)
            
            # Language
            lang = p.get('language', '')
            self.top10_table.setItem(r, 3, QTableWidgetItem(lang))
            
            cat_id = p.get('category', '')
            cat_info = cat_of(cat_id)
            self.top10_table.setItem(r, 4, QTableWidgetItem(cat_info.get('zh', cat_id)))
            
            # Applicant
            applicant_str = p.get('applicant_x', '') or (p.get('applicant', {}).get('x', '') if isinstance(p.get('applicant'), dict) else '')
            self.top10_table.setItem(r, 5, QTableWidgetItem(applicant_str))
            
            # Update
            pushed_at = p.get('pushed_at', '') or p.get('metrics', {}).get('pushed_at', '')
            self.top10_table.setItem(r, 6, QTableWidgetItem(fmt_date(pushed_at)))

        # Tracks Update
        for i in reversed(range(self.tracks_grid.count())): 
            w = self.tracks_grid.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()

        cat_stats = data_store.stats.get('category_stats', {})
        def _get_c_info(val):
            if isinstance(val, dict):
                return val.get('count', 0), val.get('stars', 0)
            cnt = val if isinstance(val, (int, float)) else 0
            return cnt, 0

        counts = [_get_c_info(c)[0] for c in cat_stats.values()]
        max_count = max(counts) if counts and max(counts) > 0 else 1
        
        row, col = 0, 0
        for cat_id, cat_info in CATS.items():
            if cat_id == 'all': continue
            c_val = cat_stats.get(cat_id, {})
            c_cnt, c_stars = _get_c_info(c_val)
            
            card = QWidget()
            card.setCursor(Qt.PointingHandCursor)
            card.setStyleSheet("""
                QWidget {
                    background-color: #121824;
                    border: 1px solid #1e2638;
                    border-radius: 8px;
                }
                QWidget:hover {
                    border-color: #e3b341;
                }
            """)
            card_layout = QVBoxLayout(card)
            
            title = QLabel(cat_info['zh'])
            title.setStyleSheet("color: #ece5d6; font-size: 16px; font-weight: bold; border: none; background: transparent;")
            subtitle = QLabel(cat_id)
            subtitle.setStyleSheet("color: #67758c; font-size: 11px; font-family: 'Menlo', 'Courier New'; border: none; background: transparent;")
            
            stats_label = QLabel(f"{c_cnt} projects · {fmt_k(c_stars)} stars")
            stats_label.setStyleSheet("color: #9aa7ba; font-size: 12px; border: none; background: transparent;")
            
            prog = QProgressBar()
            prog.setFixedHeight(4)
            prog.setTextVisible(False)
            prog.setMaximum(max_count)
            prog.setValue(c_cnt)
            prog.setStyleSheet("""
                QProgressBar { border: none; background: #0a0e17; border-radius: 2px; }
                QProgressBar::chunk { background-color: #e3b341; border-radius: 2px; }
            """)
            
            card_layout.addWidget(title)
            card_layout.addWidget(subtitle)
            card_layout.addStretch()
            card_layout.addWidget(stats_label)
            card_layout.addWidget(prog)
            
            card.mouseReleaseEvent = lambda e, cid=cat_id: self.navigate_to.emit('leaderboard', {'cat': cid})
            
            self.tracks_grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        # Featured Update
        for i in reversed(range(self.featured_grid.count())): 
            w = self.featured_grid.itemAt(i).widget()
            if w:
                w.setParent(None)
                w.deleteLater()
                
        featured = data_store.featured[:8] if data_store.featured else sorted_proj[:8]
        r_f, c_f = 0, 0
        for p in featured:
            card = ProjectCard(p)
            card.mouseReleaseEvent = lambda e, name=p.get('name'): self.navigate_to.emit('project_detail', {'name': name})
            self.featured_grid.addWidget(card, r_f, c_f)
            c_f += 1
            if c_f > 1:
                c_f = 0
                r_f += 1

        # Ecosystem Update
        lang_stats = data_store.stats.get('language_stats', {})
        sorted_langs = sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        self.lang_chart.set_data(
            [(k, v) for k, v in sorted_langs],
            [LANG_COLORS.get(k, '#9aa7ba') for k, v in sorted_langs]
        )
        
        tier_stats = data_store.stats.get('star_tiers', {})
        tier_data = []
        tier_colors = []
        for t_id, t_meta in TIER_META.items():
            count = tier_stats.get(t_id, 0)
            if count > 0:
                tier_data.append((t_meta['label'], count))
                tier_colors.append(t_meta.get('color', '#9aa7ba'))
        self.tier_chart.set_data(tier_data, tier_colors)
        
        track_data = []
        for cat_id, c_stat in cat_stats.items():
            c_cnt, _ = _get_c_info(c_stat)
            track_data.append((CATS.get(cat_id, {}).get('zh', cat_id), c_cnt))
        track_data.sort(key=lambda x: x[1], reverse=True)
        self.track_chart.set_data(track_data[:10], ['#4f6385']*10)

        # Gaps Update
        for i in reversed(range(self.gaps_flow.count())): 
            item = self.gaps_flow.itemAt(i)
            if item.widget():
                item.widget().setParent(None)
                item.widget().deleteLater()
                
        gap_stats = data_store.stats.get('residual_gaps', {})
        for g_id, g_label in GAP_META.items():
            count = gap_stats.get(g_id, 0)
            text = f"{g_label} {count}"
            lbl = BadgeLabel(text, "#67758c")
            self.gaps_flow.addWidget(lbl)

    def on_top10_clicked(self, row, col):
        if hasattr(self, 'top10_data') and row < len(self.top10_data):
            p = self.top10_data[row]
            self.navigate_to.emit('project_detail', {'name': p.get('name')})
