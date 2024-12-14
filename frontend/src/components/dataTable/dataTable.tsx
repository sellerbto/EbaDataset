// src/components/dataTable/MainDataTable.tsx
import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { confirmDialog } from 'primereact/confirmdialog';
import { DataTable } from 'primereact/datatable';
import {
    InputNumber,
    InputNumberValueChangeEvent,
} from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { ProgressSpinner } from 'primereact/progressspinner';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { useContext, useEffect, useState } from 'react';
import { ToastContext } from '../../context/toastContext';
import { ProductService } from '../../services/productService';
import { Resource } from '../../types/resource';
import './dataTable.scss';

const MainDataTable: React.FC = () => {
    const [data, setData] = useState<Resource[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const toastContext = useContext(ToastContext);

    useEffect(() => {
        ProductService.getServers()
            .then((fetchedData: Resource[]) => {
                setData(fetchedData);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось загрузить ресурсы.',
                    life: 3000,
                });
            });
    }, [toastContext]);

    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        // Валидация введённых данных
        if (
            (field === 'size' || field === 'frequency_of_use_in_month') &&
            (typeof newValue !== 'number' || newValue < 0)
        ) {
            event.preventDefault();
            toastContext?.show({
                severity: 'warn',
                summary: 'Предупреждение',
                detail: `${
                    field === 'size' ? 'Размер' : 'Частота использования'
                } должно быть положительным числом.`,
                life: 3000,
            });
            return;
        } else if (
            typeof newValue === 'string' &&
            newValue.trim().length === 0
        ) {
            event.preventDefault();
            toastContext?.show({
                severity: 'warn',
                summary: 'Предупреждение',
                detail: `Поле "${field}" не может быть пустым.`,
                life: 3000,
            });
            return;
        }

        // Создание обновлённого объекта
        const updatedRow: Resource = { ...rowData, [field]: newValue };

        // Отправка обновления на сервер
        ProductService.updateServer(updatedRow)
            .then((updatedServer: Resource) => {
                setData(prevData =>
                    prevData.map(item =>
                        item.id === updatedServer.id ? updatedServer : item
                    )
                );
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Ресурс успешно обновлен.',
                    life: 3000,
                });
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось обновить ресурс.',
                    life: 3000,
                });
                setData(prevData => [...prevData]); // Можно восстановить предыдущее состояние, если требуется
            });
    };

    const confirmDelete = (rowData: Resource) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ресурс "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                ProductService.deleteServer(rowData.id)
                    .then(() => {
                        setData(prevData =>
                            prevData.filter(item => item.id !== rowData.id)
                        );
                        toastContext?.show({
                            severity: 'success',
                            summary: 'Успех',
                            detail: 'Ресурс успешно удален.',
                            life: 3000,
                        });
                    })
                    .catch(() => {
                        toastContext?.show({
                            severity: 'error',
                            summary: 'Ошибка',
                            detail: 'Не удалось удалить ресурс.',
                            life: 3000,
                        });
                    });
            },
            reject: () => {
                // Опционально: действия при отклонении
                toastContext?.show({
                    severity: 'info',
                    summary: 'Отменено',
                    detail: 'Удаление ресурса отменено.',
                    life: 3000,
                });
            },
        });
    };

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

    const formatDate = (dateString: string) => {
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
                        header='Name'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '15%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='access_rights'
                        header='Access Rights'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '15%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='size'
                        header='Size'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='host'
                        header='Host'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '15%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='frequency_of_use_in_month'
                        header='Freq. of Use/Month'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        editor={options => cellEditor(options)}
                        onCellEditComplete={onCellEditComplete}
                    />
                    <Column
                        field='created_at_server'
                        header='Created at Server'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.created_at_server)
                        }
                    />
                    <Column
                        field='created_at_host'
                        header='Created at Host'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.created_at_host)
                        }
                    />
                    <Column
                        field='last_read'
                        header='Last Read'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.last_read)
                        }
                    />
                    <Column
                        field='last_modified'
                        header='Last Modified'
                        sortable
                        headerClassName='centered-header'
                        style={{ width: '10%' }}
                        body={(rowData: Resource) =>
                            formatDate(rowData.last_modified)
                        }
                    />
                    <Column
                        header='Delete'
                        body={deleteBodyTemplate}
                        style={{ width: '5%', textAlign: 'center' }}
                    />
                </DataTable>
            )}
        </div>
    );
};

export default MainDataTable;
