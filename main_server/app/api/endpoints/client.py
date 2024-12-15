from datetime import datetime, timedelta

from fastapi import APIRouter, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_session
from app.core.repository import DatasetUsageHistoryRepository, DatasetRepository
from app.schemas.requests import DaemonClientRequest

router = APIRouter()


@router.post("/add_event", status_code=status.HTTP_200_OK, description="Add an event for dataset usage")
async def add_usage_event(
        client_request: DaemonClientRequest,
        session: AsyncSession = Depends(get_session)
):
    dataset_repo = DatasetRepository(session)
    events_repo = DatasetUsageHistoryRepository(session)

    dataset = await dataset_repo.get_dataset_by(client_request.dataset_name, client_request.hostname)

    if not dataset:
        await dataset_repo.create_dataset(
            name=client_request.dataset_name,
            size=client_request.size,
            created_at_device=client_request.age,
            access_rights=client_request.access_rights,
            host=client_request.hostname,
        )
    else:
        await dataset_repo.update_dataset(
            dataset_id=dataset.id,
            size=client_request.size,
            access_rights=client_request.access_rights,
        )

    event_added = await events_repo.add_event(client_request)
    verdict = {"message": f"Event added = {event_added}"}

    return verdict


