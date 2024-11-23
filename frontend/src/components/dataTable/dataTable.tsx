import 'primeicons/primeicons.css';
import { Column, ColumnEditorOptions, ColumnEvent } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
import {
    InputNumber,
    InputNumberValueChangeEvent,
} from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { useEffect, useState } from 'react';
import { ProductService } from '../../service/productService';
import './dataTable.scss';

interface Server {
    hostname: string;
    age: number;
    access_rights: string;
    last_access_date: string;
    last_modification_date: string;
}

const MainDataTable: React.FC = () => {
    const [servers, setServers] = useState<Server[]>([]);

    useEffect(() => {
        ProductService.getServers().then((data: Server[]) => setServers(data));
    }, []);

    // Обработчик завершения редактирования ячейки
    const onCellEditComplete = (e: ColumnEvent) => {
        const { rowData, newValue, field, originalEvent: event } = e;

        // Проверка и обновление значения ячейки
        if (field === 'age' && (typeof newValue !== 'number' || newValue < 0)) {
            event.preventDefault(); // Отклоняем изменение, если новое значение не является положительным числом
        } else if (
            typeof newValue === 'string' &&
            newValue.trim().length === 0
        ) {
            event.preventDefault(); // Отклоняем изменение, если новое значение пустое для строковых полей
        } else {
            rowData[field] = newValue; // Применяем новое значение
        }
    };

    // Функция, возвращающая компонент редактора для каждой ячейки
    const cellEditor = (options: ColumnEditorOptions) => {
        if (options.field === 'age') {
            return numberEditor(options);
        } else {
            return textEditor(options);
        }
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

    // Редактор для числовых ячеек
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

    return (
        <div className='table-container'>
            <DataTable
                value={servers}
                sortMode='multiple'
                paginator
                rows={10}
                tableStyle={{ minWidth: '50rem' }}
                editMode='cell'
            >
                <Column
                    field='hostname'
                    header='Hostname'
                    sortable
                    style={{ width: '20%' }}
                    editor={options => cellEditor(options)}
                    onCellEditComplete={onCellEditComplete}
                />
                <Column
                    field='age'
                    header='Age (years)'
                    sortable
                    style={{ width: '15%' }}
                    editor={options => cellEditor(options)}
                    onCellEditComplete={onCellEditComplete}
                />
                <Column
                    field='access_rights'
                    header='Access Rights'
                    sortable
                    style={{ width: '20%' }}
                    editor={options => cellEditor(options)}
                    onCellEditComplete={onCellEditComplete}
                />
                <Column
                    field='last_access_date'
                    header='Last Access Date'
                    sortable
                    style={{ width: '25%' }}
                    body={(rowData: Server) =>
                        new Date(rowData.last_access_date).toLocaleString()
                    }
                />
                <Column
                    field='last_modification_date'
                    header='Last Modification Date'
                    sortable
                    style={{ width: '20%' }}
                    body={(rowData: Server) =>
                        new Date(
                            rowData.last_modification_date
                        ).toLocaleString()
                    }
                />
            </DataTable>
        </div>
    );
};

export default MainDataTable;
