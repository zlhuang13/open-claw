"""Home module - bin collection, household info."""
import html as html_mod
from datetime import datetime

ROUTE = '/home'
TITLE = '🏠 Home'
ICON = '🏠'
DESCRIPTION = '垃圾提醒 · 日常管理'

from common import BIN_CACHE_PATH

BIN_CACHE = str(BIN_CACHE_PATH)


def is_enabled():
    return True


def nav():
    return '<a href="/">🩵 UMI</a><span class="sep">›</span><span>Home</span>'


def render():
    try:
        with open(BIN_CACHE, 'r') as f:
            bin_info = f.read().strip()
        bin_html = html_mod.escape(bin_info).replace('\n', '<br>')
    except Exception:
        bin_html = '暂无数据，请稍后刷新'

    now = datetime.utcnow()
    weekday = ['一', '二', '三', '四', '五', '六', '日'][now.weekday()]
    date_str = now.strftime('%Y-%m-%d')

    return f'''<h1>🏠 Home</h1>
<p class="stats">{date_str} 星期{weekday}</p>
<p class="subtitle">家庭模块首页，这里可以继续扩展更多日常管理卡片。</p>
<div class="home-subgrid">
    <div class="home-card home-subcard">
        <div class="subcard-kicker">Household</div>
        <h3>🗑️ 垃圾提醒</h3>
        <div class="bin-info">{bin_html}</div>
        <p class="hint">📍 26 Oak Hill Lane, Didcot OX11 6AP · 每周五收集 · 数据每周四更新</p>
    </div>
    <div class="home-card home-subcard soft">
        <div class="subcard-kicker">More soon</div>
        <h3>✨ 家庭模块</h3>
        <p class="hint">后续这里可以继续放收纳、清单、家务提醒等家庭小模块。</p>
    </div>
</div>'''
