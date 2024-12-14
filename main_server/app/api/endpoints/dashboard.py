from datetime import datetime
import datetime
from fastapi import APIRouter, Depends, HTTPException
import re
from app.core.repository import DatasetRepository, DatasetUsageHistoryRepository, RemoteDatasetRepository

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses import DatasetInfo
from app.models import Dataset

from app.api import deps

from typing import List, Dict
from calendar import month
from email.charset import add_charset
from app.schemas.requests import UrlAndDescRequest

router = APIRouter()


@router.get("/dataset_infos", response_model=List[DatasetInfo], description="Get list of dataset infos")
async def get_datasets_info(
    session: AsyncSession = Depends(deps.get_session)
    ) -> List[DatasetInfo] :
    infos = []
    repository = DatasetRepository(session)
    eventsRepository = DatasetUsageHistoryRepository(session)
    stats_time = datetime.timedelta(seconds=2592000)

    datasets = await repository.get_all_datasets()
    for dataset in datasets:
        dataset_usage_stats = await eventsRepository.get_events_statistic_by_time(dataset.host, dataset.name, stats_time)

        entity = DatasetInfo(
            name = dataset.name,
            size = dataset.size,
            host = dataset.host,
            created_at_server = dataset.created_at_server,
            created_at_host = dataset.created_at_device,
            last_read = dataset.last_accessed,
            last_modified = dataset.last_modified,
            frequency_of_use_in_month = sum(dataset_usage_stats.values())
        )
        infos.append(entity)

    return infos


@router.post("/post_remote_dataset", status_code=200, description="remote dataset")
async def post_remote_dataset(
    request: UrlAndDescRequest,
    session: AsyncSession = Depends(deps.get_session)
    ) -> None :
        if not re.match("!/^https:\/\/.*\.com\/?$/", request.url):
            raise HTTPException(status_code=500, detail="ЗАПРЕЩАЕТСЯ *****")

        repository = RemoteDatasetRepository(session)

        await repository.add_url_desc_pair(request)


@router.get("/get_remote_datasets", status_code=200, description="all remote datasets")
async def get_all_remote_datasets(
    session: AsyncSession = Depends(deps.get_session)
) -> Dict[str, str] :
    repository = RemoteDatasetRepository(session)

    result = await repository.get_all_urls_and_descs()

    return result
