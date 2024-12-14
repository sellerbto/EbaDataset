import {createAsyncThunk} from '@reduxjs/toolkit';
import {AxiosInstance} from 'axios';
import {ApiRoute} from '../enums/apiRoute.ts';
import {LinkData} from "../types/link.ts";
import {AppDispatch} from "../types/state.ts";
import {TIMEOUT_SHOW_ERROR} from "../const.ts";


export const fetchLinks = createAsyncThunk<LinkData[], undefined, {
  extra: AxiosInstance;
}>(
  'fetchLinks',
  async (_, {extra: api}) => {
    const {data} = await api.get<LinkData[]>(ApiRoute.Links);
    return data;
  },
);

export const clearErrorAction = createAsyncThunk<void, undefined, {
  dispatch: AppDispatch;
}>(
  'clearError',
  async (_arg, {dispatch}) => {
    await new Promise((_) => setTimeout(_, TIMEOUT_SHOW_ERROR)).then(() => dispatch(setErrorMessage(null)));
  },
);

