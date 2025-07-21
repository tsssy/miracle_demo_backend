from .echo import router as echo_router
from .upper import router as upper_router
from .reverse import router as reverse_router

all_ws_routers = [echo_router, upper_router, reverse_router] 