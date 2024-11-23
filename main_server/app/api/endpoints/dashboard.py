from datetime import datetime
from fastapi import APIRouter, Depends

from app.core.repository import DatasetRepository, DatasetUsageHistoryRepository

from app.schemas.responses import DatasetInfo
from app.models import Dataset

from app.api import deps

from typing import List

router = APIRouter()
repository = DatasetRepository(Depends(deps.get_session))
eventsRepository = DatasetUsageHistoryRepository(Depends(deps.get_session))


@router.get("/dataset_infos", response_model=List[DatasetInfo], description="Get list of dataset infos")
async def get_datasets_info(

    datasets:  List[Dataset] = Depends(repository.get_all_datasets),
) -> List[DatasetInfo] :
    infos = []

    stats_time = datetime(year=0, month=1, day=0)


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
