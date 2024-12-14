import React from 'react';
import HomeInfo from '../components/homeInfo/homeInfo';
import { MenuBar } from '../components/menubar/menuBar';

const HomePage: React.FC = () => {
    return (
        <>
            <MenuBar />
            <div className='home-page-content'>
                <HomeInfo />
            </div>
        </>
    );
};

export default HomePage;
