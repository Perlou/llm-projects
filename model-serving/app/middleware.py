"""
中间件模块
"""

import time
import logging
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """请求日志中间件"""

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()

        # 处理请求
        response = await call_next(request)

        # 计算耗时
        duration = (time.time() - start_time) * 1000

        # 记录日志
        logger.info(
            f"{request.method} {request.url.path} - "
            f"{response.status_code} - {duration:.2f}ms"
        )

        # 添加响应头
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        return response


class CORSMiddleware(BaseHTTPMiddleware):
    """CORS 中间件"""

    async def dispatch(self, request: Request, call_next):
        # 处理预检请求
        if request.method == "OPTIONS":
            from starlette.responses import Response

            response = Response()
        else:
            response = await call_next(request)

        # 添加 CORS 头
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return response
