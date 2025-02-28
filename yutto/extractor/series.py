from __future__ import annotations

import argparse
import asyncio
import re
from typing import Any, Coroutine, Optional

import aiohttp

from yutto._typing import EpisodeData, MId, SeriesId
from yutto.api.space import get_medialist_avids, get_medialist_title, get_user_name
from yutto.api.ugc_video import UgcVideoListItem, get_ugc_video_list
from yutto.exceptions import NotFoundError
from yutto.extractor._abc import BatchExtractor
from yutto.extractor.common import extract_ugc_video_data
from yutto.utils.console.logger import Badge, Logger
from yutto.utils.fetcher import Fetcher


class SeriesExtractor(BatchExtractor):
    """视频列表"""

    REGEX_SERIES = re.compile(
        r"https?://space\.bilibili\.com/(?P<mid>\d+)/channel/seriesdetail\?sid=(?P<series_id>\d+)"
    )
    REGEX_SERIES_MEDIA_LIST = re.compile(
        r"https?://www\.bilibili\.com/medialist/play/(?P<mid>\d+)\?business=space_series&business_id=(?P<series_id>\d+)"
    )

    mid: MId
    series_id: SeriesId

    def match(self, url: str) -> bool:
        if (match_obj := self.REGEX_SERIES_MEDIA_LIST.match(url)) or (match_obj := self.REGEX_SERIES.match(url)):
            self.mid = MId(match_obj.group("mid"))
            self.series_id = SeriesId(match_obj.group("series_id"))
            return True
        else:
            return False

    async def extract(
        self, session: aiohttp.ClientSession, args: argparse.Namespace
    ) -> list[Optional[Coroutine[Any, Any, Optional[EpisodeData]]]]:
        username, series_title = await asyncio.gather(
            get_user_name(session, self.mid), get_medialist_title(session, self.series_id)
        )
        Logger.custom(series_title, Badge("视频列表", fore="black", back="cyan"))

        ugc_video_info_list: list[tuple[UgcVideoListItem, str, str]] = []
        for avid in await get_medialist_avids(session, self.series_id, self.mid):
            try:
                ugc_video_list = await get_ugc_video_list(session, avid)
                await Fetcher.touch_url(session, avid.to_url())
                for ugc_video_item in ugc_video_list["pages"]:
                    ugc_video_info_list.append(
                        (
                            ugc_video_item,
                            ugc_video_list["title"],
                            ugc_video_list["pubdate"],
                        )
                    )
            except NotFoundError as e:
                Logger.error(e.message)
                continue

        return [
            extract_ugc_video_data(
                session,
                ugc_video_item["avid"],
                ugc_video_item,
                args,
                {
                    "series_title": series_title,
                    "username": username,  # 虽然默认模板的用不上，但这里可以提供一下
                    "title": title,
                    "pubdate": pubdate,
                },
                "{series_title}/{title}/{name}",
            )
            for ugc_video_item, title, pubdate in ugc_video_info_list
        ]
