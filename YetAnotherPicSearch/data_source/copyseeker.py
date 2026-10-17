from typing import TYPE_CHECKING

from nonebot_plugin_alconna.uniseg import UniMessage
from PicImageSearch import Copyseeker

from ..config import config
from ..registry import SearchFunctionReturnType, search_function
from ..utils import async_lock, combine_message, get_source, handle_img, shorten_url

if TYPE_CHECKING:
    from httpx import AsyncClient


@search_function("copyseeker")
@async_lock()
async def copyseeker_search(
    file: bytes,
    client: "AsyncClient",
    _: str,
) -> SearchFunctionReturnType:
    copyseeker = Copyseeker(client=client)
    res = await copyseeker.search(file=file)
    if not res.raw:
        return [UniMessage.text("Copyseeker 暂时无法使用")]

    label = res.best_guess_label or "未知"
    res_list: list = [f"Copyseeker（识别为 {label}，找到 {res.total} 个来源）"]
    for item in res.raw[:3]:
        thumbnail = await handle_img(item.thumbnail, config.hide_img)
        source = await get_source(item.url)
        res_list += [
            thumbnail,
            item.title[:80] if item.title else "",
            await shorten_url(item.url),
            f"来源：{source}" if source else "",
        ]
    res_list.append(f"搜索页面：{res.url}")
    return [combine_message(res_list)]
