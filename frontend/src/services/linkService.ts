import { LinkData } from '../types/link';

const mockLinks: LinkData[] = [
    {
        id: '1',
        name: 'OpenAI',
        url: 'https://www.openai.com',
        description: 'AI research lab',
    },
    {
        id: '2',
        name: 'Google',
        url: 'https://www.google.com',
        description: 'Search engine',
    },
    {
        id: '3',
        name: 'GitHub',
        url: 'https://www.github.com',
        description: 'Code hosting platform',
    },
];

export const linkService = {
    /**
     * Получение всех ссылок
     * @returns Promise, возвращающий массив LinkData
     */
    async getLinks(): Promise<LinkData[]> {
        return new Promise(resolve => {
            setTimeout(() => {
                resolve([...mockLinks]);
            }, 2000);
        });
    },

    /**
     * Обновление существующей ссылки
     * @param updatedLink - Обновленные данные ссылки
     * @returns Promise, возвращающий обновленный LinkData
     */
    async updateLink(updatedLink: LinkData): Promise<LinkData> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const index = mockLinks.findIndex(
                    link => link.id === updatedLink.id
                );
                if (index !== -1) {
                    mockLinks[index] = { ...updatedLink };
                    resolve({ ...mockLinks[index] });
                } else {
                    reject(new Error('Ссылка не найдена'));
                }
            }, 1000);
        });
    },

    /**
     * Удаление ссылки по ID
     * @param id - Идентификатор ссылки
     * @returns Promise<void>
     */
    async deleteLink(id: string): Promise<void> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const index = mockLinks.findIndex(link => link.id === id);
                if (index !== -1) {
                    mockLinks.splice(index, 1);
                    resolve();
                } else {
                    reject(new Error('Ссылка не найдена'));
                }
            }, 1000);
        });
    },

    /**
     * Создание новой ссылки
     * @param newLink - Данные новой ссылки без ID
     * @returns Promise<LinkData>
     */
    async createLink(newLink: Omit<LinkData, 'id'>): Promise<LinkData> {
        return new Promise(resolve => {
            setTimeout(() => {
                const id = (mockLinks.length + 1).toString();
                const createdLink: LinkData = { id, ...newLink };
                mockLinks.push(createdLink);

                resolve({ ...createdLink });
            }, 1000);
        });
    },
};
