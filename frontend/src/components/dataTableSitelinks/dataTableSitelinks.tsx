// src/components/dataTableSitelinks/LinkDataTable.tsx
import 'primeicons/primeicons.css';
import { Button } from 'primereact/button';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { confirmDialog } from 'primereact/confirmdialog';
import { DataTable } from 'primereact/datatable';
import { InputText } from 'primereact/inputtext';
import { ProgressSpinner } from 'primereact/progressspinner';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { useContext, useEffect, useState } from 'react';
import { ToastContext } from '../../context/toastContext';
import { linkService } from '../../services/linkService';
import { LinkData } from '../../types/link';
import './dataTableSitelinks.scss';

const LinkDataTable: React.FC = () => {
    const [links, setLinks] = useState<LinkData[]>([]);
    const [loading, setLoading] = useState<boolean>(true);
    const toastContext = useContext(ToastContext);

    useEffect(() => {
        linkService
            .getLinks()
            .then((fetchedLinks: LinkData[]) => {
                setLinks(fetchedLinks);
                setLoading(false);
            })
            .catch(() => {
                setLoading(false);
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось загрузить ссылки.',
                    life: 3000,
                });
            });
    }, [toastContext]);

    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

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

        const updatedLink: LinkData = { ...rowData, [field]: newValue };

        linkService
            .updateLink(updatedLink)
            .then((updated: LinkData) => {
                setLinks(prevLinks =>
                    prevLinks.map(link =>
                        link.id === updated.id ? updated : link
                    )
                );
                toastContext?.show({
                    severity: 'success',
                    summary: 'Успех',
                    detail: 'Ссылка успешно обновлена.',
                    life: 3000,
                });
            })
            .catch(() => {
                toastContext?.show({
                    severity: 'error',
                    summary: 'Ошибка',
                    detail: 'Не удалось обновить ссылку.',
                    life: 3000,
                });
            });
    };

    const confirmDelete = (rowData: LinkData) => {
        confirmDialog({
            message: `Вы уверены, что хотите удалить ссылку "${rowData.name}"?`,
            header: 'Подтверждение удаления',
            icon: 'pi pi-exclamation-triangle',
            accept: () => {
                linkService
                    .deleteLink(rowData.id)
                    .then(() => {
                        setLinks(prevLinks =>
                            prevLinks.filter(link => link.id !== rowData.id)
                        );
                        toastContext?.show({
                            severity: 'success',
                            summary: 'Успех',
                            detail: 'Ссылка успешно удалена.',
                            life: 3000,
                        });
                    })
                    .catch(() => {
                        toastContext?.show({
                            severity: 'error',
                            summary: 'Ошибка',
                            detail: 'Не удалось удалить ссылку.',
                            life: 3000,
                        });
                    });
            },
            reject: () => {
                toastContext?.show({
                    severity: 'info',
                    summary: 'Отменено',
                    detail: 'Удаление ссылки отменено.',
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
            )}
        </div>
    );
};

export default LinkDataTable;
