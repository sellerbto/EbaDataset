import { createAsyncThunk } from '@reduxjs/toolkit';
import { AxiosInstance } from 'axios';
import { TIMEOUT_SHOW_ERROR } from '../const.ts';
import { ApiRoute } from '../enums/apiRoute.ts';
import { LinkData } from '../types/link.ts';
import { Resource } from '../types/resource.ts';
import { AppDispatch } from '../types/state.ts';
import { setErrorMessage } from './slice.ts';

export const fetchLinks = createAsyncThunk<
    LinkData[],
    undefined,
    {
        extra: AxiosInstance;
    }
>('fetchLinks', async (_, { extra: api }) => {
    const { data } = await api.get<LinkData[]>(ApiRoute.Links);
    return data;
});

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

export const deleteLink = createAsyncThunk<
    LinkData[],
    string,
    {
        extra: AxiosInstance;
    }
>('deleteLink', async (link_url, { extra: api }) => {
    const { data } = await api.delete<LinkData[]>(ApiRoute.Links, {
        params: { link_url: link_url },
    });
    return data;
});

export const fetchDatasets = createAsyncThunk<
    Resource[],
    undefined,
    {
        extra: AxiosInstance;
    }
>('fetchDatasets', async (_, { extra: api }) => {
    const { data } = await api.get<Resource[]>(ApiRoute.Datasets);
    return data;
});

//попытался написать
export const addDataset = createAsyncThunk<
    void,
    { name: string; description: string },
    {
        extra: AxiosInstance;
    }
>('addDataset', async ({ name, description }, { extra: api }) => {
    await api.post(ApiRoute.Datasets, { name, description });
});

export const updateDatasetDescription = createAsyncThunk<
    void,
    { id: string; name: string; description: string },
    {
        extra: AxiosInstance;
    }
>(
    'updateDatasetDescription',
    async ({ id, name, description }, { extra: api }) => {
        await api.post(ApiRoute.Datasets, { id, name, description });
    }
);

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
