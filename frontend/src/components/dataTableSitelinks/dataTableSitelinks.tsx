import 'primeicons/primeicons.css';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import { InputText } from 'primereact/inputtext';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { useEffect, useState } from 'react';
import './dataTableSitelinks.scss';

interface LinkData {
    name: string;
    url: string;
    description: string;
}

const LinkDataTable: React.FC = () => {
    const [links, setLinks] = useState<LinkData[]>([]);

    useEffect(() => {
        // Здесь можно загрузить данные, например из сервиса или API
        setLinks([
            {
                name: 'OpenAI',
                url: 'https://www.openai.com',
                description: 'AI research lab',
            },
            {
                name: 'Google',
                url: 'https://www.google.com',
                description: 'Search engine',
            },
            {
                name: 'GitHub',
                url: 'https://www.github.com',
                description: 'Code hosting platform',
            },
        ]);
    }, []);

    // Обработчик завершения редактирования ячейки
    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        // Проверка и обновление значения ячейки
        if (typeof newValue === 'string' && newValue.trim().length === 0) {
            event.preventDefault(); // Отклоняем изменение, если новое значение пустое для строковых полей
        } else {
            rowData[field] = newValue; // Применяем новое значение
        }
    };

    // Функция, возвращающая компонент редактора для каждой ячейки
    const cellEditor = (options: ColumnEditorOptions) => {
        return textEditor(options);
    };

    // Редактор для текстовых ячеек
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

    // Шаблон для отображения ссылки как кликабельного URL
    const linkBodyTemplate = (rowData: LinkData) => (
        <a href={rowData.url} target='_blank' rel='noopener noreferrer'>
            {rowData.url}
        </a>
    );

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
                    editor={options => cellEditor(options)}
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
                    style={{ width: '50%' }}
                    editor={options => cellEditor(options)}
                    onCellEditComplete={onCellEditComplete}
                />
            </DataTable>
        </div>
    );
};

export default LinkDataTable;
