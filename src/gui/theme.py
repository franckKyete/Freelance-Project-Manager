"""GUI style constants and theme helpers for the Freelance Project Manager."""

# ── Colour Palette ─────────────────────────────────────────────────────
BG_DARK = "#0f1117"          # main background
BG_PANEL = "#1a1d27"         # sidebar + card background
BG_CARD = "#222637"          # inner card / treeview background
ACCENT = "#6c63ff"           # primary purple accent
ACCENT_HOVER = "#8179ff"     # accent on hover
ACCENT_2 = "#00d4aa"         # teal secondary accent
SUCCESS = "#22c55e"          # green success
WARNING = "#f59e0b"          # amber warning
DANGER = "#ef4444"           # red danger
FG_PRIMARY = "#f1f5f9"       # main text
FG_SECONDARY = "#94a3b8"     # muted text
FG_MUTED = "#475569"         # very muted
BORDER = "#2e3347"           # subtle borders

# ── Typography ──────────────────────────────────────────────────────────
FONT_FAMILY = "Inter"
FONT_FALLBACK = "Segoe UI"

FONT_H1 = (FONT_FAMILY, 22, "bold")
FONT_H2 = (FONT_FAMILY, 16, "bold")
FONT_H3 = (FONT_FAMILY, 12, "bold")
FONT_BODY = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_MONO = ("Courier New", 10)

# ── Sizing ──────────────────────────────────────────────────────────────
SIDEBAR_W = 200
CONTENT_PAD = 20
CARD_PAD = 16
CORNER_RADIUS = 8

# ── Status badge colours ────────────────────────────────────────────────
STATUS_COLORS = {
    "active": ACCENT_2,
    "on_hold": WARNING,
    "completed": SUCCESS,
    "cancelled": DANGER,
    "pending": WARNING,
    "sent": ACCENT,
    "paid": SUCCESS,
    "overdue": DANGER,
    "todo": FG_MUTED,
    "in_progress": ACCENT,
    "review": WARNING,
    "done": SUCCESS,
}
