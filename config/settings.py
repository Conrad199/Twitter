"""Centralized application settings and X page scripts."""

import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Configuration
# =============================================================================

DATA_DIR = PROJECT_ROOT / "data"

X_HOME_URL = "https://x.com/home"
X_SEARCH_URL = "https://x.com/search"
X_PROFILE_URL = "https://x.com/{username}"

NAME_THRESHOLD = 30  # % minimum de ressemblance du NOM pour garder le lien
MAX_LINKS_PER_COMPANY = 3  # Permet d'avoir jusqu'à 3 éléments (0, 1, 2) dans le tableau twitter

# --- MongoDB -----------------------------------------------------------------
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb://adding_social_accounts_user:45dfgd454gf26zeerf@57.129.18.234:27017/"
    "leadfeeder-social-accounts?authSource=leadfeeder-social-accounts",
)
MONGO_COLLECTION = os.environ.get("MONGO_COLLECTION", "adding_social_accounts")
MONGO_TIMEOUT_MS = 5000
SCAN_PROGRESS_EVERY = 20000

MONGO_RETRIES = 3
MONGO_RETRY_DELAY_S = 2

IGNORED_FIELDS = {"_id", "companyName", "socialAccounts", "numSocialAccounts"}

# --- Recherche X -------------------------------------------------------------
SEARCH_TABS = [
    ("Personnes", "user", "{name}"),
    ("À la une", "", "{name}"),
]
SEARCH_EXCLUDED_TERMS: list[str] = []

# --- Temporisations / tentatives ---------------------------------------------
PAGE_SETTLE_DELAY_MS = 1800
SEARCH_RESULTS_RETRY_INTERVAL_MS = 2000
MAX_SEARCH_RESULTS_ATTEMPTS = 12
MAX_PROFILE_ATTEMPTS = 6
LOGIN_POLL_INTERVAL_MS = 2000
MAX_LOG_LINES = 500

MAX_ACCOUNTS_BEFORE_PICKING_BEST = 3
BEST_ACCOUNTS_KEPT = 3  # Garde jusqu'à 3 meilleurs comptes pour remplir le tableau

PAGE_LOAD_TIMEOUT_MS = 30000

PROGRESS_FILE = DATA_DIR / "x_social_progress.json"
LEGACY_PROGRESS_FILE = PROJECT_ROOT / "x_social_progress.json"

SCAN_CACHE_FILE = DATA_DIR / "x_social_targets_cache.json"
LEGACY_SCAN_CACHE_FILE = PROJECT_ROOT / "x_social_targets_cache.json"

PHASE_SEARCH = "search"
PHASE_PROFILE = "profile"

# =============================================================================
# Scripts JavaScript injectés dans la page X
# =============================================================================

LOGGED_IN_JS = """Boolean(document.querySelector(
  '[data-testid="SideNav_AccountSwitcher_Button"], ' +
  '[data-testid="AppTabBar_Profile_Link"], ' +
  '[data-testid="AppTabBar_Home_Link"], ' +
  '[data-testid="SideNav_NewTabButton"]'
))"""

SEARCH_RESULTS_SCRIPT = (
    "(() => {\n  const loggedIn = "
    + LOGGED_IN_JS
    + """;
  const cells = Array.from(document.querySelectorAll('[data-testid="UserCell"], article[data-testid="tweet"]'));
  const users = cells.map((cell) => {
    const nameBox = cell.querySelector('[data-testid="User-Name"]') || cell;
    const spans = nameBox ? Array.from(nameBox.querySelectorAll('span')) : [];
    const name = spans.map((span) => (span.innerText || '').trim())
      .find((text) => text && !text.startsWith('@')) || '';
    const handleText = spans.map((span) => (span.innerText || '').trim())
      .map((text) => text.match(/^@([A-Za-z0-9_]{1,15})$/))
      .find(Boolean);
    const findProfileLink = (container) => Array.from(container.querySelectorAll('a[href]'))
      .find((anchor) => /^\\/[A-Za-z0-9_]{1,15}\\/?$/.test(new URL(anchor.href).pathname));
    const profileLink = findProfileLink(nameBox) || findProfileLink(cell);
    const profilePath = profileLink ? new URL(profileLink.href).pathname : '';
    const username = profilePath.match(/^\\/([A-Za-z0-9_]{1,15})\\/?$/);
    return {
      name,
      username: username ? username[1] : (handleText ? handleText[1] : ''),
      text: (cell.innerText || '').slice(0, 800),
    };
  });
  return {
    loggedIn,
    href: location.href,
    users,
    bodyText: (document.body ? document.body.innerText : '').slice(0, 4000),
  };
})()
"""
)

PROFILE_SCRIPT = (
    "(() => {\n  const loggedIn = "
    + LOGGED_IN_JS
    + """;
  const text = (selector) => {
    const element = document.querySelector(selector);
    return element ? (element.innerText || '').trim() : '';
  };
  const links = Array.from(document.querySelectorAll(
    '[data-testid="UserProfileHeader_Items"] a[href], [data-testid="UserUrl"]'
  )).map((anchor) => (anchor.href || '') + ' ' + (anchor.innerText || '')).join(' ');
  return {
    loggedIn,
    href: location.href,
    ready: Boolean(document.querySelector('[data-testid="UserName"]')),
    name: text('[data-testid="UserName"]'),
    bio: text('[data-testid="UserDescription"]'),
    items: text('[data-testid="UserProfileHeader_Items"]'),
    links,
  };
})()
"""
)