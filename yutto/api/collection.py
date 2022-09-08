from __future__ import annotations

import asyncio
import math
from typing import TypedDict

from aiohttp import ClientSession

from yutto._typing import AvId, BvId, MId, SeriesId
from yutto.utils.fetcher import Fetcher


class CollectionDetailsItem(TypedDict):
    id: int
    title: str
    avid: AvId


class CollectionDetails(TypedDict):
    title: str
    pages: list[CollectionDetailsItem]


async def get_collection_details(session: ClientSession, series_id: SeriesId, mid: MId) -> CollectionDetails:
    title, avids = await asyncio.gather(
        _get_collection_title(session, series_id),
        _get_collection_avids(session, series_id, mid),
    )
    sub_titles = {}
    if avids:
        sub_titles = await _get_collection_sub_titles(session, series_id, avids[0])
    return CollectionDetails(
        title=title,
        pages=[
            CollectionDetailsItem(
                id=i + 1,
                title=sub_titles.get(avid.value, ""),
                avid=avid,
            )
            for i, avid in enumerate(avids)
        ],
    )


async def _get_collection_avids(session: ClientSession, series_id: SeriesId, mid: MId) -> list[AvId]:
    api = "https://api.bilibili.com/x/polymer/space/seasons_archives_list?mid={mid}&season_id={series_id}&sort_reverse=false&page_num={pn}&page_size={ps}"
    ps = 30
    pn = 1
    total = 1
    all_avid: list[AvId] = []

    while pn <= total:
        space_videos_url = api.format(series_id=series_id, ps=ps, pn=pn, mid=mid)
        json_data = await Fetcher.fetch_json(session, space_videos_url)
        assert json_data is not None
        total = math.ceil(json_data["data"]["page"]["total"] / ps)
        pn += 1
        all_avid += [BvId(archives["bvid"]) for archives in json_data["data"]["archives"]]
    return all_avid


async def _get_collection_title(session: ClientSession, series_id: SeriesId) -> str:
    api = "https://api.bilibili.com/x/v1/medialist/info?type=8&biz_id={series_id}"
    json_data = await Fetcher.fetch_json(session, api.format(series_id=series_id))
    assert json_data is not None
    return json_data["data"]["title"]


async def _get_collection_sub_titles(session: ClientSession, series_id: SeriesId, avid: AvId) -> dict:
    api = "http://api.bilibili.com/x/web-interface/view?aid={aid}&bvid={bvid}"
    sid = int(series_id.value)
    json_data = await Fetcher.fetch_json(session, api.format(**avid.to_dict()))
    assert json_data is not None
    assert json_data["data"]["ugc_season"]["id"] == sid
    assert json_data["data"]["ugc_season"]["sections"][0]["season_id"] == sid
    return {
        item["bvid"]: item["title"]
        for item in json_data["data"]["ugc_season"]["sections"][0]["episodes"]
    }
