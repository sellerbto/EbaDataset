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
import { linkService } from '../../services/linkService.ts';
import { LinkData } from '../../types/link.ts';
import './dataTableSitelinks.scss';

const LinkDataTable = () => {
    const toastContext = useContext(ToastContext);
    const [links, setLinks] = useState<LinkData[]>([]);
    const [loading, setLoading] = useState(false);
    const [dialogVisible, setDialogVisible] = useState(false);
    const [newLink, setNewLink] = useState<LinkData>({
        name: '',
        url: '',
        description: '',
    });

    //это я дописал
    useEffect(() => {
        setLoading(true);
        linkService
            .getLinks()
            .then(fetchedLinks => {
                setLinks(fetchedLinks);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, [toastContext]);

    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        if (typeof newValue === 'string' && newValue.trim().length === 0) {
            event.preventDefault();
            console.warn(`Field "${field}" cannot be empty.`);
            return;
        }

        const updatedLink: LinkData = { ...rowData, [field]: newValue };
        // это дописал
        linkService
            .updateLink(updatedLink)
            .then(() => {
                setLinks(prevLinks =>
                    prevLinks.map(link =>
                        link.url === rowData.url ? updatedLink : link
                    )
                );
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

    const confirmDelete = (rowData: { url: string; name: string }) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ссылку "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                // это написал
                linkService
                    .deleteLink(rowData.url)
                    .then(() => {
                        setLinks(prevLinks =>
                            prevLinks.filter(link => link.url !== rowData.url)
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

    const cellEditor = (options: ColumnEditorOptions) => textEditor(options);

    const linkBodyTemplate = (rowData: { url: string }) => (
        <a href={rowData.url} target='_blank' rel='noopener noreferrer'>
            {rowData.url}
        </a>
    );

    const deleteBodyTemplate = (rowData: { url: string; name: string }) => (
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

    const handleAddLink = async () => {
        if (!newLink.name || !newLink.url || !newLink.description) {
            alert('Все поля должны быть заполнены');
            return;
        }

        // это написал
        linkService
            .createLink(newLink)
            .then(createdLink => {
                setLinks(prevLinks => [...prevLinks, createdLink]);
                closeAddLinkDialog();
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
