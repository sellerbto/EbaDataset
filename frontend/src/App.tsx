import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';
import { PrimeReactProvider } from 'primereact/api';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import './app.scss';
import MainDataTable from './components/dataTable/dataTable';
import LinkDataTable from './components/dataTableSitelinks/dataTableSitelinks';
import { MenuBar } from './components/menubar/menuBar';

function App() {
    return (
        <>
            <PrimeReactProvider>
                <MenuBar />
                <div className='main-content'>
                    <MainDataTable />
                    <LinkDataTable />
                </div>
            </PrimeReactProvider>
        </>
    );
}

export default App;
