import React from 'react';
import LinkDataTable from '../components/dataTableSitelinks/dataTableSitelinks';
import { MenuBar } from '../components/menubar/menuBar';

const LinksPage: React.FC = () => {
    return (
        <>
            <MenuBar />
            <div className='main-content'>
                <LinkDataTable />
            </div>
        </>
    );
};

export default LinksPage;
