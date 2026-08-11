# Harness Index · DeepSeek Harness 内测报名档案 (Desktop App)

![PyQt5](https://img.shields.io/badge/PyQt-5.15-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11%2B-green.svg)
![License](https://img.shields.io/badge/License-MIT-gold.svg)

DeepSeek Harness 社区内测报名档案桌面客户端 (Python 3.11 + PyQt5)。收录 769 位报名者、964 位开发者、877 个开源仓库与 18 个智能体赛道切片。

---

## 仓库地址

- **Gitee**: [https://gitee.com/fangjiayu/xxoo-deepseek-harness-applicants.git](https://gitee.com/fangjiayu/xxoo-deepseek-harness-applicants.git)
- **GitHub**: [https://github.com/mhxy13867806343/xxoo-deepseek-harness-applicants.git](https://github.com/mhxy13867806343/xxoo-deepseek-harness-applicants.git)

---

## 核心功能特性

1. **总览仪表盘 (Home Dashboard)**
   - 全局核心 KPI（开发者数、开源项目数、总 Stars 数、GitHub 身份匹配率、有主页率）。
   - Stars 总榜前十快速通道，点击直接查看项目详情。
   - 18 大赛道卡片索引与精选项目展示。
   - 语言分布 (Top 10)、Stars 梯队分布与赛道容量生态剖面柱状图。

2. **项目排行榜 (Leaderboard)**
   - 支持按 Stars 高→低、最近更新时间、上线时间多维排序。
   - 支持 18 个赛道 Chip 一键切换过滤，支持“仅 DeepSeek 相关”智能筛选。
   - 包含项目名、Stars、主语言、赛道、报名者、上线时间与更新时间。
   - **点击任意项目行，直接跳转至项目详情页**。

3. **赛道索引 (Categories)**
   - 汇聚 18 大智能体赛道（智能体框架、编程智能体、记忆与上下文、工具与自动化等）。
   - 显示各赛道收录项目数与累积 Stars 数，支持点击直达赛道项目榜单。

4. **项目目录 (Projects Grid)**
   - 877 个开源智能体框架与工具无极网格展布。
   - 支持项目名 / 描述 / 报名者实时模糊搜索。
   - 支持语言下拉筛选（包括未指定语言）、按 Stars/更新/上线/名称排序，以及 DeepSeek/高相关/有主页复选过滤。

5. **开发者目录 (Developers Grid)**
   - 964 位开发者卡片名录。
   - 显示 X / GitHub 账号绑定、报名意图标签（强报名/报名/仅兴趣等）、身份置信度标签（显式确认/来源映射/未确认）。
   - 实时计算开发者名下代表项目数与最高 Star 数，点击卡片直达开发者详情页。

6. **项目详情页 (Project Detail View)**
   - 完美还原专属设计（包含 `← 返回目录` 导航）。
   - 赛道标签、DeepSeek 相关性标签、许可证标签。
   - 36px 醒目仓库名称与详细描述，标注描述来源。
   - 一键跳转按钮 `GitHub 仓库 ↗`（自动调用系统默认浏览器打开 GitHub 页面）。
   - 8 维 KPI 指标卡片（Stars、Forks、主语言、许可证、上线时间、最后更新、最新 Release、Owner 类型）。
   - README 摘要预览板块。

7. **开发者详情页 (Developer Detail View)**
   - 开发者基础资料卡片、GitHub / X 个人主页跳转。
   - 开发者提交的名下全部开源项目表格，支持点击表格直接穿透跳转项目详情。

8. **异步加载与数据刷新 (Loading & Remote Refresh)**
   - 页面切换与筛选时显示半透明遮罩加载动画 (`LoadingOverlay`)。
   - 顶部导航栏配备「🔄 刷新」按钮，支持一键实时重新获取与同步档案数据。

---

## 运行方式

### 1. 快速启动
```bash
# 安装依赖
pip install -r requirements.txt

# 启动应用
python3 main.py
```

或使用启动脚本：
```bash
./run_app.sh
```

---

## 目录结构

```
├── core/
│   └── data_loader.py          # 数据加载器与单例 DataStore、筛选/排序/索引算法
├── data/
│   ├── developers.json         # 开发者档案数据 (964 位)
│   ├── featured-projects.json  # 精选项目数据
│   ├── projects.json           # 项目全量数据 (877 个)
│   └── stats.json              # 统计指标数据
├── gui/
│   ├── components/             # UI 组件
│   │   ├── about_view.py       # 关于页面
│   │   ├── categories_view.py  # 赛道页面
│   │   ├── developer_detail_view.py # 开发者详情页
│   │   ├── developers_view.py  # 开发者目录
│   │   ├── home_view.py        # 总览仪表盘
│   │   ├── leaderboard_view.py # 项目排行榜
│   │   ├── project_detail_view.py   # 项目详情页 (图片3样式)
│   │   ├── projects_view.py    # 项目目录
│   │   └── widgets.py          # 通用小部件 (ChipRow, PagerWidget, LoadingOverlay, ProjectCard 等)
│   ├── main_window.py          # 主窗口导航与 Stack 路由
│   └── styles.py               # 深色主题全局 QSS 样式表
├── main.py                     # 应用入口
├── README.md                   # 项目说明
└── requirements.txt            # Python 依赖清单
```
