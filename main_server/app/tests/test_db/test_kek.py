import datetime

import pytest
import sqlalchemy
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from app.models import EventType
from app.main import app
from app.models import DatasetUsageHistory

@pytest.mark.asyncio
async def test_get_statistic(session: AsyncSession) -> None:
    dataset_name = "test_dataset"
    host_name = "test_host"

    new_event = DatasetUsageHistory(
        id=15,
        host_name=host_name,
        dataset_name=dataset_name,
        event_type=EventType.READ,
        event_time=datetime.datetime.now(),
    )
    session.add(new_event)
    await session.commit()

    result = await session.execute(sqlalchemy.select(DatasetUsageHistory).filter_by(id=15))
    retrieved_event = result.scalar_one_or_none()
    assert retrieved_event is not None
    assert retrieved_event.dataset_name == dataset_name
    assert retrieved_event.host_name == host_name
