import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { DatasetsSummary } from '../types/datasetTypes.ts';
import { LinkData } from '../types/link.ts';
import {
    addDataset,
    createOrUpdateLink,
    deleteLink,
    fetchDatasets,
    fetchLinks,
    updateDatasetDescription,
} from './api-actions.ts';

/** Описываем состояние нашего slice. */
interface EbaDatasetState {
    /** Список ссылок (LinkData[]), которые пришли с бэка ( /links ). */
    currentLinks: LinkData[];
    /** Список «датасетов» (Resource[]), которые мы используем на фронте. */
    currentDatasets: DatasetsSummary[];
    /** Флаги загрузки (true, когда идёт запрос). */
    linksLoading: boolean;
    datasetsLoading: boolean;
    /** Текст ошибки (если произошла) или null. */
    error: string | null;
}

/** Начальное состояние. */
const ebaDatasetInitialState: EbaDatasetState = {
    currentLinks: [],
    currentDatasets: [],
    linksLoading: false,
    datasetsLoading: false,
    error: null,
};

const ebaDatasetSlice = createSlice({
    name: 'ebaDataset',
    initialState: ebaDatasetInitialState,
    reducers: {
        /** Позволяем вручную выставлять ошибку (например, для очистки через clearErrorAction). */
        setErrorMessage: (state, action: PayloadAction<string | null>) => {
            state.error = action.payload;
        },
    },
    extraReducers: builder => {
        // --------- LINKS -----------
        // fetchLinks
        builder
            .addCase(fetchLinks.pending, state => {
                state.linksLoading = true;
            })
            .addCase(fetchLinks.fulfilled, (state, action) => {
                state.linksLoading = false;
                state.currentLinks = action.payload;
            })
            .addCase(fetchLinks.rejected, (state, action) => {
                state.linksLoading = false;
                state.error =
                    action.error.message ?? 'Ошибка при загрузке списка ссылок';
            });

        // createOrUpdateLink
        builder
            .addCase(createOrUpdateLink.pending, state => {
                state.linksLoading = true;
            })
            .addCase(createOrUpdateLink.fulfilled, (state, action) => {
                state.linksLoading = false;
                state.currentLinks = action.payload;
            })
            .addCase(createOrUpdateLink.rejected, (state, action) => {
                state.linksLoading = false;
                state.error =
                    action.error.message ??
                    'Ошибка при создании/изменении ссылки';
            });

        // deleteLink
        builder
            .addCase(deleteLink.pending, state => {
                state.linksLoading = true;
            })
            .addCase(deleteLink.fulfilled, (state, action) => {
                state.linksLoading = false;
                state.currentLinks = action.payload;
            })
            .addCase(deleteLink.rejected, (state, action) => {
                state.linksLoading = false;
                state.error =
                    action.error.message ?? 'Ошибка при удалении ссылки';
            });

        // --------- DATASETS -----------
        // fetchDatasets
        builder
            .addCase(fetchDatasets.pending, state => {
                state.datasetsLoading = true;
            })
            .addCase(fetchDatasets.fulfilled, (state, action) => {
                state.datasetsLoading = false;
                state.currentDatasets = action.payload;
            })
            .addCase(fetchDatasets.rejected, (state, action) => {
                state.datasetsLoading = false;
                state.error =
                    action.error.message ??
                    'Ошибка при загрузке списка датасетов';
            });

        // addDataset
        builder
            .addCase(addDataset.pending, state => {
                state.datasetsLoading = true;
            })
            .addCase(addDataset.fulfilled, state => {
                state.datasetsLoading = false;
                // можно сделать refetchDatasets, если нужно обновить список
            })
            .addCase(addDataset.rejected, (state, action) => {
                state.datasetsLoading = false;
                state.error =
                    action.error.message ?? 'Ошибка при добавлении датасета';
            });

        // updateDatasetDescription
        builder
            .addCase(updateDatasetDescription.pending, state => {
                state.datasetsLoading = true;
            })
            .addCase(updateDatasetDescription.fulfilled, state => {
                state.datasetsLoading = false;
                // тоже можно сделать refetchDatasets, если нужно обновить описание
            })
            .addCase(updateDatasetDescription.rejected, (state, action) => {
                state.datasetsLoading = false;
                state.error =
                    action.error.message ??
                    'Ошибка при обновлении описания датасета';
            });
    },
});

export const { setErrorMessage } = ebaDatasetSlice.actions;
export default ebaDatasetSlice.reducer;
