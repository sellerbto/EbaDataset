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
        events = []

        stmt = select(DatasetUsageHistory).filter(
            DatasetUsageHistory.host_name == client_request.hostname,
            DatasetUsageHistory.dataset_name == client_request.dataset_name
        )
        result = await self.session.execute(stmt)
        existing_records = result.scalars().all()

        latest_records = {}
        for record in existing_records:
            if record.event_type not in latest_records or record.event_time > latest_records[
                record.event_type].event_time:
                latest_records[record.event_type] = record

        for event_type, event_time in zip(event_types, event_times):
            normalized_time = self._normalize_event_time(event_time)
            if event_type in latest_records:
                latest_event = latest_records[event_type]
                if event_type == EventType.READ and latest_event.event_time != normalized_time:
                    new_event = DatasetUsageHistory(
                        host_name=client_request.hostname,
                        dataset_name=client_request.dataset_name,
                        event_type=EventType.READ,
                        event_time=normalized_time
                    )
                    self.session.add(new_event)
                    events.append(EventType.READ)

                elif event_type == EventType.MODIFY and latest_event.event_time != normalized_time:
                    new_event = DatasetUsageHistory(
                        host_name=client_request.hostname,
                        dataset_name=client_request.dataset_name,
                        event_type=EventType.MODIFY,
                        event_time=normalized_time
                    )
                    self.session.add(new_event)
                    events.append(EventType.MODIFY)
            else:
                new_event = DatasetUsageHistory(
                    host_name=client_request.hostname,
                    dataset_name=client_request.dataset_name,
                    event_type=event_type,
                    event_time=normalized_time
                )
                self.session.add(new_event)
                events.append(event_type)

        if not existing_records:
            create_event = DatasetUsageHistory(
                host_name=client_request.hostname,
                dataset_name=client_request.dataset_name,
                event_type=EventType.CREATE,
                event_time=self._normalize_event_time(client_request.age)
            )
            self.session.add(create_event)
            events.append(EventType.CREATE)

        await self.session.commit()
        return events

    def _normalize_event_time(self, event_time):
        return (
            datetime.fromtimestamp(event_time, tz=timezone.utc).replace(tzinfo=None)
            if isinstance(event_time, float)
            else event_time.replace(tzinfo=None) if isinstance(event_time, datetime) and event_time.tzinfo
            else event_time
        )

    async def get_events_statistic_by_time(self, host_name: str, dataset_name: str, timestamp: timedelta):
        stmt = select(
            DatasetUsageHistory.event_type,
            func.count(DatasetUsageHistory.event_type).label('event_count')
        ).filter(
            DatasetUsageHistory.host_name == host_name,
            DatasetUsageHistory.dataset_name == dataset_name,
            datetime.now() - DatasetUsageHistory.event_time > timestamp
        ).group_by(DatasetUsageHistory.event_type)

        result = await self.session.execute(stmt)
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
