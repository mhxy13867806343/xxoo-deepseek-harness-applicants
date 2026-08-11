import os
import json
from datetime import datetime

# -----------------------------------------------------------------------------
# Constants
# -----------------------------------------------------------------------------

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

INTENT_LABELS = {
    "strong_application": "强报名", 
    "application": "报名", 
    "interest_only": "仅兴趣",
    "profile_only": "仅主页", 
    "unknown": "未知", 
    "bot": "机器人", 
    "noise_or_comment": "灌水/评论",
}

IDENTITY_LABELS = {
    "explicit": "显式确认", 
    "mapped": "来源映射", 
    "unconfirmed": "未确认", 
    "bot": "机器人"
}

LANG_COLORS = {
    "Python": "#3572A5",
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Rust": "#dea584",
    "Go": "#00ADD8",
    "Java": "#b07219",
    "C++": "#f34b7d",
    "C": "#555555",
    "C#": "#178600",
    "Shell": "#89e051",
    "HTML": "#e34c26",
    "Swift": "#F05138",
    "(none)": "#666666"
}

TIER_META = {
    "S_10k": {"label": "S (10k+)", "color": "#e3b341"},
    "A_1k": {"label": "A (1k-10k)", "color": "#d4a373"},
    "B_100": {"label": "B (100-1k)", "color": "#a8dadc"},
    "C_1": {"label": "C (1-100)", "color": "#457b9d"},
    "Z_0": {"label": "Z (0)", "color": "#1d3557"}
}

GAP_META = {
    "missing_explicit_github_id_with_project": "Missing Github ID",
    "no_project": "No Project",
    "github_404": "Github 404",
    "empty_description": "Empty Description",
    "unclassified": "Unclassified",
    "no_homepage": "No Homepage"
}


# -----------------------------------------------------------------------------
# Utility Functions
# -----------------------------------------------------------------------------

def fmt_num(n):
    """Format number with commas (e.g. 12,345)"""
    try:
        return f"{int(n):,}"
    except (ValueError, TypeError):
        return str(n)

def fmt_k(n):
    """Format as 1.2k, 3.4M etc"""
    try:
        n = float(n)
        if n >= 1000000:
            return f"{n/1000000:.1f}M"
        if n >= 1000:
            return f"{n/1000:.1f}k"
        return str(int(n))
    except (ValueError, TypeError):
        return str(n)

def fmt_date(iso_str):
    """Format ISO date to YYYY-MM-DD"""
    if not iso_str:
        return ""
    return iso_str.split('T')[0]

def cat_of(val):
    """Return {zh, desc} category dict for a category ID or project dict"""
    if isinstance(val, dict):
        cat_id = val.get('category') or val.get('cat_id') or val.get('cat') or 'unclassified'
    else:
        cat_id = val
    if not isinstance(cat_id, str):
        cat_id = str(cat_id) if cat_id else 'unclassified'
    return CATS.get(cat_id, CATS.get("unclassified", {"zh": cat_id, "desc": ""}))

def sort_projects(project_list, sort_key='stars', by=None):
    """Sort by stars/pushed/updated/created/name"""
    key = by or sort_key
    if key == 'stars':
        return sorted(project_list, key=lambda x: (x.get('metrics', {}).get('stars', 0) if isinstance(x.get('metrics'), dict) else (x.get('stars', 0) if isinstance(x.get('stars'), int) else 0)), reverse=True)
    elif key in ('pushed', 'updated'):
        return sorted(project_list, key=lambda x: (x.get('metrics', {}).get('pushed_at', '') if isinstance(x.get('metrics'), dict) else (x.get('updated_at') or '')), reverse=True)
    elif key == 'created':
        return sorted(project_list, key=lambda x: (x.get('metrics', {}).get('created_at', '') if isinstance(x.get('metrics'), dict) else (x.get('created_at') or '')), reverse=True)
    elif key == 'name':
        return sorted(project_list, key=lambda x: (x.get('name') or x.get('repo') or x.get('repo_id') or '').lower())
    return project_list

def filter_projects(projects, cat='', lang='', ds=False, high=False, home=False, query='', ds_only=None, high_only=None, home_only=None):
    """Filter projects based on multiple criteria"""
    if ds_only is not None:
        ds = ds_only
    if high_only is not None:
        high = high_only
    if home_only is not None:
        home = home_only

    filtered = []
    for p in projects:
        if cat and (p.get('category') or p.get('cat')) != cat:
            continue
        if lang and p.get('language') != lang:
            continue
        if ds and not (p.get('deepseek_native') or p.get('ds_related')):
            continue
        if high:
            stars = p.get('metrics', {}).get('stars', 0) if isinstance(p.get('metrics'), dict) else p.get('stars', 0)
            if stars < 1000:
                continue
        if home and not p.get('homepage'):
            continue
        if query:
            q = query.lower()
            name = (p.get('name') or p.get('repo') or p.get('repo_id') or '').lower()
            desc = (p.get('description') or '').lower()
            if q not in name and q not in desc:
                continue
        filtered.append(p)
    return filtered

def filter_developers(developers, intent='all', identity='all', has_project='all', query=''):
    """Filter developers based on multiple criteria"""
    filtered = []
    for d in developers:
        if intent != 'all' and d.get('intent') != intent:
            continue
        idc = d.get('identity_confidence') or d.get('identity')
        if identity != 'all' and idc != identity:
            continue
        if has_project != 'all':
            p_count = d.get('project_count') or len(d.get('projects') or [])
            if has_project == 'yes' and p_count == 0:
                continue
            if has_project == 'no' and p_count > 0:
                continue
        if query:
            q = query.lower()
            x_handle = (d.get('x') or '').lower()
            gh_user = (d.get('github') or '').lower()
            name = (d.get('name') or '').lower()
            excerpt = (d.get('excerpt') or '').lower()
            bio = (d.get('bio') or '').lower()
            company = (d.get('company') or '').lower()
            location = (d.get('location') or '').lower()
            if not any(q in text for text in [x_handle, gh_user, name, excerpt, bio, company, location]):
                continue
        filtered.append(d)
    return filtered


import urllib.request


def fetch_live_json(url, timeout=6):
    """Fetch live JSON payload from remote web server."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'HarnessIndex/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data_bytes = resp.read()
                return json.loads(data_bytes.decode('utf-8'))
    except Exception as e:
        print(f"Failed to fetch online dataset endpoint {url}: {e}")
    return None


class DataStore:
    def __init__(self):
        self.stats = {}
        self.projects = []
        self.featured = []
        self.developers = []
        self.dev_by_x = {}
        self.proj_by_name = {}
        
    def load(self, force_remote=True):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        base_remote_url = "https://deepseek-harness-applicants.octoooo.com/data"
        remote_endpoints = {
            'stats.json': f"{base_remote_url}/stats.json",
            'projects.json': f"{base_remote_url}/projects.json",
            'developers.json': f"{base_remote_url}/developers.json",
            'featured-projects.json': f"{base_remote_url}/featured-projects.json"
        }

        # Attempt to fetch live dynamic datasets via HTTP
        for filename, remote_url in remote_endpoints.items():
            live_data = fetch_live_json(remote_url)
            if live_data:
                local_path = os.path.join(data_dir, filename)
                try:
                    with open(local_path, 'w', encoding='utf-8') as f:
                        json.dump(live_data, f, ensure_ascii=False, indent=2)
                    try:
                        from core.logger import app_logger
                        app_logger.info("HTTP", f"成功同步在线动态数据 -> {filename}")
                    except Exception:
                        pass
                except Exception as e:
                    print(f"Error caching live {filename}: {e}")

        # Load JSON from data directory
        def load_json(filename):
            path = os.path.join(data_dir, filename)
            if not os.path.exists(path):
                return {}
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading {filename}: {e}")
                return {}

        self.stats = load_json('stats.json')
        
        projects_data = load_json('projects.json')
        self.projects = projects_data.get('projects', []) if isinstance(projects_data, dict) else (projects_data if isinstance(projects_data, list) else [])
        
        featured_data = load_json('featured-projects.json')
        self.featured = featured_data.get('projects', []) if isinstance(featured_data, dict) else (featured_data if isinstance(featured_data, list) else [])
        
        dev_data = load_json('developers.json')
        self.developers = dev_data.get('developers', []) if isinstance(dev_data, dict) else (dev_data if isinstance(dev_data, list) else [])
        
        # Build indexes
        self.dev_by_x = {}
        for dev in self.developers:
            x_handle = dev.get('x') or dev.get('handle') or dev.get('github') or dev.get('id')
            if x_handle:
                self.dev_by_x[x_handle] = dev
                
        self.proj_by_name = {}
        for proj in self.projects:
            name = proj.get('name') or proj.get('repo_id') or proj.get('repo')
            if name:
                self.proj_by_name[name] = proj

    def get_project(self, key):
        if not key:
            return None
        if isinstance(key, dict):
            return key
        if key in self.proj_by_name:
            return self.proj_by_name[key]
        key_lower = str(key).lower()
        for p in self.projects:
            p_name = (p.get('name') or p.get('repo_id') or p.get('repo') or '').lower()
            if p_name == key_lower or p_name.endswith('/' + key_lower):
                return p
        return None

    def get_developer(self, key):
        if not key:
            return None
        if isinstance(key, dict):
            return key
        if key in self.dev_by_x:
            return self.dev_by_x[key]
        key_lower = str(key).lower()
        for d in self.developers:
            d_x = (d.get('x') or d.get('github') or d.get('name') or '').lower()
            if d_x == key_lower:
                return d
        return None

# Global instance
data_store = DataStore()
