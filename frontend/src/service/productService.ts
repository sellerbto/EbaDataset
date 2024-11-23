export const ProductService = {
    getServersData() {
        return [
            {
                hostname: 'unknown', // Пустое имя заменяется на "unknown"
                age: 0, // Размер данных (size) равен 0, что значит возраст не указан
                access_rights: 'unknown', // Нет данных о правах доступа
                last_access_date: '2024-11-23T14:39:55.530381Z', // Взято из `last_read`
                last_modification_date: '2024-11-23T14:39:55.530381Z', // Взято из `last_modified`
            },
            {
                hostname: '234',
                age: 0,
                access_rights: 'unknown',
                last_access_date: '2024-11-23T14:40:23.103175Z',
                last_modification_date: '2024-11-23T14:40:23.103175Z',
            },
            {
                hostname: '4444',
                age: 0,
                access_rights: 'unknown',
                last_access_date: '2024-11-23T14:40:27.185439Z',
                last_modification_date: '2024-11-23T14:40:27.185439Z',
            },
            {
                hostname: '5555',
                age: 0,
                access_rights: 'unknown',
                last_access_date: '2024-11-23T14:40:31.644517Z',
                last_modification_date: '2024-11-23T14:40:31.644517Z',
            },
        ];
    },

    getServers() {
        return Promise.resolve(this.getServersData());
    },
};
