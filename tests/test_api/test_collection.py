from __future__ import annotations

import aiohttp
import pytest

from yutto._typing import BvId, MId, SeriesId
from yutto.api.collection import get_collection_details
from yutto.utils.fetcher import Fetcher
from yutto.utils.funcutils import as_sync


@pytest.mark.api
@as_sync
async def test_get_collection_details():
    # 测试页面：https://space.bilibili.com/6762654/channel/collectiondetail?sid=39879&ctype=0
    series_id = SeriesId("39879")
    mid = MId("6762654")
    async with aiohttp.ClientSession(
        headers=Fetcher.headers,
        cookies=Fetcher.cookies,
        trust_env=Fetcher.trust_env,
        timeout=aiohttp.ClientTimeout(total=5),
    ) as session:
        collection_details = await get_collection_details(session, series_id=series_id, mid=mid)
        title = collection_details["title"]
        avids = [page["avid"] for page in collection_details["pages"]]
        assert title == "原神傻开心整活"
        assert BvId("BV1er4y1H7tQ") in avids
        assert BvId("BV1Yi4y1C7u6") in avids
