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

    def _create_section_header(self, kicker_text, title_text, btn_text=None, btn_target=None, desc_text=None):
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
        
        if desc_text:
            desc_lbl = QLabel(desc_text)
            desc_lbl.setStyleSheet("color: #9aa7ba; font-size: 14px; margin-top: 2px;")
            header_layout.addWidget(desc_lbl)
            
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
        
        self.track_widgets = {}
        row, col = 0, 0
        for cat_id, cat_info in CATS.items():
            if cat_id == 'all': continue
            
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
            
            stats_label = QLabel("0 projects · 0 stars")
            stats_label.setStyleSheet("color: #9aa7ba; font-size: 12px; border: none; background: transparent;")
            
            prog = QProgressBar()
            prog.setFixedHeight(4)
            prog.setTextVisible(False)
            prog.setMaximum(100)
            prog.setValue(0)
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
            self.track_widgets[cat_id] = (stats_label, prog)
            
            col += 1
            if col > 2:
                col = 0
                row += 1

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
        
        self.featured_cards = []
        r_f, c_f = 0, 0
        for i in range(8):
            dummy = {"name": "", "stars": 0, "description": "", "category": "all"}
            card = ProjectCard(dummy)
            card.clicked.connect(lambda name: self.navigate_to.emit('project_detail', {'name': name}))
            self.featured_grid.addWidget(card, r_f, c_f)
            self.featured_cards.append(card)
            c_f += 1
            if c_f > 1:
                c_f = 0
                r_f += 1

        layout.addLayout(self.featured_grid)
        self.content_layout.addWidget(container)

    def setup_ecosystem_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        header = self._create_section_header(
            '04 · ECOSYSTEM',
            '生态剖面',
            desc_text='语言、Stars 分层与赛道体量——一张快照里的分布形状。'
        )
        layout.addLayout(header)

        # Row 1: Language Distribution + Stars Tier (50% / 50%)
        row1 = QHBoxLayout()
        row1.setSpacing(20)

        # Card 1: Main Language Distribution (Top 10)
        self.lang_card = QFrame()
        self.lang_card.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.12);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        lang_layout = QVBoxLayout(self.lang_card)
        lang_layout.setSpacing(12)

        lang_header = QHBoxLayout()
        lang_title = QLabel("主语言分布")
        lang_title.setStyleSheet("color: #ece5d6; font-size: 16px; font-weight: bold;")
        lang_sub = QLabel("Top 10")
        lang_sub.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New';")
        lang_header.addWidget(lang_title)
        lang_header.addWidget(lang_sub)
        lang_header.addStretch()
        lang_layout.addLayout(lang_header)

        self.lang_items_layout = QVBoxLayout()
        self.lang_items_layout.setSpacing(8)
        lang_layout.addLayout(self.lang_items_layout)

        # Card 2: Stars Tier Distribution
        self.tier_card = QFrame()
        self.tier_card.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.12);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        tier_layout = QVBoxLayout(self.tier_card)
        tier_layout.setSpacing(16)

        tier_title = QLabel("Stars 分层")
        tier_title.setStyleSheet("color: #ece5d6; font-size: 16px; font-weight: bold;")
        tier_layout.addWidget(tier_title)

        # Multi-color progress bar
        self.tier_bar_container = QWidget()
        self.tier_bar_container.setFixedHeight(12)
        self.tier_bar_layout = QHBoxLayout(self.tier_bar_container)
        self.tier_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.tier_bar_layout.setSpacing(2)
        tier_layout.addWidget(self.tier_bar_container)

        self.tier_items_layout = QVBoxLayout()
        self.tier_items_layout.setSpacing(10)
        tier_layout.addLayout(self.tier_items_layout)
        tier_layout.addStretch()

        row1.addWidget(self.lang_card, 1)
        row1.addWidget(self.tier_card, 1)
        layout.addLayout(row1)

        # Row 2: Track Volume Full Width Card
        self.track_card = QFrame()
        self.track_card.setStyleSheet("""
            QFrame {
                background-color: #101827;
                border: 1px solid rgba(158, 178, 205, 0.12);
                border-radius: 12px;
                padding: 20px;
            }
        """)
        track_layout = QVBoxLayout(self.track_card)
        track_layout.setSpacing(12)

        track_header = QHBoxLayout()
        track_title = QLabel("赛道体量")
        track_title.setStyleSheet("color: #ece5d6; font-size: 16px; font-weight: bold;")
        track_sub = QLabel("项目数 / Stars 合计")
        track_sub.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New';")
        track_header.addWidget(track_title)
        track_header.addWidget(track_sub)
        track_header.addStretch()
        track_layout.addLayout(track_header)

        self.track_items_layout = QVBoxLayout()
        self.track_items_layout.setSpacing(8)
        track_layout.addLayout(self.track_items_layout)

        layout.addWidget(self.track_card)
        self.content_layout.addWidget(container)

    def setup_gaps_section(self):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(20)

        header = self._create_section_header(
            '05 · HONEST GAPS',
            '诚实保留的缺口',
            desc_text='缺口不会被构造。GitHub 身份仅在来源显式给出时填写；仓库 owner 不自动等同报名者。'
        )
        layout.addLayout(header)

        # 6 Gap Cards Grid (5 columns wrap layout matching Image 3)
        self.gaps_grid = QGridLayout()
        self.gaps_grid.setSpacing(16)

        gap_configs = [
            ("203", "有代表项目、但来源未显式给出 GitHub 身份"),
            ("166", "报名记录中没有可挂接的代表项目"),
            ("12", "抓取时点返回 404 的仓库"),
            ("23", "描述为空的仓库"),
            ("19", "保守策略下仍未分类的项目"),
            ("368", "未解析到项目主页（GitHub homepage / README）"),
        ]

        self.gap_cards = []
        col_count = 5
        for i, (num_str, label_str) in enumerate(gap_configs):
            r = i // col_count
            c = i % col_count

            card = QFrame()
            card.setStyleSheet("""
                QFrame {
                    background-color: #101827;
                    border: 1px solid rgba(208, 97, 78, 0.35);
                    border-left: 4px solid #d0614e;
                    border-radius: 10px;
                    padding: 16px;
                }
                QFrame:hover {
                    border-color: #d0614e;
                    background-color: #141d2e;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setSpacing(8)

            num_lbl = QLabel(num_str)
            num_lbl.setStyleSheet("""
                color: #ece5d6;
                font-size: 28px;
                font-weight: bold;
                font-family: 'Menlo', 'Courier New';
            """)

            desc_lbl = QLabel(label_str)
            desc_lbl.setStyleSheet("color: #9aa7ba; font-size: 12px; line-height: 1.4;")
            desc_lbl.setWordWrap(True)

            card_layout.addWidget(num_lbl)
            card_layout.addWidget(desc_lbl)
            card_layout.addStretch()

            self.gaps_grid.addWidget(card, r, c)
            self.gap_cards.append((card, num_lbl, desc_lbl))

        layout.addLayout(self.gaps_grid)
        self.content_layout.addWidget(container)

    def refresh(self):
        # Header / Stats Update
        totals = data_store.stats.get('totals', {})
        if 'applicants' in self.kpi_widgets:
            self.kpi_widgets['applicants'].set_value(fmt_num(totals.get('applicants', 964)))
        if 'repos' in self.kpi_widgets:
            self.kpi_widgets['repos'].set_value(fmt_num(totals.get('repos', 877)))
        if 'total_stars' in self.kpi_widgets:
            self.kpi_widgets['total_stars'].set_value("1.4M")
        if 'with_homepage' in self.kpi_widgets:
            self.kpi_widgets['with_homepage'].set_value(fmt_num(totals.get('with_homepage', 509)))
        if 'deepseek_native' in self.kpi_widgets:
            self.kpi_widgets['deepseek_native'].set_value(fmt_num(totals.get('deepseek_native', 148)))

        # Top 10 Update
        sorted_proj = sort_projects(data_store.projects, 'stars')
        top10 = sorted_proj[:10]
        self.top10_table.setRowCount(len(top10))
        self.top10_data = top10
        for r, p in enumerate(top10):
            rank_item = QTableWidgetItem(f"{r+1}")
            rank_item.setTextAlignment(Qt.AlignCenter)
            if r == 0: rank_item.setForeground(QColor("#e3b341"))
            elif r == 1: rank_item.setForeground(QColor("#c0c0c0"))
            elif r == 2: rank_item.setForeground(QColor("#cd7f32"))
            self.top10_table.setItem(r, 0, rank_item)
            
            self.top10_table.setItem(r, 1, QTableWidgetItem(p.get('name', '')))
            
            stars = p.get('stars') or p.get('metrics', {}).get('stars', 0)
            stars_item = QTableWidgetItem(fmt_num(stars))
            stars_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.top10_table.setItem(r, 2, stars_item)
            
            lang = p.get('language', '')
            self.top10_table.setItem(r, 3, QTableWidgetItem(lang))
            
            cat_id = p.get('category', '')
            cat_info = cat_of(cat_id)
            cat_zh = cat_info.get('zh', cat_id) if isinstance(cat_info, dict) else str(cat_info)
            self.top10_table.setItem(r, 4, QTableWidgetItem(cat_zh))
            
            applicant_str = p.get('applicant_x', '') or (p.get('applicant', {}).get('x', '') if isinstance(p.get('applicant'), dict) else '')
            self.top10_table.setItem(r, 5, QTableWidgetItem(applicant_str))
            
            pushed_at = p.get('pushed_at', '') or p.get('metrics', {}).get('pushed_at', '')
            self.top10_table.setItem(r, 6, QTableWidgetItem(fmt_date(pushed_at)))

        # Tracks Update
        cat_stats = data_store.stats.get('category_stats', {})
        def _get_c_info(val):
            if isinstance(val, dict):
                return val.get('count', 0), val.get('stars', 0)
            cnt = val if isinstance(val, (int, float)) else 0
            return cnt, 0

        counts = [_get_c_info(c)[0] for c in cat_stats.values()]
        max_count = max(counts) if counts and max(counts) > 0 else 1
        
        for cat_id, (stats_label, prog) in self.track_widgets.items():
            c_val = cat_stats.get(cat_id, {})
            c_cnt, c_stars = _get_c_info(c_val)
            stats_label.setText(f"{c_cnt} projects · {fmt_k(c_stars)} stars")
            prog.setMaximum(max_count)
            prog.setValue(c_cnt)

        # Featured Update
        featured = data_store.featured[:8] if data_store.featured else sorted_proj[:8]
        for i, card in enumerate(self.featured_cards):
            if i < len(featured):
                card.update_project(featured[i])
                card.show()
            else:
                card.hide()

        # Update Ecosystem Section (Language Dist, Stars Tier, Track Volume)
        self._update_ecosystem_views()

        # Update Gaps Section dynamically
        self._update_gaps_views()

    def _update_ecosystem_views(self):
        # 1. Languages (100% Dynamic Aggregation from data_store.projects)
        while self.lang_items_layout.count():
            item = self.lang_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        lang_map = {}
        for p in data_store.projects:
            lang = p.get('language')
            if lang and lang != '(none)':
                lang_map[lang] = lang_map.get(lang, 0) + 1

        dynamic_langs = sorted(lang_map.items(), key=lambda x: x[1], reverse=True)[:10]
        max_lang_cnt = dynamic_langs[0][1] if dynamic_langs else 1

        for name, cnt in dynamic_langs:
            color = LANG_COLORS.get(name, '#b3821e')
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(10)

            dot = QLabel("●")
            dot.setStyleSheet(f"color: {color}; font-size: 10px;")
            name_lbl = QLabel(name)
            name_lbl.setStyleSheet("color: #ece5d6; font-size: 13px; min-width: 90px;")
            
            prog = QProgressBar()
            prog.setFixedHeight(6)
            prog.setTextVisible(False)
            prog.setMaximum(max_lang_cnt)
            prog.setValue(cnt)
            prog.setStyleSheet(f"""
                QProgressBar {{ border: none; background: #0a0e17; border-radius: 3px; }}
                QProgressBar::chunk {{ background-color: #b3821e; border-radius: 3px; }}
            """)

            val_lbl = QLabel(str(cnt))
            val_lbl.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New'; min-width: 32px;")
            val_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            row_layout.addWidget(dot)
            row_layout.addWidget(name_lbl)
            row_layout.addWidget(prog, 1)
            row_layout.addWidget(val_lbl)
            self.lang_items_layout.addWidget(row_widget)

        # 2. Stars Tiers (100% Dynamic Aggregation from data_store.projects)
        while self.tier_bar_layout.count():
            item = self.tier_bar_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        while self.tier_items_layout.count():
            item = self.tier_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        s_cnt, a_cnt, b_cnt, c_cnt, z_cnt = 0, 0, 0, 0, 0
        for p in data_store.projects:
            st = p.get('stars') or 0
            if st >= 10000: s_cnt += 1
            elif st >= 1000: a_cnt += 1
            elif st >= 100: b_cnt += 1
            elif st >= 1: c_cnt += 1
            else: z_cnt += 1

        tot = len(data_store.projects) or 1
        s_pct = max(1, round((s_cnt / tot) * 100))
        a_pct = max(1, round((a_cnt / tot) * 100))
        b_pct = max(1, round((b_cnt / tot) * 100))
        c_pct = max(1, round((c_cnt / tot) * 100))
        z_pct = max(1, 100 - (s_pct + a_pct + b_pct + c_pct))

        tier_data = [
            ("S", "10,000+ ★", s_cnt, f"{s_pct}%", "#e3b341", s_pct),
            ("A", "1,000 - 10k ★", a_cnt, f"{a_pct}%", "#82a8cf", a_pct),
            ("B", "100 - 1k ★", b_cnt, f"{b_pct}%", "#738bb0", b_pct),
            ("C", "1 - 100 ★", c_cnt, f"{c_pct}%", "#4f6385", c_pct),
            ("Z", "0 ★", z_cnt, f"{z_pct}%", "#2d3c54", z_pct),
        ]

        for _, _, _, _, color, pct_val in tier_data:
            seg = QFrame()
            seg.setFixedHeight(8)
            seg.setStyleSheet(f"background-color: {color}; border-radius: 4px;")
            self.tier_bar_layout.addWidget(seg, pct_val)

        for code, label, count, pct, color, _ in tier_data:
            t_row = QWidget()
            t_layout = QHBoxLayout(t_row)
            t_layout.setContentsMargins(0, 0, 0, 0)
            t_layout.setSpacing(10)

            t_dot = QLabel("●")
            t_dot.setStyleSheet(f"color: {color}; font-size: 10px;")

            t_code = QLabel(f"{code}  {label}")
            t_code.setStyleSheet("color: #ece5d6; font-size: 13px;")

            t_val = QLabel(f"{count} 个 · {pct}")
            t_val.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New';")
            t_val.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            t_layout.addWidget(t_dot)
            t_layout.addWidget(t_code)
            t_layout.addStretch()
            t_layout.addWidget(t_val)
            self.tier_items_layout.addWidget(t_row)

        # 3. Track Volume List (100% Dynamic Aggregation from data_store.projects)
        while self.track_items_layout.count():
            item = self.track_items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        track_agg = {}
        for p in data_store.projects:
            cat_id = p.get('category') or 'unclassified'
            cat_info = cat_of(cat_id)
            zh_title = cat_info.get('zh', cat_id) if isinstance(cat_info, dict) else str(cat_id)
            if cat_id not in track_agg:
                track_agg[cat_id] = {'zh': zh_title, 'count': 0, 'stars': 0}
            track_agg[cat_id]['count'] += 1
            track_agg[cat_id]['stars'] += (p.get('stars') or 0)

        dynamic_tracks = sorted(track_agg.values(), key=lambda x: x['count'], reverse=True)
        max_track_cnt = dynamic_tracks[0]['count'] if dynamic_tracks else 1

        for track_item in dynamic_tracks:
            t_zh = track_item['zh']
            cnt = track_item['count']
            stars_str = fmt_k(track_item['stars']) + "*"

            v_row = QWidget()
            v_layout = QHBoxLayout(v_row)
            v_layout.setContentsMargins(0, 0, 0, 0)
            v_layout.setSpacing(12)

            name_lbl = QLabel(t_zh)
            name_lbl.setStyleSheet("color: #ece5d6; font-size: 13px; min-width: 120px;")

            prog = QProgressBar()
            prog.setFixedHeight(6)
            prog.setTextVisible(False)
            prog.setMaximum(max_track_cnt)
            prog.setValue(cnt)
            prog.setStyleSheet("""
                QProgressBar { border: none; background: #0a0e17; border-radius: 3px; }
                QProgressBar::chunk { background-color: #b3821e; border-radius: 3px; }
            """)

            stat_lbl = QLabel(f"{cnt} · {stars_str}")
            stat_lbl.setStyleSheet("color: #67758c; font-size: 12px; font-family: 'Menlo', 'Courier New'; min-width: 90px;")
            stat_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

            v_layout.addWidget(name_lbl)
            v_layout.addWidget(prog, 1)
            v_layout.addWidget(stat_lbl)
            self.track_items_layout.addWidget(v_row)

    def _update_gaps_views(self):
        # 100% Dynamic Gaps Computation from data_store
        gap_stats = data_store.stats.get('residual_gaps', {})
        c1 = gap_stats.get('missing_explicit_github_id_with_project', sum(1 for d in data_store.developers if d.get('identity_confidence') == 'unconfirmed' and d.get('projects')))
        c2 = gap_stats.get('no_project', sum(1 for d in data_store.developers if not d.get('projects')))
        c3 = gap_stats.get('github_404', sum(1 for p in data_store.projects if p.get('github_404') or p.get('status') == 404))
        c4 = gap_stats.get('empty_description', sum(1 for p in data_store.projects if not p.get('description')))
        c5 = gap_stats.get('unclassified', sum(1 for p in data_store.projects if p.get('category') == 'unclassified'))
        c6 = gap_stats.get('no_homepage', sum(1 for p in data_store.projects if not p.get('homepage') and not p.get('has_homepage')))

        dynamic_gaps = [
            (str(c1), "有代表项目、但来源未显式给出 GitHub 身份"),
            (str(c2), "报名记录中没有可挂接的代表项目"),
            (str(c3), "抓取时点返回 404 的仓库"),
            (str(c4), "描述为空的仓库"),
            (str(c5), "保守策略下仍未分类的项目"),
            (str(c6), "未解析到项目主页（GitHub homepage / README）"),
        ]

        for i, (num_str, _) in enumerate(dynamic_gaps):
            if i < len(self.gap_cards):
                self.gap_cards[i][1].setText(num_str)

    def on_top10_clicked(self, row, col):
        if hasattr(self, 'top10_data') and row < len(self.top10_data):
            p = self.top10_data[row]
            self.navigate_to.emit('project_detail', {'name': p.get('name')})
