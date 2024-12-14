import datetime
from typing import Dict

from fastapi import APIRouter, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.repository import DatasetUsageHistoryRepository
from app.schemas.requests import ClientRequest

router = APIRouter()


@router.put("/add_event", status_code=status.HTTP_200_OK, description="Add an event for dataset usage")
async def add_usage_event(
    client_request: ClientRequest,
    session: AsyncSession = Depends(get_session)
):
    repository = DatasetUsageHistoryRepository(session)
    event_added = await repository.add_event(client_request)
    verdict = {"message": f"Event added = {event_added}"}

    print(verdict)
    return verdict

@router.post("/get_statistic", status_code=status.HTTP_200_OK, response_model=Dict[str, int])
async def get_events_statistic(
    client_request: ClientRequest,
    session: AsyncSession = Depends(get_session)
):
    repository = DatasetUsageHistoryRepository(session)
    return await repository.get_events_statistic_by_time(client_request.hostname, client_request.dataset_name, datetime.timedelta(seconds=2592000))
