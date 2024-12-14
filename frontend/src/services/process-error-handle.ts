import {store} from '../store';
import {clearErrorAction} from '../store/api-actions';
import {setErrorMessage} from '../store/slice.ts';

export const processErrorHandle = (message: string): void => {
  store.dispatch(setErrorMessage(message));
  store.dispatch(clearErrorAction());
};
