from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from core.data_loader import data_store, fmt_num, cat_of

CATS = {
    "agent-harness": {"zh": "智能体框架", "desc": "Agent 运行时、脚手架与框架"},
    "coding-agent": {"zh": "编程智能体", "desc": "会写代码、改代码的 Agent"},
    "agent-orchestration": {"zh": "智能体编排", "desc": "多智能体协作与任务编排"},
    "memory-context": {"zh": "记忆与上下文", "desc": "记忆、上下文与知识管理"},
    "agent-workspace": {"zh": "智能体工作台", "desc": "Agent 的工作区与执行环境"},
    "agent-client": {"zh": "智能体客户端", "desc": "面向用户的 Agent 客户端与入口"},
    "skills": {"zh": "技能包", "desc": "Skills / 插件 / 提示词资产"},
    "tooling-automation": {"zh": "工具与自动化", "desc": "开发流程工具与自动化"},
    "infrastructure": {"zh": "基础设施", "desc": "推理、训练与平台基础设施"},
    "developer-tools": {"zh": "开发者工具", "desc": "编辑器、CLI 与效率工具"},
    "creative-tools": {"zh": "创意工具", "desc": "内容生成与创意生产"},
    "security-governance": {"zh": "安全与治理", "desc": "安全、审计与合规治理"},
    "research-evaluation": {"zh": "研究与评测", "desc": "基准、评测与学术研究"},
    "research-tools": {"zh": "研究工具", "desc": "科研工作流与实验工具"},
    "education": {"zh": "教育", "desc": "教学与学习资源"},
    "domain-application": {"zh": "领域应用", "desc": "垂直领域应用"},
    "other": {"zh": "其他", "desc": "不便归入以上赛道"},
    "unclassified": {"zh": "未分类", "desc": "保守策略下暂不归类"},
}

class CategoryRow(QFrame):
    clicked = pyqtSignal(str)

    def __init__(self, index, cat_id, cat_info, count, stars):
        super().__init__()
        self.cat_id = cat_id
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName("CategoryRow")
        self.setStyleSheet("""
            #CategoryRow {
                background: #101827;
                border: 1px solid rgba(158,178,205,0.10);
                border-radius: 12px;
                margin-bottom: 8px;
            }
            #CategoryRow:hover {
                background: #1a2335;
                border: 1px solid rgba(227,179,65,0.30);
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        
        idx_lbl = QLabel(f"{index:02d}")
        idx_lbl.setStyleSheet("font-family: 'Menlo', 'Courier New'; color: rgba(236,229,214,0.4); font-size: 14px;")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(0, 0, 0, 0)
        name_lbl = QLabel(cat_info['zh'])
        name_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #ece5d6;")
        id_lbl = QLabel(cat_id)
        id_lbl.setStyleSheet("font-family: 'Menlo', 'Courier New'; color: rgba(236,229,214,0.4); font-size: 12px;")
        title_layout.addWidget(name_lbl)
        title_layout.addWidget(id_lbl)
        title_layout.addStretch()
        
        desc_lbl = QLabel(cat_info['desc'])
        desc_lbl.setStyleSheet("color: rgba(236,229,214,0.7); font-size: 13px;")
        
        info_layout.addLayout(title_layout)
        info_layout.addWidget(desc_lbl)
        
        stats_layout = QVBoxLayout()
        stats_layout.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        stats_layout.setSpacing(2)
        
        count_lbl = QLabel(f"<b style='color:#e3b341;font-size:16px;'>{count}</b> <span style='color:rgba(236,229,214,0.5);font-size:12px;'>projects</span>")
        count_lbl.setAlignment(Qt.AlignRight)
        
        stars_lbl = QLabel(f"<b style='color:#ece5d6;font-size:14px;'>{fmt_num(stars) if stars else 0}</b> <span style='color:rgba(236,229,214,0.5);font-size:12px;'>Stars 合计</span>")
        stars_lbl.setAlignment(Qt.AlignRight)
        
        stats_layout.addWidget(count_lbl)
        stats_layout.addWidget(stars_lbl)
        
        layout.addWidget(idx_lbl)
        layout.addSpacing(16)
        layout.addLayout(info_layout, 1)
        layout.addLayout(stats_layout)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.cat_id)
            
class CategoriesView(QWidget):
    navigate_to = pyqtSignal(str, dict)

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("background-color: transparent;")
        
        container = QWidget()
        container.setStyleSheet("background-color: transparent;")
        self.layout = QVBoxLayout(container)
        self.layout.setContentsMargins(40, 40, 40, 40)
        self.layout.setSpacing(0)
        
        header_layout = QVBoxLayout()
        kicker = QLabel("TRACKS")
        kicker.setStyleSheet("color: #e3b341; font-weight: bold; font-size: 12px; letter-spacing: 2px;")
        title = QLabel("赛道索引")
        title.setStyleSheet("font-size: 28px; font-weight: bold; color: #ece5d6; margin-top: 4px; margin-bottom: 8px;")
        desc = QLabel("点击赛道进入对应排行榜。分类为保守关键词规则，宁可留「未分类」也不硬猜。")
        desc.setStyleSheet("color: rgba(236,229,214,0.7); font-size: 14px; margin-bottom: 24px;")
        desc.setWordWrap(True)
        
        header_layout.addWidget(kicker)
        header_layout.addWidget(title)
        header_layout.addWidget(desc)
        
        self.layout.addLayout(header_layout)
        
        self.list_layout = QVBoxLayout()
        self.list_layout.setSpacing(0)
        self.layout.addLayout(self.list_layout)
        self.layout.addStretch()
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def refresh(self):
        while self.list_layout.count():
            child = self.list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        stats = data_store.stats.get('category_stats', {})
        
        cat_list = []
        for cat_id, info in CATS.items():
            c_data = stats.get(cat_id, {})
            if isinstance(c_data, dict):
                count = c_data.get('count', c_data.get('projects', 0))
                stars = c_data.get('stars', 0)
            else:
                count = c_data if isinstance(c_data, (int, float)) else 0
                stars = 0
            cat_list.append((cat_id, info, count, stars))
            
        cat_list.sort(key=lambda x: x[2], reverse=True)
        
        for i, (cat_id, info, count, stars) in enumerate(cat_list, 1):
            row = CategoryRow(i, cat_id, info, count, stars)
            row.clicked.connect(self.on_cat_clicked)
            self.list_layout.addWidget(row)
            
    def on_cat_clicked(self, cat_id):
        self.navigate_to.emit('leaderboard', {'cat': cat_id})
