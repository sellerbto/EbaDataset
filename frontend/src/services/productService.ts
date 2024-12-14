import { Resource } from '../types/resource';

const mockData: Resource[] = [
    {
        id: '1',
        name: 'serverA',
        access_rights: 'read',
        size: 1532,
        host: '192.168.0.10',
        created_at_server: new Date(2024, 10, 12, 10, 30, 15).toISOString(),
        created_at_host: new Date(2024, 10, 12, 10, 35, 5).toISOString(),
        last_read: new Date(2024, 11, 1, 12, 45, 30).toISOString(),
        last_modified: new Date(2024, 11, 1, 13, 15, 10).toISOString(),
        frequency_of_use_in_month: 5,
    },
    {
        id: '2',
        name: 'dataNodeX',
        access_rights: 'admin',
        size: 9845,
        host: '10.0.1.25',
        created_at_server: new Date(2023, 5, 22, 9, 0, 0).toISOString(),
        created_at_host: new Date(2023, 5, 22, 9, 5, 0).toISOString(),
        last_read: new Date(2024, 10, 25, 18, 20, 45).toISOString(),
        last_modified: new Date(2024, 10, 25, 18, 30, 0).toISOString(),
        frequency_of_use_in_month: 12,
    },
];

export const ProductService = {
    /**
     * Получение всех серверов (ресурсов)
     * @returns Promise, возвращающий массив Resource
     */
    async getServers(): Promise<Resource[]> {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve([...mockData]);
            }, 2000);
        });
    },

    /**
     * Обновление существующего сервера (ресурса)
     * @param updatedServer - Обновленные данные ресурса
     * @returns Promise, возвращающий обновленный Resource
     */
    async updateServer(updatedServer: Resource): Promise<Resource> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const index = mockData.findIndex(
                    server => server.id === updatedServer.id
                );
                if (index !== -1) {
                    mockData[index] = { ...updatedServer };
                    resolve({ ...mockData[index] });
                } else {
                    reject(new Error('Ресурс не найден'));
                }
            }, 1000);
        });
    },

    /**
     * Удаление сервера (ресурса) по ID
     * @param id - Идентификатор ресурса
     * @returns Promise<void>
     */
    async deleteServer(id: string): Promise<void> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const index = mockData.findIndex(server => server.id === id);
                if (index !== -1) {
                    mockData.splice(index, 1);
                    resolve();
                } else {
                    reject(new Error('Ресурс не найден'));
                }
            }, 1000);
        });
    },

    /**
     * Создание нового сервера (ресурса)
     * @param newServer - Данные нового ресурса без ID
     * @returns Promise, возвращающий созданный Resource
     */
    async createServer(newServer: Omit<Resource, 'id'>): Promise<Resource> {
        return new Promise(resolve => {
            setTimeout(() => {
                const id = (mockData.length + 1).toString();
                const createdServer: Resource = { id, ...newServer };
                mockData.push(createdServer);
                resolve({ ...createdServer });
            }, 1000);
        });
    },
};
