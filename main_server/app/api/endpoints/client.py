from datetime import datetime

from fastapi import APIRouter, status
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.api.deps import get_session
from app.core.repository import DatasetUsageHistoryRepository, DatasetRepository
from app.models import DatasetGeneralInfo, Dataset
from app.schemas.requests import DaemonClientRequest

router = APIRouter()


@router.post("/add_event", status_code=status.HTTP_200_OK, description="Add an event for dataset usage")
async def add_usage_event(
        client_request: DaemonClientRequest,
        session: AsyncSession = Depends(get_session)
):
    dataset_repo = DatasetRepository(session)
    events_repo = DatasetUsageHistoryRepository(session)

    dataset_query = select(Dataset).filter(Dataset.file_path == client_request.file_path)
    result = await session.execute(dataset_query)
    dataset = result.scalar_one_or_none()

    if not dataset:
        print('Add dataset general info')
        dataset_general_info = DatasetGeneralInfo(
            name=client_request.dataset_name,
            description="Default description"
        )

        dataset = Dataset(
            name=client_request.dataset_name,
            file_path=client_request.file_path,
            access_rights=client_request.access_rights,
            size=client_request.size,
            host=client_request.hostname,
            created_at_device=client_request.age,
            created_at_server=datetime.utcnow(),
            dataset_general_info=dataset_general_info
        )

        session.add(dataset)
        await session.commit()
        await session.refresh(dataset)

    dataset.last_access_date = client_request.last_access_date
    dataset.last_modification_date = client_request.last_modification_date
    dataset.size = client_request.size

    await session.commit()

    event_added = await events_repo.add_event(client_request)
    verdict = {"message": f"Event added = {event_added}"}
    print(verdict)
    return verdict


