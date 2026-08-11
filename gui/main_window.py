import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QStackedWidget, QPushButton, QLabel, QFrame,
    QSizePolicy, QApplication, QSpacerItem
)
from PyQt5.QtCore import Qt, QSize, QTimer, QPointF
from PyQt5.QtGui import QFont, QIcon, QPainter, QColor, QPen, QPolygonF

from core.data_loader import data_store

from gui.components.home_view import HomeView
from gui.components.leaderboard_view import LeaderboardView
from gui.components.categories_view import CategoriesView
from gui.components.projects_view import ProjectsView
from gui.components.developers_view import DevelopersView
from gui.components.about_view import AboutView
from gui.components.project_detail_view import ProjectDetailView
from gui.components.developer_detail_view import DeveloperDetailView
from gui.components.widgets import LoadingOverlay


class BrandIcon(QWidget):
    """Diamond brand mark matching the website logo."""

    def __init__(self, size=26, parent=None):
        super().__init__(parent)
        self._size = size
        self.setFixedSize(size, size)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        s = self._size
        cx, cy = s / 2, s / 2
        margin = 2

        # Diamond outline
        diamond = QPolygonF([
            QPointF(cx, margin),
            QPointF(s - margin, cy),
            QPointF(cx, s - margin),
            QPointF(margin, cy),
        ])
        pen = QPen(QColor("#e3b341"), 1.4)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawPolygon(diamond)

        # Center dot
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#e3b341"))
        p.drawEllipse(QPointF(cx, cy), 2.2, 2.2)
        p.end()


class NavButton(QPushButton):
    """Navigation button with active state."""

    def __init__(self, text, key, parent=None):
        super().__init__(text, parent)
        self.key = key
        self.setCheckable(True)
        self.setCursor(Qt.PointingHandCursor)
        self.setProperty("cssClass", "navBtn")
        self.setFixedHeight(34)
        font = self.font()
        font.setPointSize(13)
        self.setFont(font)


class MainWindow(QMainWindow):
    """Main application window for Harness Index."""

    VIEW_KEYS = ["home", "leaderboard", "categories", "projects", "developers", "about"]
    VIEW_LABELS = {
        "home": "总览",
        "leaderboard": "排行榜",
        "categories": "赛道",
        "projects": "项目",
        "developers": "开发者",
        "about": "关于",
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harness Index · DeepSeek Harness 内测报名档案")
        self.setMinimumSize(1100, 720)
        self.resize(1280, 860)

        # Load data
        data_store.load()

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # --- Navigation Bar ---
        self.nav_bar = QFrame()
        self.nav_bar.setObjectName("navBar")
        self.nav_bar.setFixedHeight(56)
        self.nav_bar.setStyleSheet("""
            QFrame#navBar {
                background: rgba(10, 14, 23, 0.95);
                border-bottom: 1px solid rgba(158, 178, 205, 0.10);
            }
        """)

        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(24, 0, 24, 0)
        nav_layout.setSpacing(10)

        # Brand
        brand_icon = BrandIcon(26)
        nav_layout.addWidget(brand_icon)

        brand_text = QWidget()
        brand_text_layout = QVBoxLayout(brand_text)
        brand_text_layout.setContentsMargins(0, 0, 0, 0)
        brand_text_layout.setSpacing(0)

        brand_name = QLabel("Harness Index")
        brand_name.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #f7f2e6;
            font-family: 'Avenir Next', 'Helvetica Neue', Arial;
        """)
        brand_sub = QLabel("DeepSeek 内测报名档案")
        brand_sub.setStyleSheet("""
            font-size: 10px;
            color: #67758c;
            letter-spacing: 1px;
        """)
        brand_text_layout.addWidget(brand_name)
        brand_text_layout.addWidget(brand_sub)
        nav_layout.addWidget(brand_text)

        nav_layout.addSpacerItem(QSpacerItem(40, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Nav buttons
        self.nav_buttons = {}
        for key in self.VIEW_KEYS:
            btn = NavButton(self.VIEW_LABELS[key], key)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: #9aa7ba;
                    border: none;
                    border-radius: 16px;
                    padding: 6px 16px;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    color: #f7f2e6;
                    background: rgba(130, 168, 207, 0.12);
                }
                QPushButton:checked {
                    color: #e3b341;
                    background: transparent;
                }
            """)
            btn.clicked.connect(lambda checked, k=key: self._navigate(k))
            nav_layout.addWidget(btn)
            self.nav_buttons[key] = btn

        nav_layout.addSpacerItem(QSpacerItem(20, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # Refresh Data Button
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.setCursor(Qt.PointingHandCursor)
        self.btn_refresh.setToolTip("重新加载与刷新数据档案")
        self.btn_refresh.setStyleSheet("""
            QPushButton {
                background: rgba(227, 179, 65, 0.12);
                color: #e3b341;
                border: 1px solid rgba(227, 179, 65, 0.3);
                border-radius: 14px;
                padding: 5px 14px;
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: rgba(227, 179, 65, 0.25);
                border-color: #e3b341;
            }
        """)
        self.btn_refresh.clicked.connect(self._on_refresh_clicked)
        nav_layout.addWidget(self.btn_refresh)

        main_layout.addWidget(self.nav_bar)

        # --- View Stack ---
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background: #0a0e17;")
        main_layout.addWidget(self.stack)

        # Loading Overlay
        self.loading_overlay = LoadingOverlay(central)

        # Create views
        self.views = {}
        self._create_views()

        # Default view
        self._navigate("home")

    def _create_views(self):
        """Create and add all view widgets to the stack."""

        # Home
        home = HomeView()
        home.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(home)
        self.views["home"] = home

        # Leaderboard
        leaderboard = LeaderboardView()
        leaderboard.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(leaderboard)
        self.views["leaderboard"] = leaderboard

        # Categories
        categories = CategoriesView()
        categories.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(categories)
        self.views["categories"] = categories

        # Projects
        projects = ProjectsView()
        projects.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(projects)
        self.views["projects"] = projects

        # Developers
        developers = DevelopersView()
        developers.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(developers)
        self.views["developers"] = developers

        # About
        about = AboutView()
        self.stack.addWidget(about)
        self.views["about"] = about

        # Project Detail (Image 3)
        project_detail = ProjectDetailView()
        project_detail.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(project_detail)
        self.views["project_detail"] = project_detail

        # Developer Detail
        developer_detail = DeveloperDetailView()
        developer_detail.navigate_to.connect(self._handle_navigate)
        self.stack.addWidget(developer_detail)
        self.views["developer_detail"] = developer_detail

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            self.loading_overlay.resize(self.centralWidget().size())

    def _navigate(self, key, params=None):
        """Switch to the specified view with loading animation."""
        if key not in self.views:
            return

        self.loading_overlay.show_loading("正在加载数据...")

        def execute_switch():
            try:
                view = self.views[key]

                # Detail parameters
                if key == "project_detail" and params:
                    view.set_project(params)
                elif key == "developer_detail" and params:
                    view.set_developer(params)
                elif params and key == "leaderboard" and "cat" in params:
                    if hasattr(view, 'set_category'):
                        view.set_category(params["cat"])

                self.stack.setCurrentWidget(view)

                # Update nav button states
                for k, btn in self.nav_buttons.items():
                    btn.setChecked(k == key)

                # Refresh view data
                if hasattr(view, 'refresh') and key not in ("project_detail", "developer_detail"):
                    view.refresh()
            except Exception as e:
                print(f"Error switching view to {key}: {e}")
            finally:
                self.loading_overlay.hide_loading()

        QTimer.singleShot(150, execute_switch)

    def _on_refresh_clicked(self):
        """Reload dataset and refresh current view."""
        self.loading_overlay.show_loading("正在重新获取与同步最新档案数据...")

        def execute_reload():
            data_store.load()
            current_view = self.stack.currentWidget()
            if hasattr(current_view, 'refresh'):
                current_view.refresh()
            self.loading_overlay.hide_loading()

        QTimer.singleShot(400, execute_reload)

    def _handle_navigate(self, target, params):
        """Handle navigation signals from views."""
        view_map = {
            "leaderboard": "leaderboard",
            "categories": "categories",
            "projects": "projects",
            "developers": "developers",
            "about": "about",
            "home": "home",
            "project_detail": "project_detail",
            "developer_detail": "developer_detail",
        }
        key = view_map.get(target, "home")
        if not isinstance(params, (dict, str)):
            params = {}
        self._navigate(key, params)
