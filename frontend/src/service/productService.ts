export const ProductService = {
    getServersData() {
        return [
            {
                hostname: 'server123',
                age: 5.2,
                access_rights: 'admin',
                last_access_date: '2024-11-21T14:30:00Z',
                last_modification_date: '2024-11-20T10:15:00Z',
            },
            {
                hostname: 'server456',
                age: 3.8,
                access_rights: 'user',
                last_access_date: '2024-11-19T11:00:00Z',
                last_modification_date: '2024-11-18T09:45:00Z',
            },
            {
                hostname: 'server789',
                age: 7.1,
                access_rights: 'guest',
                last_access_date: '2024-11-15T08:20:00Z',
                last_modification_date: '2024-11-14T12:10:00Z',
            },
            {
                hostname: 'server321',
                age: 1.5,
                access_rights: 'admin',
                last_access_date: '2024-11-22T09:00:00Z',
                last_modification_date: '2024-11-21T13:30:00Z',
            },
            {
                hostname: 'server654',
                age: 4.6,
                access_rights: 'editor',
                last_access_date: '2024-11-18T16:00:00Z',
                last_modification_date: '2024-11-17T14:40:00Z',
            },
            {
                hostname: 'server098',
                age: 9.3,
                access_rights: 'user',
                last_access_date: '2024-11-12T10:20:00Z',
                last_modification_date: '2024-11-11T08:00:00Z',
            },
            {
                hostname: 'server765',
                age: 6.7,
                access_rights: 'guest',
                last_access_date: '2024-11-10T14:00:00Z',
                last_modification_date: '2024-11-09T17:25:00Z',
            },
            {
                hostname: 'server432',
                age: 2.1,
                access_rights: 'editor',
                last_access_date: '2024-11-23T12:10:00Z',
                last_modification_date: '2024-11-22T15:45:00Z',
            },
            {
                hostname: 'server999',
                age: 8.4,
                access_rights: 'admin',
                last_access_date: '2024-11-20T07:50:00Z',
                last_modification_date: '2024-11-19T11:00:00Z',
            },
            {
                hostname: 'server101',
                age: 4.0,
                access_rights: 'user',
                last_access_date: '2024-11-16T18:00:00Z',
                last_modification_date: '2024-11-15T09:45:00Z',
            },
        ];
    },

    getServers() {
        return Promise.resolve(this.getServersData());
    },
};
