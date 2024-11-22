from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models import Dataset, DatasetUsageHistory, AccessRights, EventType

from sqlalchemy import update, delete
from typing import Optional, List

class DatasetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(self, name: str, size: int, created_at_device: datetime, access_rights: AccessRights):
        dataset = Dataset(
            name=name,
            size=size,
            created_at_device=created_at_device,
            access_rights=access_rights,
        )
        self.session.add(dataset)
        await self.session.commit()
        return dataset

    async def get_dataset_by_id(self, dataset_id: int) -> Optional[Dataset]:
        result = await self.session.execute(
            select(Dataset).where(Dataset.id == dataset_id)
        )
        return result.scalars().first()

    async def get_all_datasets(self) -> List[Dataset]:
        result = await self.session.execute(select(Dataset))
        return result.scalars().all()

    async def update_dataset(self, dataset_id: int, **kwargs):
        await self.session.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .values(**kwargs)
        )
        await self.session.commit()

    async def delete_dataset(self, dataset_id: int):
        await self.session.execute(
            delete(Dataset).where(Dataset.id == dataset_id)
        )
        await self.session.commit()


class DatasetUsageHistoryRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_usage_event(self, host_name: str, dataset_name: str, event_type: EventType, event_time: datetime):
        usage_event = DatasetUsageHistory(
            host_name=host_name,
            dataset_name=dataset_name,
            event_type=event_type,
            event_time=event_time,
        )
        self.session.add(usage_event)
        await self.session.commit()
        return usage_event

    async def get_usage_events_by_dataset(self, dataset_name: str) -> List[DatasetUsageHistory]:
        result = await self.session.execute(
            select(DatasetUsageHistory)
            .where(DatasetUsageHistory.dataset_name == dataset_name)
            .order_by(DatasetUsageHistory.event_time.desc())
        )
        return result.scalars().all()

    async def get_usage_events_by_host(self, host_name: str) -> List[DatasetUsageHistory]:
        result = await self.session.execute(
            select(DatasetUsageHistory)
            .where(DatasetUsageHistory.host_name == host_name)
            .order_by(DatasetUsageHistory.event_time.desc())
        )
        return result.scalars().all()

    async def delete_events_older_than(self, timestamp: datetime):
        await self.session.execute(
            delete(DatasetUsageHistory).where(DatasetUsageHistory.event_time < timestamp)
        )
        await self.session.commit()
