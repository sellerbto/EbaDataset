import {configureStore} from '@reduxjs/toolkit';
import slice from './slice.ts';
import {TypedUseSelectorHook, useDispatch, useSelector} from 'react-redux';
import {AppDispatch, State} from '../types/state.ts';
import {createAPI} from '../services/api.ts';

export const api = createAPI();

export const store = configureStore({
  reducer: slice,
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      thunk: {
        extraArgument: api,
      },
    }),
});

export const useAppDispatch = () => useDispatch<AppDispatch>();

export const useAppSelector: TypedUseSelectorHook<State> = useSelector;
