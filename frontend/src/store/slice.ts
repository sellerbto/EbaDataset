import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { LinkData } from '../types/link.ts';
import { Resource } from '../types/resource.ts';
import {
    addDataset,
    createOrUpdateLink,
    deleteLink,
    fetchDatasets,
    fetchLinks,
    updateDatasetDescription,
} from './api-actions.ts';

interface EbaDatasetState {
    currentLinks: LinkData[];
    currentDatasets: Resource[];
    linksLoading: boolean;
    datasetsLoading: boolean;
    error: string | null;
}

const ebaDatasetInitialState: EbaDatasetState = {
    currentLinks: [],
    currentDatasets: [],
    linksLoading: false,
    datasetsLoading: false,
    error: null,
};

const ebaDatasetSlice = createSlice({
    name: 'cityAndOffers',
    initialState: ebaDatasetInitialState,
    reducers: {
        setErrorMessage: (state, action: PayloadAction<string | null>) => {
            state.error = action.payload;
        },
    },
    extraReducers: builder => {
        builder.addCase(fetchLinks.fulfilled, (state, action) => {
            state.currentLinks = action.payload;
            state.linksLoading = false;
        });
        builder.addCase(fetchLinks.pending, state => {
            state.linksLoading = true;
        });
        builder.addCase(createOrUpdateLink.fulfilled, (state, action) => {
            state.currentLinks = action.payload;
            state.linksLoading = false;
        });
        builder.addCase(fetchLinks.rejected, (state, action) => {
            state.linksLoading = false;
            state.error = action.error.message ?? 'Ошибка при загрузке ссылок';
        });
        builder.addCase(deleteLink.fulfilled, (state, action) => {
            state.currentLinks = action.payload;
            state.linksLoading = false;
        });
        builder.addCase(deleteLink.pending, state => {
            state.linksLoading = true;
        });
        builder.addCase(createOrUpdateLink.pending, state => {
            state.linksLoading = true;
        });
        builder.addCase(deleteLink.rejected, (state, action) => {
            state.linksLoading = false;
            state.error = action.error.message ?? 'Ошибка при удалении ссылки';
        });
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
            })

            .addCase(addDataset.pending, state => {
                state.datasetsLoading = true;
            })
            .addCase(addDataset.fulfilled, state => {
                state.datasetsLoading = false;
            })
            .addCase(addDataset.rejected, (state, action) => {
                state.datasetsLoading = false;
                state.error =
                    action.error.message ?? 'Ошибка при добавлении датасета';
            })

            .addCase(updateDatasetDescription.pending, state => {
                state.datasetsLoading = true;
            })
            .addCase(updateDatasetDescription.fulfilled, state => {
                state.datasetsLoading = false;
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
