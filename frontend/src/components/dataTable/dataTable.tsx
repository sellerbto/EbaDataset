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
import { useContext, useState } from 'react';
import { ToastContext } from '../../context/toastContext';
// import { ProductService } from '../../services/productService';
import { Resource } from '../../types/resource';
import './dataTable.scss';

const MainDataTable: React.FC = () => {
    const toastContext = useContext(ToastContext);

    const [data, setData] = useState<Resource[]>([
        {
            id: '1',
            name: 'Сервер1',
            access_rights: 'read',
            size: 500,
            host: 'host1',
            frequency_of_use_in_month: 10,
            created_at_server: '2023-01-01T10:00:00Z',
            created_at_host: '2023-01-02T10:00:00Z',
            last_read: '2023-01-05T10:00:00Z',
            last_modified: '2023-01-06T10:00:00Z',
        },
        {
            id: '2',
            name: 'Сервер2',
            access_rights: 'write',
            size: 1024,
            host: 'host2',
            frequency_of_use_in_month: 5,
            created_at_server: '2023-02-01T09:00:00Z',
            created_at_host: '2023-02-02T09:00:00Z',
            last_read: '2023-02-10T09:00:00Z',
            last_modified: '2023-02-11T09:00:00Z',
        },
        {
            id: '3',
            name: 'Сервер3',
            access_rights: 'admin',
            size: 250,
            host: 'host3',
            frequency_of_use_in_month: 20,
            created_at_server: '2023-03-01T08:30:00Z',
            created_at_host: '2023-03-02T08:30:00Z',
            last_read: '2023-03-10T08:30:00Z',
            last_modified: '2023-03-11T08:30:00Z',
        },
    ]);

    const [loading, setLoading] = useState<boolean>(false);

    /*
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
    */

    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        if (
            (field === 'size' || field === 'frequency_of_use_in_month') &&
            (typeof newValue !== 'number' || newValue < 0)
        ) {
            event.preventDefault();
            toastContext?.show({
                severity: 'warn',
                summary: 'Предупреждение',
                detail:
                    field === 'size'
                        ? 'Размер должен быть положительным числом.'
                        : 'Частота использования должна быть положительным числом.',
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

        const updatedRow: Resource = { ...rowData, [field]: newValue };

        setData(prevData =>
            prevData.map(item =>
                item.id === updatedRow.id ? updatedRow : item
            )
        );

        /*
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
            });
        */

        toastContext?.show({
            severity: 'success',
            summary: 'Успех',
            detail: 'Ресурс успешно обновлен (тестовые данные).',
            life: 3000,
        });
    };

    const confirmDelete = (rowData: Resource) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ресурс "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                // Удаляем локально
                setData(prevData =>
                    prevData.filter(item => item.id !== rowData.id)
                );

                /*
                ProductService.deleteServer(rowData.id)
                    .then(() => {
                        setData(prevData => prevData.filter(item => item.id !== rowData.id));
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
                */

                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Ресурс успешно удален (тестовые данные).',
                    life: 3000,
                });
            },
            reject: () => {
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
        } else if (options.field === 'access_rights') {
            return (
                <InputText
                    type='text'
                    value={options.value}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                        options.editorCallback?.(e.target.value)
                    }
                    onKeyDown={e => e.stopPropagation()}
                />
            );
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
        </div>
    );
};

export default MainDataTable;
