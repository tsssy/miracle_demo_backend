from .base import router as base_router
from .message import router as message_router
from .match import router as match_router

all_ws_routers = [
    base_router,
    message_router,
    match_router
] 