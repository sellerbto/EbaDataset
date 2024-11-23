from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence, cast

from sqlalchemy import cast, DateTime
from sqlalchemy import func
from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession, AsyncSessionTransaction


from app.models import Dataset, DatasetUsageHistory, AccessRights, EventType, RemoteDataset
from app.schemas.requests import ClientRequest, UrlAndDescRequest


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

    async def get_all_datasets(self) -> Sequence[Dataset]:
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

    async def get_usage_events_by_dataset(self, dataset_name: str) -> Sequence[DatasetUsageHistory]:
        result = await self.session.execute(
            select(DatasetUsageHistory)
            .where(DatasetUsageHistory.dataset_name == dataset_name)
            .order_by(DatasetUsageHistory.event_time.desc())
        )
        return result.scalars().all()

    async def get_usage_events_by_host(self, host_name: str) -> Sequence[DatasetUsageHistory]:
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


    async def add_event(self, client_request: ClientRequest):
        async with self.session.begin_nested() as transaction:
            transaction: AsyncSessionTransaction
            event_types = [
                EventType.READ,
                EventType.MODIFY,
                EventType.CREATE
            ]

            event_times = [
                client_request.last_access_date,
                client_request.last_modification_date,
                client_request.age
            ]

            event_added = False

            for event_type, event_time in zip(event_types, event_times):
                stmt = select(DatasetUsageHistory).filter(
                    DatasetUsageHistory.host_name == client_request.hostname,
                    DatasetUsageHistory.dataset_name == client_request.dataset_name,
                    DatasetUsageHistory.event_type == event_type,
                    DatasetUsageHistory.event_time == cast(event_time.replace(tzinfo=None), DateTime)
                )

                result = await transaction.session.execute(stmt)
                length = len(result.scalars().all())
                print(f'LENGTH - {length}')
                if length == 0:
                    event_added = True
                    new_event = DatasetUsageHistory(
                        host_name=client_request.hostname,
                        dataset_name=client_request.dataset_name,
                        event_type=event_type,
                        event_time=(
                            datetime.fromtimestamp(event_time, tz=timezone.utc).replace(tzinfo=None)
                            if isinstance(event_time, float)
                            else event_time.replace(tzinfo=None) if isinstance(event_time, datetime) and event_time.tzinfo
                            else event_time
                        )
                    )
                    transaction.session.add(new_event)

                    if event_type == EventType.CREATE:
                        new_dataset = Dataset(
                            name=client_request.dataset_name,
                            size=100,
                            host=client_request.hostname,
                            created_at_device=client_request.last_modification_date,
                            last_accessed=client_request.last_access_date,

                        )
                        transaction.session.add(new_dataset)
                    elif event_type == EventType.DELETE:
                        stmt = delete(Dataset).where(
                                Dataset.host == client_request.hostname,
                                DatasetUsageHistory.dataset_name == client_request.dataset_name)
                        await transaction.session.execute(stmt)
                    else:
                        stmt = (
                            update(Dataset).where(
                                Dataset.host == client_request.hostname,
                                DatasetUsageHistory.dataset_name == client_request.dataset_name)
                            .values (
                                {
                                    Dataset.last_modified: client_request.last_modification_date,
                                    Dataset.last_accessed: client_request.last_access_date,
                                }))
                        await transaction.session.execute(stmt)

            await transaction.commit()
            return event_added

    async def get_events_statistic(self, host_name: str, dataset_name: str):
        stmt = select(
            DatasetUsageHistory.event_type,
            func.count(DatasetUsageHistory.event_type).label('event_count')
        ).filter(
            DatasetUsageHistory.host_name == host_name,
            DatasetUsageHistory.dataset_name == dataset_name
        ).group_by(DatasetUsageHistory.event_type)

        # Выполняем запрос
        result = await self.session.execute(stmt)

        # Преобразуем результат в словарь
        event_statistics = {event_type: count for event_type, count in result.fetchall()}

        return event_statistics

    async def get_events_statistic_by_time(self, host_name: str, dataset_name: str, timestamp: timedelta):
        stmt = select(
            DatasetUsageHistory.event_type,
            func.count(DatasetUsageHistory.event_type).label('event_count')
        ).filter(
            DatasetUsageHistory.host_name == host_name,
            DatasetUsageHistory.dataset_name == dataset_name,
            datetime.now() - DatasetUsageHistory.event_time > timestamp
        ).group_by(DatasetUsageHistory.event_type)

        # Выполняем запрос
        result = await self.session.execute(stmt)

        # Преобразуем результат в словарь
        event_statistics = {event_type: count for event_type, count in result.fetchall()}

        return event_statistics


class RemoteDatasetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all_urls_and_descs(self):
        stmt = select(RemoteDataset.url)

        result = await self.session.execute(stmt)

        return {url: desc for url, desc in result.fetchall()}


    async def add_url_desc_pair(self, request: UrlAndDescRequest):
        self.session.add(RemoteDataset(url=request.url, desc=request.desc))
