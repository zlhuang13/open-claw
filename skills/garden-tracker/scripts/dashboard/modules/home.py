"""Home module - bin collection, household info."""
import html as html_mod
import os
from datetime import datetime

ROUTE = '/home'
TITLE = '🏠 Home'
ICON = '🏠'
DESCRIPTION = '垃圾提醒 · 日常管理'

BIN_CACHE = '/home/ubuntu/.openclaw/workspace/skills/garden-tracker/data/bin_cache.txt'


def is_enabled():
    return True


def nav():
    return '<a href="/">🤍 UMI</a><span class="sep">›</span><span>Home</span>'


def render():
    try:
        with open(BIN_CACHE, 'r') as f:
            bin_info = f.read().strip()
        bin_html = html_mod.escape(bin_info).replace('\n', '<br>')
    except Exception:
        bin_html = '暂无数据，请稍后刷新'

    now = datetime.utcnow()
    weekday = ['一','二','三','四','五','六','日'][now.weekday()]
    date_str = now.strftime('%Y-%m-%d')

    return f'''<h1>🏠 Home</h1>
<p class="stats">{date_str} 星期{weekday}</p>
<h2>🗑️ 垃圾收集</h2>
<div class="home-card">
    <div class="bin-info">{bin_html}</div>
    <p class="hint">📍 26 Oak Hill Lane, Didcot OX11 6AP · 每周五收集 · 数据每周四更新</p>
</div>'''
