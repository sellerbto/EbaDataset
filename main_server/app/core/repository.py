from datetime import datetime, timedelta, timezone
from typing import Optional, Sequence, List

from sqlalchemy import func, desc
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.models import Dataset, DatasetUsageHistory, EventType, Link, DatasetGeneralInfo
from app.schemas.requests import DaemonClientRequest, LinkDescriptionUpdateRequest
from app.schemas.responses import Statistic, DatasetsSummary


class DatasetGeneralInfoRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, name: str, description: str) -> DatasetsSummary:
        new_record = DatasetGeneralInfo(name=name, description=description)
        self.session.add(new_record)
        await self.session.commit()
        await self.session.refresh(new_record)
        datasets_summary = DatasetsSummary(
            dataset_general_info_id=new_record.id,
            name=new_record.name,
            description=new_record.description,
            datasets_infos=[]
        )

        return datasets_summary

    async def get(self, dataset_general_info_id: int, deep: bool = True) -> DatasetGeneralInfo | None:
        query = select(DatasetGeneralInfo).where(DatasetGeneralInfo.id == dataset_general_info_id)
        if deep:
            query = query.options(selectinload(DatasetGeneralInfo.dataset))

        result = await self.session.execute(query)
        dataset_general_info = result.scalar_one_or_none()
        return dataset_general_info

    async def edit_description(self, id: int, dataset_name: str, new_description: str):
        stmt = (
            update(DatasetGeneralInfo)
            .where(DatasetGeneralInfo.id == id)
            .values(name=dataset_name, description=new_description)
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_all(self):
        query = select(DatasetGeneralInfo)
        result = await self.session.execute(query)
        return result.scalars().all()


class DatasetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_dataset(
            self,
            size: int,
            created_at_device: datetime,
            access_rights: str,
            host: str,
    ):
        dataset = Dataset(
            size=size,
            created_at_device=created_at_device,
            access_rights=access_rights,
            host=host,
        )
        self.session.add(dataset)
        await self.session.commit()
        return dataset

    async def get_dataset_by(self, dataset_name: str, dataset_host: str) -> Optional[Dataset]:
        query = (
            select(Dataset)
            .join(DatasetGeneralInfo, Dataset.dataset_general_info)
            .where(
                DatasetGeneralInfo.name == dataset_name,
                Dataset.host == dataset_host
            )
        )
        result = await self.session.execute(query)
        dataset = result.scalars().first()
        return dataset

    async def get_all_datasets(self) -> Sequence[Dataset]:
        result = await self.session.execute(select(Dataset))
        datasets =  result.scalars().all()
        return datasets

    async def update_dataset(
            self,
            dataset_id: int,
            size: int,
            access_rights: str,
    ):
        updated_values = {"size": size, "access_rights": access_rights}

        await self.session.execute(
            update(Dataset)
            .where(Dataset.id == dataset_id)
            .values(**updated_values)
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

    async def get_usage_events_by_dataset_id(self, dataset_id) -> Sequence[DatasetUsageHistory]:
        result = await self.session.execute(
            select(DatasetUsageHistory)
            .where(DatasetUsageHistory.dataset_id == dataset_id)
            .order_by(DatasetUsageHistory.event_time.desc())
        )
        return result.scalars().all()

    async def delete_events_older_than(self, timestamp: datetime):
        await self.session.execute(
            delete(DatasetUsageHistory).where(DatasetUsageHistory.event_time < timestamp)
        )
        await self.session.commit()

    async def add_event(self, dataset_id, client_request: DaemonClientRequest):
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
            DatasetUsageHistory.dataset_id == dataset_id
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
                        dataset_id=dataset_id,
                        event_type=EventType.READ,
                        event_time=normalized_time
                    )
                    self.session.add(new_event)
                    events.append(EventType.READ)

                elif event_type == EventType.MODIFY and latest_event.event_time != normalized_time:
                    new_event = DatasetUsageHistory(
                        dataset_id=dataset_id,
                        event_type=EventType.MODIFY,
                        event_time=normalized_time
                    )
                    self.session.add(new_event)
                    events.append(EventType.MODIFY)
            else:
                new_event = DatasetUsageHistory(
                    dataset_id=dataset_id,
                    event_type=event_type,
                    event_time=normalized_time
                )
                self.session.add(new_event)
                events.append(event_type)

        if not existing_records:
            create_event = DatasetUsageHistory(
                dataset_id=dataset_id,
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

    async def get_events_statistic_by_time(self, dataset_id, timestamp: timedelta = timedelta(days=30)):
        stmt_count = select(
            DatasetUsageHistory.event_type,
            func.count(DatasetUsageHistory.event_type).label('event_count')
        ).filter(
            DatasetUsageHistory.dataset_id == dataset_id,
            datetime.now() - DatasetUsageHistory.event_time <= timestamp
        ).group_by(DatasetUsageHistory.event_type)

        stmt_last_read = select(DatasetUsageHistory.event_time).filter(
            DatasetUsageHistory.dataset_id == dataset_id,
            DatasetUsageHistory.event_type == EventType.READ
        ).order_by(desc(DatasetUsageHistory.event_time)).limit(1)

        stmt_last_modified = select(DatasetUsageHistory.event_time).filter(
            DatasetUsageHistory.dataset_id == dataset_id,
            DatasetUsageHistory.event_type == EventType.MODIFY
        ).order_by(desc(DatasetUsageHistory.event_time)).limit(1)

        result_count = await self.session.execute(stmt_count)
        last_read_result = await self.session.execute(stmt_last_read)
        last_modified_result = await self.session.execute(stmt_last_modified)

        event_statistics = {event_type: count for event_type, count in result_count.fetchall()}
        last_read = last_read_result.scalar()
        last_modified = last_modified_result.scalar()

        frequency_of_use = sum(event_statistics.values())

        return Statistic(
            last_read=last_read,
            last_modified=last_modified,
            frequency_of_use_in_month=frequency_of_use
        )

    async def get_latest_events(self, dataset_id) -> dict:
        """
        Fetch the latest READ and MODIFY events for a given dataset.
        """
        stmt = select(
            DatasetUsageHistory.event_type,
            func.max(DatasetUsageHistory.event_time).label("latest_event_time")
        ).filter(
            DatasetUsageHistory.dataset_id == dataset_id
        ).group_by(DatasetUsageHistory.event_type)

        result = await self.session.execute(stmt)
        # Convert results into a dictionary for easier access
        latest_events = {row.event_type: row.latest_event_time for row in result.fetchall()}
        return latest_events


class LinkRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_urls(self) -> List[Link]:
        stmt = select(Link)
        result = await self.session.execute(stmt)
        links = list(result.scalars().fetchall())
        return links

    async def add_or_update_url(self, request: LinkDescriptionUpdateRequest) -> List[Link]:
        stmt = select(Link).where(Link.url == str(request.url))
        result = await self.session.execute(stmt)
        existing_link = result.scalars().first()

        if existing_link:
            existing_link.description = request.description
            existing_link.name = request.name
        else:
            self.session.add(Link(url=str(request.url), description=request.description, name=request.name))

        await self.session.commit()
        return await self.get_all_urls()

    async def delete_link(self, url: str) -> List[Link]:
        stmt = delete(Link).where(Link.url == url)
        await self.session.execute(stmt)
        await self.session.commit()
        return await self.get_all_urls()
