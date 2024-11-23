import datetime
import json

import pytest
import sqlalchemy
from fastapi import status
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import EventType
from app.main import app
from app.models import DatasetUsageHistory


@pytest.mark.asyncio(loop_scope="session")
async def test_get_statistic(client: AsyncClient, session: AsyncSession, default_user_headers: dict[str, str],) -> None:
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

    client_request = {
        "hostname": "string",
        "dataset_name": "string",
        "age": "2024-11-23T17:25:50.481Z",
        "access_rights": "public",
        "last_access_date": "2024-11-23T17:25:50.481Z",
        "last_modification_date": "2024-11-23T17:25:50.481Z"
    }

    response = await client.put(
        app.url_path_for("add_usage_event"),
        headers=default_user_headers,
        json=client_request
    )

    assert response.status_code == status.HTTP_200_OK
    #
    # response = await client.get(
    #     app.url_path_for("get_events_statistic"),
    # )
    #
    # assert response.status_code == status.HTTP_200_OK
    # stats = response.json()
    # print(f'PIDARAS - {stats}')
    # assert "READ" in stats
    # assert stats["READ"] > 0  # Убедимся, что подсчитан хотя бы 1 READ

# @pytest.mark.asyncio
# async def test_event_not_added_if_duplicate(client: AsyncClient, session: AsyncSession) -> None:
#     # Создаем событие напрямую
#     client_request = {
#         "hostname": "duplicate_host",
#         "dataset_name": "duplicate_dataset",
#         "last_access_date": "2024-11-22T12:34:56Z",
#         "last_modification_date": "2024-11-21T11:22:33Z",
#         "age": 1690195567.0,
#     }
#
#     existing_event = DatasetUsageHistory(
#         host_name=client_request["hostname"],
#         dataset_name=client_request["dataset_name"],
#         event_type="READ",
#         event_time=client_request["last_access_date"],
#     )
#     session.add(existing_event)
#     await session.commit()
#
#     # Попробуем добавить через API
#     response = await client.put(
#         app.url_path_for("add_usage_event"),
#         json=client_request,
#     )
#
#     assert response.status_code == status.HTTP_200_OK
#     assert response.json() == {"message": "Event not added"}
#
#     # Убедимся, что дубликатов не появилось
#     result = await session.execute(
#         select(DatasetUsageHistory).where(DatasetUsageHistory.dataset_name == client_request["dataset_name"])
#     )
#     events = result.scalars().all()
#     assert len(events) == 1
