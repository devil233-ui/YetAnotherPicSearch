"""搜图过程中的上下文变量。

`ascii2d` 的上传接口被 Cloudflare 硬拦（`/search/file` 一律 403 挑战），
但 URL 搜索接口（`/search/uri`）正常。这里用 contextvar 把当前图片的原始
URL 传给数据源，供其改走 URL 模式。
"""

from contextvars import ContextVar

current_image_url: ContextVar[str | None] = ContextVar("current_image_url", default=None)
