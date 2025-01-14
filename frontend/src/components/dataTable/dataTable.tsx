import { nanoid } from 'nanoid'; // импортируем nanoid
import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { confirmDialog } from 'primereact/confirmdialog';
import { DataTable } from 'primereact/datatable';
import { Dialog } from 'primereact/dialog';
import { Dropdown } from 'primereact/dropdown';
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
    const toastContext = useContext(ToastContext);

    const [data, setData] = useState<Resource[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [dialogVisible, setDialogVisible] = useState(false);
    const [newResource, setNewResource] = useState<Resource>({
        id: nanoid(),
        name: '',
        access_rights: 'unknown',
        size: 0,
        host: '',
        frequency_of_use_in_month: 0,
        created_at_server: '',
        created_at_host: '',
        last_read: '',
        last_modified: '',
    });

    const accessRightsOptions = [
        { label: 'Read', value: 'read' },
        { label: 'Write', value: 'write' },
        { label: 'Admin', value: 'admin' },
        { label: 'Unknown', value: 'unknown' },
    ];

    const openAddResourceDialog = () => {
        setDialogVisible(true);
    };

    const closeAddResourceDialog = () => {
        setDialogVisible(false);
        setNewResource({
            id: '',
            name: '',
            access_rights: 'unknown',
            size: 0,
            host: '',
            frequency_of_use_in_month: 0,
            created_at_server: '',
            created_at_host: '',
            last_read: '',
            last_modified: '',
        });
    };

    const handleAddResource = async () => {
        if (
            !newResource.name ||
            !newResource.access_rights ||
            !newResource.host
        ) {
            alert('Все поля должны быть заполнены');
            return;
        }

        if (
            newResource.size <= 0 ||
            newResource.frequency_of_use_in_month <= 0
        ) {
            alert(
                'Размер и частота использования должны быть положительными числами.'
            );
            return;
        }

        ProductService.createServer(newResource)
            .then(addedResource => {
                setData(prevData => [...prevData, addedResource]);
                closeAddResourceDialog();
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Ресурс успешно добавлен.',
                    life: 3000,
                });
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось добавить ресурс.',
                    life: 3000,
                });
            });
    };

    useEffect(() => {
        setLoading(true);
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
            <div className='table-toolbar'>
                <Button
                    icon='pi pi-plus'
                    label='Добавить ресурс'
                    className='p-button-success p-button-block'
                    onClick={openAddResourceDialog}
                />
            </div>
            <Dialog
                header='Добавить новый ресурс'
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
                            value={newResource.name}
                            onChange={e =>
                                setNewResource({
                                    ...newResource,
                                    name: e.target.value,
                                })
                            }
                            autoFocus
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='access_rights'>Права доступа</label>
                        <Dropdown
                            id='access_rights'
                            value={newResource.access_rights}
                            options={accessRightsOptions}
                            onChange={e =>
                                setNewResource({
                                    ...newResource,
                                    access_rights: e.value,
                                })
                            }
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='host'>Хост</label>
                        <InputText
                            id='host'
                            value={newResource.host}
                            onChange={e =>
                                setNewResource({
                                    ...newResource,
                                    host: e.target.value,
                                })
                            }
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='size'>Размер</label>
                        <InputNumber
                            id='size'
                            value={newResource.size}
                            onValueChange={e =>
                                setNewResource({
                                    ...newResource,
                                    size: e.value || 0,
                                })
                            }
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='frequency_of_use_in_month'>
                            Частота использования (мес)
                        </label>
                        <InputNumber
                            id='frequency_of_use_in_month'
                            value={newResource.frequency_of_use_in_month}
                            onValueChange={e =>
                                setNewResource({
                                    ...newResource,
                                    frequency_of_use_in_month: e.value || 0,
                                })
                            }
                        />
                    </div>
                </div>
            </Dialog>
        </div>
    );
};

export default MainDataTable;
