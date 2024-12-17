from typing import List

from fastapi import APIRouter, Depends, status
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps
from app.core.db_utils import get_dataset_infos
from app.core.repository import LinkRepository, \
    DatasetGeneralInfoRepository
from app.models import Link
from app.schemas.requests import LinkDescriptionUpdateRequest, DatasetInfoUpdateRequest
from app.schemas.responses import LinkResponse, DatasetsSummary

router = APIRouter()


@router.get("/datasets", response_model=DatasetsSummary, description="Get list of dataset infos")
async def get_datasets_info(
    session: AsyncSession = Depends(deps.get_session)
) -> DatasetsSummary:
    return await get_dataset_infos(session)

@router.post("/datasets", response_model=DatasetsSummary, description="Edits dataset description")
async def edit_dataset_description(
    request: DatasetInfoUpdateRequest,
    session: AsyncSession = Depends(deps.get_session)
) -> DatasetsSummary:
    repository = DatasetGeneralInfoRepository(session)
    await repository.edit_description(request.name, request.description)
    return await get_dataset_infos(session)

@router.post("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def add_or_update_link(
    request: LinkDescriptionUpdateRequest,
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)
    return await repository.add_or_update_url(request)


@router.get("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def get_all_links(
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)

    return await repository.get_all_urls()

@router.delete("/links", status_code=status.HTTP_200_OK, response_model=List[LinkResponse])
async def delete_link(
    link_url: HttpUrl,
    session: AsyncSession = Depends(deps.get_session)
) -> List[Link]:
    repository = LinkRepository(session)

    return await repository.delete_link(str(link_url))
