from datetime import datetime
import datetime
from fastapi import APIRouter, Depends

from app.core.repository import DatasetRepository, DatasetUsageHistoryRepository

from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.responses import DatasetInfo
from app.models import Dataset

from app.api import deps

from typing import List
from calendar import month

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
