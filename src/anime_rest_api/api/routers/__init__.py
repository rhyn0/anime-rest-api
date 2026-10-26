from .episodes_routes import ROUTER as EPISODES_ROUTER
from .session_routes import ROUTER as SESSION_ROUTER
from .shows_routes import ROUTER as SHOW_ROUTER
from .user_episodes_routes import ROUTER as USER_EPISODES_ROUTER
from .user_routes import ROUTER as USER_ROUTER
from .user_shows_routes import ROUTER as USER_SHOWS_ROUTER

__all__ = [
    "SHOW_ROUTER",
    "USER_ROUTER",
    "SESSION_ROUTER",
    "EPISODES_ROUTER",
    "USER_SHOWS_ROUTER",
    "USER_EPISODES_ROUTER",
]
