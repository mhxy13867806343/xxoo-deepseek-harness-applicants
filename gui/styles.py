COLORS = {
    'bg': '#0a0e17', 'bg_raise': '#0d1320', 'surface': '#101827', 'surface_2': '#141e2f', 'surface_3': '#182437',
    'line': 'rgba(158,178,205,0.10)', 'line_strong': 'rgba(158,178,205,0.22)',
    'ink': '#ece5d6', 'ink_strong': '#f7f2e6', 'muted': '#9aa7ba', 'faint': '#67758c',
    'gold': '#e3b341', 'gold_soft': 'rgba(227,179,65,0.12)',
    'blue': '#82a8cf', 'blue_soft': 'rgba(130,168,207,0.12)',
    'red': '#d0614e', 'green': '#82bd92',
    'rank_1': '#e3b341', 'rank_2': '#b9c6d6', 'rank_3': '#c08a5a',
}

APP_QSS = """
/* Main window & base */
QMainWindow, QDialog, QWidget {
    background-color: #0a0e17;
    color: #ece5d6;
    font-family: "Helvetica Neue", "Arial";
}

/* Navigation bar */
QFrame#navBar {
    background-color: rgba(10,14,23,0.92);
    border-bottom: 1px solid rgba(158,178,205,0.10);
    max-height: 56px;
    min-height: 56px;
}
QFrame#navBar QLabel {
    font-weight: 600;
    color: #f7f2e6;
}
QPushButton.navBtn {
    background-color: transparent;
    color: #9aa7ba;
    border-radius: 16px;
    padding: 6px 14px;
    border: none;
}
QPushButton.navBtn:hover {
    color: #f7f2e6;
    background-color: rgba(130,168,207,0.12);
}
QPushButton.navBtn:checked, QPushButton.navBtn:active {
    color: #e3b341;
}

/* Cards */
QFrame.card {
    background-color: #101827;
    border: 1px solid rgba(158,178,205,0.10);
    border-radius: 12px;
}
QFrame.card:hover {
    border-color: rgba(158,178,205,0.22);
}

/* Tables */
QTableWidget {
    background-color: #101827;
    gridline-color: rgba(158,178,205,0.10);
    border: none;
}
QHeaderView::section {
    background-color: #141e2f;
    color: #67758c;
    font-size: 11px;
    font-weight: 500;
    border: none;
    padding: 4px;
}
QTableWidget::item {
    border-bottom: 1px solid rgba(158,178,205,0.10);
    padding: 10px;
}
QTableWidget::item:hover {
    background-color: rgba(130,168,207,0.12);
}
QTableWidget::item:selected {
    background-color: rgba(227,179,65,0.12);
    color: #ece5d6;
}

/* Buttons */
QPushButton.btnPrimary {
    background-color: #e3b341;
    color: #171207;
    border-radius: 20px;
    font-weight: 550;
    padding: 6px 16px;
    border: none;
}
QPushButton.btnGhost {
    background-color: transparent;
    border: 1px solid rgba(158,178,205,0.22);
    color: #ece5d6;
    border-radius: 20px;
    padding: 6px 16px;
}

/* Search box */
QLineEdit.searchBox {
    background-color: #101827;
    border: 1px solid rgba(158,178,205,0.10);
    border-radius: 20px;
    padding: 8px 16px;
    color: #ece5d6;
}
QLineEdit.searchBox:focus {
    border-color: #e3b341;
}

/* Combo box */
QComboBox {
    background-color: #101827;
    border: 1px solid rgba(158,178,205,0.10);
    border-radius: 20px;
    padding: 7px 14px;
    color: #ece5d6;
}
QComboBox::drop-down {
    border: none;
}

/* Checkbox/Switch */
QCheckBox::indicator {
    width: 14px;
    height: 14px;
    border: 1px solid rgba(158,178,205,0.22);
    border-radius: 3px;
}
QCheckBox::indicator:checked {
    background-color: #e3b341;
    border-color: #e3b341;
}

/* Scroll area */
QScrollArea {
    background-color: transparent;
    border: none;
}
QScrollBar:vertical {
    width: 6px;
    background-color: rgba(0,0,0,0.2);
    border-radius: 3px;
    margin: 0px;
}
QScrollBar::handle:vertical {
    background-color: rgba(158,178,205,0.3);
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover {
    background-color: #e3b341;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Labels */
QLabel.sectionKicker {
    color: #e3b341;
    font-size: 11px;
    letter-spacing: 2px;
    font-family: "Menlo", "Courier New";
}
QLabel.sectionTitle {
    color: #f7f2e6;
    font-size: 22px;
    font-weight: 620;
}
QLabel.sectionDesc {
    color: #9aa7ba;
    font-size: 14px;
}
QLabel.kpiNum {
    color: #f7f2e6;
    font-size: 28px;
    font-weight: 600;
    font-family: "Menlo", "Courier New";
}
QLabel.kpiLabel {
    color: #67758c;
    font-size: 11px;
}
QLabel.heroTitle {
    color: #f7f2e6;
    font-size: 42px;
    font-weight: 650;
}
QLabel.muted {
    color: #9aa7ba;
}
QLabel.faint {
    color: #67758c;
}

/* Badges */
QLabel.badge {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    background-color: rgba(158,178,205,0.12);
    color: #9aa7ba;
}
QLabel.badgeGold {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    background-color: rgba(227,179,65,0.12);
    color: #e3b341;
}
QLabel.badgeBlue {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    background-color: rgba(130,168,207,0.12);
    color: #82a8cf;
}
QLabel.badgeGreen {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    background-color: rgba(130,189,146,0.12);
    color: #82bd92;
}
QLabel.badgeRed {
    padding: 3px 10px;
    border-radius: 10px;
    font-size: 11px;
    background-color: rgba(208,97,78,0.12);
    color: #d0614e;
}

/* Chips */
QPushButton.chip {
    border: 1px solid rgba(158,178,205,0.10);
    background-color: transparent;
    color: #67758c;
    border-radius: 16px;
    padding: 4px 12px;
    font-size: 12px;
}
QPushButton.chip:hover {
    border-color: rgba(158,178,205,0.22);
    color: #ece5d6;
}
QPushButton.chip:checked {
    background-color: rgba(227,179,65,0.12);
    border-color: #e3b341;
    color: #e3b341;
}

/* Pager buttons */
QPushButton.pagerBtn {
    background-color: transparent;
    border: 1px solid rgba(158,178,205,0.10);
    color: #9aa7ba;
    border-radius: 6px;
    min-width: 32px;
    min-height: 32px;
}
QPushButton.pagerBtn:checked {
    background-color: rgba(227,179,65,0.12);
    border-color: #e3b341;
    color: #e3b341;
}
QPushButton.pagerBtn:hover {
    border-color: rgba(158,178,205,0.22);
}
QPushButton.pagerBtn:disabled {
    color: rgba(103,117,140,0.4);
}

/* Category row */
QFrame.catRow {
    background-color: #101827;
    border: 1px solid rgba(158,178,205,0.10);
    border-radius: 12px;
}
QFrame.catRow:hover {
    border-color: rgba(227,179,65,0.3);
    background-color: #141e2f;
}

/* Progress bars */
QProgressBar {
    background-color: rgba(158,178,205,0.10);
    border-radius: 3px;
    max-height: 6px;
    border: none;
    text-align: center;
    color: transparent;
}
QProgressBar::chunk {
    background-color: #82a8cf;
    border-radius: 3px;
}
"""
