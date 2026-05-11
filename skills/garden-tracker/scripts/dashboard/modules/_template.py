"""Template module - copy this to create a new dashboard module.

Rename this file (e.g. weather.py) and fill in the constants below.
The module will be auto-discovered by server.py.
"""

ROUTE = '/example'          # URL path
TITLE = '📦 Example'       # Nav/page title
ICON = '📦'                # Emoji icon for the card
DESCRIPTION = 'Short description for the home card'


def is_enabled():
    """Return True to show on home page and register route."""
    return False


def nav():
    """Breadcrumb nav HTML for the topbar."""
    return '<a href="/">🩵 UMI</a><span class="sep">›</span><span>Example</span>'


def render():
    """Return HTML content (without wrapping head/body)."""
    return '<h1>📦 Example</h1><p>Module content here.</p>'
