from datetime import datetime
import datetime
from fastapi import APIRouter, Depends, HTTPException, status
import re
from app.core.repository import DatasetRepository, DatasetUsageHistoryRepository, LinkRepository

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventType, Link
from app.schemas.responses import DatasetInfo, LinkResponse
from app.api import deps
from typing import List, Dict
from app.schemas.requests import LinkDescriptionUpdateRequest
from pydantic import HttpUrl

router = APIRouter()


@router.get("/datasets", response_model=List[DatasetInfo], description="Get list of dataset infos")
async def get_datasets_info(
    session: AsyncSession = Depends(deps.get_session)
) -> List[DatasetInfo]:
    infos = []
    repository = DatasetRepository(session)
    events_repository = DatasetUsageHistoryRepository(session)
    stats_time = datetime.timedelta(seconds=2592000)

    datasets = await repository.get_all_datasets()

    for dataset in datasets:

        latest_events = await events_repository.get_latest_events(dataset.name)
        last_read = latest_events.get(EventType.READ)
        last_modified = latest_events.get(EventType.MODIFY)

        entity = DatasetInfo(
            name=dataset.name,
            size=dataset.size,
            host=dataset.host,
            created_at_server=dataset.created_at_server,
            created_at_host=dataset.created_at_device,
            last_read=last_read,
            last_modified=last_modified,
            frequency_of_use_in_month=123,
        )
        infos.append(entity)

    return infos

@router.post("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def add_or_update_link(
    request: LinkDescriptionUpdateRequest,
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)
    return await repository.add_or_update_url(request)


@router.get("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def get_all_links(
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)

    return await repository.get_all_urls()

@router.delete("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def delete_link(
    link_url: HttpUrl,
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)

    return await repository.delete_link(str(link_url))
