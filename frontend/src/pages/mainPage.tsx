import React from 'react';
import MainDataTable from '../components/dataTable/dataTable';
import { MenuBar } from '../components/menubar/menuBar';

const MainPage: React.FC = () => {
    return (
        <>
            <MenuBar />
            <div className='main-content'>
                <MainDataTable />
            </div>
        </>
    );
};

export default MainPage;
