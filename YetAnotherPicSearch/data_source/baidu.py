from typing import TYPE_CHECKING

from nonebot_plugin_alconna.uniseg import UniMessage
from PicImageSearch import BaiDu

from ..registry import SearchFunctionReturnType, search_function
from ..utils import async_lock, combine_message, handle_img, shorten_url

if TYPE_CHECKING:
    from httpx import AsyncClient


@search_function("baidu")
@async_lock()
async def baidu_search(
    file: bytes,
    client: "AsyncClient",
    _: str,
) -> SearchFunctionReturnType:
    baidu = BaiDu(client=client)
    res = await baidu.search(file=file)
    _url = await shorten_url(res.url)
    if not res.raw and not res.exact_matches:
        return [UniMessage.text(f"Baidu 搜索结果为空\n搜索页面：{_url}")]
    res_list = []
    if res.exact_matches:
        same = res.exact_matches[0]
        res_list += [
            "Baidu 图片来源",
            await handle_img(same.thumbnail),
            same.title,
            same.url,
        ]
    if res.raw:
        first = res.raw[0]
        res_list += [
            "Baidu 相似图",
            await handle_img(first.thumbnail),
            first.title or first.url,
        ]
    res_list.append(f"搜索页面：{_url}")
    return [combine_message(res_list)]
