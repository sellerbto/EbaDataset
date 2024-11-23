import { Menubar } from 'primereact/menubar';
import './MenuBar.scss';

export const MenuBar = () => {
    const startContent = (
        <div className='logo-container'>
            <h1 className='logo-text'>Data check panel</h1>
        </div>
    );

    return (
        <div>
            <div className='fixed-menubar'>
                <Menubar start={startContent} />
            </div>
        </div>
    );
};
