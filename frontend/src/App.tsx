import 'primeflex/primeflex.css';
import 'primeicons/primeicons.css';
import { PrimeReactProvider } from 'primereact/api';
import { ConfirmDialog } from 'primereact/confirmdialog';
import 'primereact/resources/primereact.min.css';
import 'primereact/resources/themes/saga-blue/theme.css';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './app.scss';
import { ToastProvider } from './context/toastContext';
import HomePage from './pages/homePage';
import LinksPage from './pages/linkPage';
import MainPage from './pages/mainPage';

function App() {
    return (
        <PrimeReactProvider>
            <BrowserRouter>
                <ConfirmDialog />
                <ToastProvider>
                    <Routes>
                        <Route path='/' element={<HomePage />} />
                        <Route path='/servers' element={<MainPage />} />
                        <Route path='/links' element={<LinksPage />} />
                    </Routes>
                </ToastProvider>
            </BrowserRouter>
        </PrimeReactProvider>
    );
}

export default App;
