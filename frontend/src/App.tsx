import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import './app.scss';
import MultipleColumnsDemo from './components/dataTable/dataTable';
import { MenuBar } from './components/menubar/menuBar';

function App() {
    return (
        <>
            <MenuBar />
            <div className='main-content'>
                <h2>Server Management</h2>
                <MultipleColumnsDemo />
            </div>
        </>
    );
}

export default App;
