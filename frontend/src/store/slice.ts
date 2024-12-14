import {createSlice, PayloadAction} from "@reduxjs/toolkit";
import {LinkData} from "../types/link.ts";
import {Resource} from "../types/resource.ts";
import {deleteLink, fetchLinks, updateLink} from "./api-actions.ts";

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
  extraReducers: (builder) => {
    builder.addCase(fetchLinks.fulfilled, (state, action) => {
      state.currentLinks = action.payload;
      state.linksLoading = false;
    });
    builder.addCase(fetchLinks.pending, (state) => {
      state.linksLoading = true;
    });
    builder.addCase(updateLink.fulfilled, (state, action) => {
      state.currentLinks = action.payload;
      state.linksLoading = false;
    });
    builder.addCase(deleteLink.fulfilled, (state, action) => {
      state.currentLinks = action.payload;
      state.linksLoading = false;
    })
  }
});


export const {setErrorMessage} = ebaDatasetSlice.actions;
export default ebaDatasetSlice.reducer;
