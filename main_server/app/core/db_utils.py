from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.core.repository import DatasetUsageHistoryRepository
from app.models import Dataset, DatasetGeneralInfo
from app.schemas.responses import DatasetInfo, DatasetsSummary


async def get_dataset_summaries(session: AsyncSession = Depends(deps.get_session)) -> List[DatasetsSummary]:
    query = (
        select(DatasetGeneralInfo, Dataset)
        .outerjoin(Dataset)
    )
    result = await session.execute(query)
    rows = result.all()
    dataset_info_map = {}
    repo = DatasetUsageHistoryRepository(session)

    for general_info, dataset in rows:
        if general_info.id not in dataset_info_map:
            dataset_info_map[general_info.id] = {
                "id": general_info.id,
                "name": general_info.name,
                "description": general_info.description,
                "datasets_infos": []
            }

        if dataset:
            statistic = await repo.get_events_statistic_by_time(dataset.id)
            print(f'STATISTIC = {statistic}')
            dataset_info = DatasetInfo(
                id=dataset.id,
                file_path=dataset.file_path,
                size=dataset.size,
                host=dataset.host,
                created_at_server=dataset.created_at_server,
                created_at_host=dataset.created_at_device,
                last_read=statistic.last_read,
                last_modified=statistic.last_modified,
                frequency_of_use_in_month=statistic.frequency_of_use_in_month
            )


            dataset_info_map[general_info.id]["datasets_infos"].append(dataset_info)

    summary_list = [
        map_to_dataset_summary(
            data["id"],
            data["name"],
            data["description"],
            data["datasets_infos"]
        )
        for data in dataset_info_map.values()
    ]

    return summary_list




def map_to_dataset_summary(id, name, description, datasets: List[DatasetInfo]) -> DatasetsSummary:
    return DatasetsSummary(
        dataset_general_info_id=id,
        name=name,
        description=description,
        datasets_infos=datasets
    )