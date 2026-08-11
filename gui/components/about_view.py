from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from core.data_loader import data_store

class AboutView(QWidget):
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
        layout = QVBoxLayout(container)
        layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
        
        content = QWidget()
        content.setMaximumWidth(700)
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(0, 60, 0, 60)
        
        self.label = QLabel()
        self.label.setWordWrap(True)
        self.label.setOpenExternalLinks(True)
        self.label.setStyleSheet("""
            QLabel {
                color: #ece5d6;
                font-size: 15px;
                line-height: 1.6;
            }
            h2 {
                color: #f7f2e6;
                font-size: 24px;
                margin-top: 24px;
                margin-bottom: 12px;
            }
            ul {
                margin-top: 8px;
                margin-bottom: 16px;
            }
            li {
                margin-bottom: 8px;
            }
        """)
        
        content_layout.addWidget(self.label)
        layout.addWidget(content)
        
        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        
    def refresh(self):
        snapshot_id = data_store.stats.get("snapshot_id", "Unknown")
        timestamp = data_store.stats.get("timestamp", "Unknown")
        
        html = f"""
        <h2>关于本档案</h2>
        <p>这是一份社区维护的非官方档案，记录 DeepSeek Harness 内测招募活动中报名者的公开信息。<br>
        与 DeepSeek 官方无关，不代表录取结果，也不构成任何背书。</p>
        
        <p>招募帖要求报名者在 X 上回复：X 身份、GitHub ID、代表性开源项目。<br>
        我们把整场活动整理为可检索、可审计、可复现的结构化数据。</p>
        
        <h2>档案原则</h2>
        <ul>
            <li>以开发者为中心；项目是挂接在报名记录下的证据</li>
            <li>github_username 只在来源显式给出时填写</li>
            <li>Stars / Fork / 最后 push 等指标带快照时间戳，不实时刷新</li>
            <li>无法安全确认的信息保留为缺口，宁可空白也不编造</li>
        </ul>
        
        <h2>数据版本</h2>
        <ul>
            <li>Snapshot ID: {snapshot_id}</li>
            <li>数据包生成时间: {timestamp}</li>
        </ul>
        """
        self.label.setText(html)
