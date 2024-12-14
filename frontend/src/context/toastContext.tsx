// src/context/ToastContext.tsx
import { Toast } from 'primereact/toast';
import React, { createContext, ReactNode, useRef } from 'react';
import { Message } from '../types/message';

interface ToastContextProps {
    show: (options: Message) => void;
}

export const ToastContext = createContext<ToastContextProps | undefined>(
    undefined
);

interface ToastProviderProps {
    children: ReactNode;
}

export const ToastProvider: React.FC<ToastProviderProps> = ({ children }) => {
    const toast = useRef<Toast>(null);

    const show = (options: Message) => {
        toast.current?.show(options);
    };

    return (
        <ToastContext.Provider value={{ show }}>
            <Toast ref={toast} />
            {children}
        </ToastContext.Provider>
    );
};
