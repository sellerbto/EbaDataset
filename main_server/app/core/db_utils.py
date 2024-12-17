from typing import List

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api import deps
from app.models import Dataset, DatasetGeneralInfo
from app.schemas.responses import DatasetInfo, DatasetsSummary


async def get_dataset_infos(session: AsyncSession = Depends(deps.get_session)) -> DatasetsSummary:
    query = (
        select(Dataset, DatasetGeneralInfo)
        .join(DatasetGeneralInfo, Dataset.dataset_general_info)
    )
    result = await session.execute(query)
    datasets = result.all()

    dataset_infos = []
    for dataset, general_info in datasets:
        print(f'dataset: {dataset}')
        print(f'general_info: {general_info}')
        dataset_infos.append(DatasetInfo(
            id=dataset.id,
            file_path=dataset.file_path,
            size=dataset.size,
            host=dataset.host,
            created_at_server=dataset.created_at_server,
            created_at_host=dataset.created_at_device
        ))

    name = general_info.name if datasets else "Unknown"
    description = general_info.description if datasets else "No description available"
    summary = DatasetsSummary(
        name=name,
        description=description,
        datasets_infos=dataset_infos
    )
    print(f'Dataset Summary:\n{summary}')
    return summary
