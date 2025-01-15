import { Button } from 'primereact/button';
import { Menubar } from 'primereact/menubar';
import { useNavigate } from 'react-router-dom';
import './menuBar.scss';

export const MenuBar = () => {
    const navigate = useNavigate();

    const startContent = (
        <div className='logo-container'>
            <h1
                className='logo-text'
                style={{ cursor: 'pointer' }}
                onClick={() => navigate('/')}
            >
                Data Check Panel
            </h1>
        </div>
    );

    const items = [
        {
            label: 'Dashboard',
            icon: 'pi pi-fw pi-home',
            command: () => navigate('/'),
        },
        {
            label: 'Resources',
            icon: 'pi pi-fw pi-database',
            items: [
                {
                    label: 'Servers',
                    icon: 'pi pi-fw pi-server',
                    command: () => navigate('/servers'),
                },
                {
                    label: 'Links',
                    icon: 'pi pi-fw pi-link',
                    command: () => navigate('/links'),
                },
                { separator: true },
                {
                    label: 'Analytics',
                    icon: 'pi pi-fw pi-chart-bar',
                    command: () => {
                        /* команда */
                    },
                },
            ],
        },
    ];

    const endContent = (
        <div className='end-content'>
            <Button
                label='Sign In'
                icon='pi pi-sign-in'
                className='p-button-rounded p-button-secondary mr-2'
            />
        </div>
    );

    return (
        <div className='menubar-wrapper'>
            <Menubar model={items} start={startContent} end={endContent} />
        </div>
    );
};
