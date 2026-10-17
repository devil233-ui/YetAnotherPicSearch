import math
from typing import TYPE_CHECKING, Any

from nonebot_plugin_alconna.uniseg import UniMessage
from PicImageSearch import TraceMoe

from ..config import config
from ..utils import async_lock, combine_message, handle_img

if TYPE_CHECKING:
    from httpx import AsyncClient

    from ..registry import SearchFunctionReturnType


@async_lock()
async def whatanime_search(
    file: bytes,
    client: "AsyncClient",
    _: str,
) -> "SearchFunctionReturnType":
    whatanime = TraceMoe(client=client)
    res = await whatanime.search(file=file)
    if res and res.raw:
        item = res.raw[0]
        time = item.From
        minutes = math.floor(time / 60)
        seconds = math.floor(time % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"
        episode = item.episode or 1

        res_list = [
            f"WhatAnime ({item.similarity}%)",
            f"该截图出自第 {episode} 集的 {time_str}",
        ]

        # AniList 侧被限流/封禁时拿不到标题与封面，此时只展示本地可得的
        # 文件名、集数与时间，避免因空字典直接抛异常导致整条搜索失败。
        if item.title_native or item.title_chinese:
            thumbnail = None
            if item.cover_image:
                thumbnail = await handle_img(
                    item.cover_image,
                    item.isAdult
                    and (config.hide_img or config.hide_img_when_whatanime_r18),
                )

            chinese_title = item.title_chinese
            native_title = item.title_native
            start_date = date_to_str(item.start_date) if item.start_date else ""
            end_date = ""
            if (end_year := item.end_date.get("year")) and end_year > 0:
                end_date = date_to_str(item.end_date)
            res_list += [
                thumbnail,
                native_title,
                chinese_title if chinese_title != native_title else "",
                f"类型：{item.type}-{item.format}",
                f"开播：{start_date}",
                f"完结：{end_date}" if end_date else "",
            ]
        else:
            res_list.append(f"文件名：{item.filename}")

        return [combine_message(res_list)]

    return [UniMessage.text("WhatAnime 暂时无法使用")]


def date_to_str(date: dict[str, Any]) -> str:
    # AniList 的日期字段可能缺日/月，拼接时跳过空值而不是抛 KeyError
    return "-".join(str(date[key]) for key in ("year", "month", "day") if date.get(key))
