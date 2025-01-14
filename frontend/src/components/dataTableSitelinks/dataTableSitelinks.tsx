import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { confirmDialog } from 'primereact/confirmdialog';
import { DataTable } from 'primereact/datatable';
import { Dialog } from 'primereact/dialog';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from 'primereact/inputtextarea';
import { ProgressSpinner } from 'primereact/progressspinner';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { useContext, useEffect, useState } from 'react';

import { ToastContext } from '../../context/toastContext.tsx';
import { useAppDispatch, useAppSelector } from '../../store';
import {
    createOrUpdateLink,
    deleteLink,
    fetchLinks,
} from '../../store/api-actions.ts';
import { LinkData } from '../../types/link.ts';
import './dataTableSitelinks.scss';

const LinkDataTable = () => {
    const toastContext = useContext(ToastContext);
    const dispatch = useAppDispatch();
    const links = useAppSelector(state => state.currentLinks);
    const loading = useAppSelector(state => state.linksLoading);
    const [dialogVisible, setDialogVisible] = useState(false);
    const [newLink, setNewLink] = useState<LinkData>({
        name: '',
        url: '',
        description: '',
    });

    useEffect(() => {
        dispatch(fetchLinks()).catch(err => {
            toastContext?.show({
                severity: 'error',
                summary: 'Ошибка',
                detail: `Не удалось загрузить ссылки: ${String(err)}`,
            });
        });
    }, [dispatch, toastContext]);

    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        if (typeof newValue === 'string' && newValue.trim().length === 0) {
            event.preventDefault();
            console.warn(`Поле "${field}" не может быть пустым!`);
            return;
        }

        const updatedLink: LinkData = { ...rowData, [field]: newValue };

        dispatch(createOrUpdateLink(updatedLink))
            .then(() => {
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Ресурс успешно изменен.',
                    life: 3000,
                });
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось изменить ресурс.',
                    life: 3000,
                });
            });
    };

    const confirmDeleteLink = (rowData: LinkData) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ссылку "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                dispatch(deleteLink(rowData.url))
                    .unwrap()
                    .then(() => {
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
        });
    };

    const textEditor = (options: ColumnEditorOptions) => (
        <InputText
            value={options.value}
            onChange={(e: React.ChangeEvent<HTMLInputElement>) =>
                options.editorCallback?.(e.target.value)
            }
            onKeyDown={e => e.stopPropagation()}
        />
    );

    const cellEditor = (options: ColumnEditorOptions) => textEditor(options);

    const linkBodyTemplate = (rowData: LinkData) => (
        <a href={rowData.url} target='_blank' rel='noopener noreferrer'>
            {rowData.url}
        </a>
    );

    const deleteBodyTemplate = (rowData: LinkData) => (
        <Button
            icon='pi pi-trash'
            className='p-button-danger p-button-sm'
            onClick={e => {
                e.stopPropagation();
                confirmDeleteLink(rowData);
            }}
            tooltip='Удалить'
            tooltipOptions={{ position: 'top' }}
        />
    );

    const openAddLinkDialog = () => {
        setDialogVisible(true);
    };

    const closeAddLinkDialog = () => {
        setDialogVisible(false);
        setNewLink({
            name: '',
            url: '',
            description: '',
        });
    };

    const handleAddLink = () => {
        if (!newLink.name || !newLink.url || !newLink.description) {
            alert('Все поля должны быть заполнены');
            return;
        }

        dispatch(createOrUpdateLink(newLink))
            .then(() => {
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
        closeAddLinkDialog();
    };

    if (loading) {
        return (
            <div className='table-container'>
                <div
                    className='loading-container'
                    style={{ textAlign: 'center', padding: '2rem' }}
                >
                    <ProgressSpinner />
                </div>
            </div>
        );
    }

    return (
        <div className='table-container'>
            <DataTable
                value={links}
                sortMode='multiple'
                paginator
                rows={10}
                tableStyle={{ minWidth: '50rem' }}
                editMode='cell'
            >
                <Column
                    field='name'
                    header='Название'
                    sortable
                    style={{ width: '25%' }}
                    editor={cellEditor}
                    onCellEditComplete={onCellEditComplete}
                />
                <Column
                    field='url'
                    header='Ссылка'
                    sortable
                    style={{ width: '25%' }}
                    body={linkBodyTemplate}
                />
                <Column
                    field='description'
                    header='Описание'
                    sortable
                    style={{ width: '45%' }}
                    editor={cellEditor}
                    onCellEditComplete={onCellEditComplete}
                />
                <Column
                    header='Delete'
                    body={deleteBodyTemplate}
                    style={{ width: '5%', textAlign: 'center' }}
                />
            </DataTable>

            <div className='table-toolbar'>
                <Button
                    icon='pi pi-plus'
                    label='Добавить ссылку'
                    className='p-button-success p-button-block'
                    onClick={openAddLinkDialog}
                />
            </div>

            <Dialog
                header='Добавить новую ссылку'
                visible={dialogVisible}
                onHide={closeAddLinkDialog}
                style={{ width: '50vw' }}
                footer={
                    <div>
                        <Button
                            label='Отмена'
                            icon='pi pi-times'
                            onClick={closeAddLinkDialog}
                            className='p-button-text'
                        />
                        <Button
                            label='Добавить'
                            icon='pi pi-check'
                            onClick={handleAddLink}
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
                            value={newLink.name}
                            onChange={e =>
                                setNewLink({ ...newLink, name: e.target.value })
                            }
                            autoFocus
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='url'>URL</label>
                        <InputText
                            id='url'
                            value={newLink.url}
                            onChange={e =>
                                setNewLink({ ...newLink, url: e.target.value })
                            }
                        />
                    </div>
                    <div className='p-field'>
                        <label htmlFor='description'>Описание</label>
                        <InputTextarea
                            id='description'
                            value={newLink.description}
                            onChange={e =>
                                setNewLink({
                                    ...newLink,
                                    description: e.target.value,
                                })
                            }
                            rows={3}
                        />
                    </div>
                </div>
            </Dialog>
        </div>
    );
};

export default LinkDataTable;
