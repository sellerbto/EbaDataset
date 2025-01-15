import { createAsyncThunk } from '@reduxjs/toolkit';
import { AxiosInstance } from 'axios';
import { TIMEOUT_SHOW_ERROR } from '../const.ts';
import { ApiRoute } from '../enums/apiRoute.ts';
import { LinkData } from '../types/link.ts';
import { AppDispatch } from '../types/state.ts';
import { setErrorMessage } from './slice.ts';
// Импортируем наши новые (или обновлённые) интерфейсы
import { DatasetsSummary } from '../types/datasetTypes.ts';

// ---------------- LINKS ACTIONS ----------------

/**
 * Получить все ссылки (GET /links).
 */
export const fetchLinks = createAsyncThunk<
    LinkData[],
    undefined,
    {
        extra: AxiosInstance;
    }
>('fetchLinks', async (_, { extra: api }) => {
    // Бэкенд возвращает List[LinkResponse].
    // На фронте у вас LinkData и LinkResponse примерно совпадают?
    const { data } = await api.get<LinkData[]>(ApiRoute.Links);
    return data;
});

/**
 * Создать или обновить ссылку (POST /links).
 */
export const createOrUpdateLink = createAsyncThunk<
    LinkData[],
    LinkData,
    {
        extra: AxiosInstance;
    }
>('createOrUpdateLink', async (linkData, { extra: api }) => {
    const { data } = await api.post<LinkData[]>(ApiRoute.Links, linkData);
    return data;
});

/**
 * Удалить ссылку (DELETE /links).
 */
export const deleteLink = createAsyncThunk<
    LinkData[],
    string,
    {
        extra: AxiosInstance;
    }
>('deleteLink', async (link_url, { extra: api }) => {
    // Параметры передаются в query ?link_url=...
    const { data } = await api.delete<LinkData[]>(ApiRoute.Links, {
        params: { link_url: link_url },
    });
    return data;
});

// ---------------- DATASETS ACTIONS ----------------

/**
 * Получить список всех датасетов (GET /datasets).
 * Возвращается массив DatasetsSummary (List[DatasetsSummary]).
 */
export const fetchDatasets = createAsyncThunk<
    DatasetsSummary[],
    undefined,
    { extra: AxiosInstance }
>('fetchDatasets', async (_, { extra: api }) => {
    // Бэкенд возвращает List[DatasetsSummary].
    const { data } = await api.get<DatasetsSummary[]>(ApiRoute.Datasets);
    // data уже массив DatasetsSummary. Его и вернём в Redux.
    return data;
});

/**
 * Добавить новый датасет (PUT /datasets).
 * Возвращается DatasetsSummary (по Swagger response_model=DatasetsSummary).
 */
export const addDataset = createAsyncThunk<
    DatasetsSummary, // результат, который сохранится в store (при желании можно `void`, если не нужно)
    { name: string; description: string }, // входные параметры
    { extra: AxiosInstance }
>('addDataset', async ({ name, description }, { extra: api }) => {
    // server expects { name: string; description: string }
    const { data } = await api.put<DatasetsSummary>(ApiRoute.Datasets, {
        name,
        description,
    });
    return data;
});

/**
 * Обновить описание датасета (POST /datasets).
 * Возвращает { "message": "Dataset description updated successfully" }
 */
interface EditDatasetDescriptionResponse {
    message: string;
}

export const updateDatasetDescription = createAsyncThunk<
    EditDatasetDescriptionResponse,
    { id: number; name: string; description: string }, // здесь id - number (по Swagger)
    { extra: AxiosInstance }
>(
    'updateDatasetDescription',
    async ({ id, name, description }, { extra: api }) => {
        const { data } = await api.post<EditDatasetDescriptionResponse>(
            ApiRoute.Datasets,
            { id, name, description }
        );
        return data;
    }
);

/**
 * Очистить ошибку по таймеру
 */
export const clearErrorAction = createAsyncThunk<
    void,
    undefined,
    {
        dispatch: AppDispatch;
    }
>('clearError', async (_arg, { dispatch }) => {
    await new Promise(_ => setTimeout(_, TIMEOUT_SHOW_ERROR)).then(() =>
        dispatch(setErrorMessage(null))
    );
});
