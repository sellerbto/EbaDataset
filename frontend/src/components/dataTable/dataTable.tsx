import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { confirmDialog } from 'primereact/confirmdialog';
import { DataTable } from 'primereact/datatable';
import { Dialog } from 'primereact/dialog';
import {
    InputNumber,
    InputNumberValueChangeEvent,
} from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { ProgressSpinner } from 'primereact/progressspinner';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import React, { useContext, useEffect, useState } from 'react';
import { ToastContext } from '../../context/toastContext';

// Импортируем хук useAppDispatch/useAppSelector (или ваши аналоги) и нужные экшены
import { useAppDispatch, useAppSelector } from '../../store';
import {
    addDataset,
    fetchDatasets,
    updateDatasetDescription,
} from '../../store/api-actions';

// Интерфейс Resource для фронта (ваш тип)
export interface Resource {
    id: string;
    name: string;
    description: string;
    access_rights: 'read' | 'write' | 'admin' | 'unknown';
    size: number;
    host: string;
    frequency_of_use_in_month: number;
    created_at_server: string;
    created_at_host: string;
    last_read: string;
    last_modified: string;
}

const MainDataTable: React.FC = () => {
    const toastContext = useContext(ToastContext);
    const dispatch = useAppDispatch();

    // Достаём данные и флаг загрузки из Redux store
    const data = useAppSelector(state => state.currentDatasets);
    const loading = useAppSelector(state => state.datasetsLoading);

    // Локальные стейты для окна "Добавить ресурс"
    const [dialogVisible, setDialogVisible] = useState(false);
    const [tempName, setTempName] = useState('');
    const [tempDescription, setTempDescription] = useState('');

    // При первом рендере запрашиваем список датасетов с бэкенда
    useEffect(() => {
        dispatch(fetchDatasets())
            .unwrap()
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось загрузить ресурсы.',
                    life: 3000,
                });
            });
    }, [dispatch, toastContext]);

    const openAddResourceDialog = () => {
        setTempName('');
        setTempDescription('');
        setDialogVisible(true);
    };

    const closeAddResourceDialog = () => {
        setDialogVisible(false);
    };

    /**
     * Создать новый "датасет" (по сути - ресурс)
     * На бэкенде (PUT /dashboard/datasets) требуется { name, description }.
     * После успеха, желательно перечитать список датасетов (fetchDatasets).
     */
    const handleAddResource = async () => {
        if (!tempName.trim()) {
            alert('Поле "Название" обязательно для заполнения');
            return;
        }

        dispatch(addDataset({ name: tempName, description: tempDescription }))
            .unwrap()
            .then(() => {
                closeAddResourceDialog();
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Датасет успешно добавлен.',
                    life: 3000,
                });
                // Обновить список после добавления
                dispatch(fetchDatasets());
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось добавить датасет.',
                    life: 3000,
                });
            });
    };

    /**
     * Пример обработки изменения ячейки (редактирование name/description).
     * Для остальных полей на бэкенде нет эндпоинта, так что либо отключите их редактирование,
     * либо сделайте отдельный запрос (например, PATCH) на ваш бекенд.
     */
    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        // Валидируем на пустые строки
        if (typeof newValue === 'string' && newValue.trim().length === 0) {
            event.preventDefault();
            toastContext?.show({
                severity: 'warn',
                summary: 'Предупреждение',
                detail: `Поле "${field}" не может быть пустым.`,
                life: 3000,
            });
            return;
        }

        // Если пытаемся редактировать "size" или "host",
        // но на бэкенде нет метода их обновления, это просто не сработает.
        // Покажем предупреждение:
        if (field !== 'name' && field !== 'description') {
            event.preventDefault();
            toastContext?.show({
                severity: 'warn',
                summary: 'Предупреждение',
                detail: 'Редактирование этого поля пока не поддерживается.',
                life: 3000,
            });
            return;
        }

        // Для name / description вызываем updateDatasetDescription
        const updatedRow = { ...rowData, [field]: newValue };

        dispatch(
            updateDatasetDescription({
                // id на бэкенде — число, а у нас string. Нужно конвертировать:
                id: updatedRow.id,
                name: updatedRow.name,
                description: updatedRow.description,
            })
        )
            .unwrap()
            .then(() => {
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Датасет успешно обновлён (описание).',
                    life: 3000,
                });
                // После успеха перезагрузить список:
                dispatch(fetchDatasets());
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось обновить датасет.',
                    life: 3000,
                });
            });
    };

    /**
     * Если вам нужен функционал удаления (и есть подходящий эндпоинт на бэкенде),
     * вы можете добавить экшен (например, deleteDataset) и здесь его использовать.
     * Для демонстрации используем confirmDialog — но пока оставим как заглушку.
     */
    const confirmDelete = (rowData: Resource) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ресурс "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                // Если появится эндпоинт, делайте dispatch(deleteDataset(rowData.id)) и refetch
                toastContext?.show({
                    severity: 'info',
                    summary: 'Уведомление',
                    detail: 'Функционал удаления не реализован.',
                    life: 3000,
                });
            },
        });
    };

    /**
     * Редакторы: textEditor и numberEditor.
     * Но если реального обновления на бэкенде нет — редактирование будет чисто «визуальным».
     */
    const textEditor = (options: ColumnEditorOptions) => (
        <InputText
            type='text'
            value={options.value}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                options.editorCallback?.(e.target.value)
            }
            onKeyDown={e => e.stopPropagation()}
        />
    );

    const numberEditor = (options: ColumnEditorOptions) => (
        <InputNumber
            value={options.value}
            onValueChange={(e: InputNumberValueChangeEvent) =>
                options.editorCallback?.(e.value)
            }
            onKeyDown={e => e.stopPropagation()}
            mode='decimal'
            min={0}
        />
    );

    const cellEditor = (options: ColumnEditorOptions) => {
        if (
            options.field === 'size' ||
            options.field === 'frequency_of_use_in_month'
        ) {
            return numberEditor(options);
        } else {
            return textEditor(options);
        }
    };

    /**
     * Простой форматтер дат (string -> Local String),
     * чтобы не отображать "undefined" или "null".
     */
    const formatDate = (dateString: string) => {
        if (!dateString) return '';
        return new Date(dateString).toLocaleString();
    };

    const deleteBodyTemplate = (rowData: Resource) => (
        <Button
            icon='pi pi-trash'
            className='p-button-danger p-button-sm'
            onClick={e => {
                e.stopPropagation();
                confirmDelete(rowData);
            }}
            tooltip='Удалить'
            tooltipOptions={{ position: 'top' }}
        />
    );

    return (
        <div className='table-container'>
            {loading ? (
                <div
                    className='loading-container'
                    style={{ textAlign: 'center', padding: '2rem' }}
                >
                    <ProgressSpinner />
                </div>
            ) : (
                <DataTable
                    value={data}
                    sortMode='multiple'
                    paginator
                    rows={10}
                    tableStyle={{ minWidth: '60rem' }}
                    editMode='cell'
                >
                    <Column
                        field='name'
                        header='Название'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '15%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='access_rights'
                        header='Права доступа'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '5%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='size'
                        header='Размер'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '5%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='host'
                        header='Хост'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '5%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='frequency_of_use_in_month'
                        header='Частота использования (мес)'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='description'
                        header='Описание'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='created_at_server'
                        header='Дата создания на сервере'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.created_at_server)
                        }
                    />
                    <Column
                        field='created_at_host'
                        header='Дата создания на хосте'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.created_at_host)
                        }
                    />
                    <Column
                        field='last_read'
                        header='Последнее чтение'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.last_read)
                        }
                    />
                    <Column
                        field='last_modified'
                        header='Последнее изменение'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.last_modified)
                        }
                    />
                    <Column
                        header='Удалить'
                        body={deleteBodyTemplate}
                        style={{ width: '5%', textAlign: 'center' }}
                    />
                </DataTable>
            )}
            <div className='table-toolbar'>
                <Button
                    icon='pi pi-plus'
                    label='Добавить ресурс'
                    className='p-button-success p-button-block'
                    onClick={openAddResourceDialog}
                />
            </div>
            <Dialog
                header='Добавить новый датасет'
                visible={dialogVisible}
                onHide={closeAddResourceDialog}
                style={{ width: '50vw' }}
                footer={
                    <div>
                        <Button
                            label='Отмена'
                            icon='pi pi-times'
                            onClick={closeAddResourceDialog}
                            className='p-button-text'
                        />
                        <Button
                            label='Добавить'
                            icon='pi pi-check'
                            onClick={handleAddResource}
                            className='p-button-text'
                        />
                    </div>
                }
            >
                <div className='p-fluid'>
                    <div className='p-field'>
                        <label htmlFor='name'>Название</label>
                        <InputText
                            id='name'
                            value={tempName}
                            onChange={e => setTempName(e.target.value)}
                            autoFocus
                        />
                    </div>

                    <div className='p-field'>
                        <label htmlFor='description'>Описание</label>
                        <InputText
                            id='description'
                            value={tempDescription}
                            onChange={e => setTempDescription(e.target.value)}
                        />
                    </div>
                </div>
            </Dialog>
        </div>
    );
};

export default MainDataTable;
