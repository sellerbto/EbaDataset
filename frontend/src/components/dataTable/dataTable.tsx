import 'primeicons/primeicons.css';
import { Column } from 'primereact/column';
import { DataTable } from 'primereact/datatable';
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

const MultipleColumnsDemo: React.FC = () => {
    const [servers, setServers] = useState<Server[]>([]);

    useEffect(() => {
        ProductService.getServers().then((data: Server[]) => setServers(data));
    }, []);

    return (
        <div className='table-container'>
            <DataTable
                value={servers}
                sortMode='multiple'
                paginator
                rows={10}
                tableStyle={{ minWidth: '50rem' }}
            >
                <Column
                    field='hostname'
                    header='Hostname'
                    sortable
                    style={{ width: '20%' }}
                />
                <Column
                    field='age'
                    header='Age (years)'
                    sortable
                    style={{ width: '15%' }}
                />
                <Column
                    field='access_rights'
                    header='Access Rights'
                    sortable
                    style={{ width: '20%' }}
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

export default MultipleColumnsDemo;
