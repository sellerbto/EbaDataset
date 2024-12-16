import { LinkData } from '../types/link';

const mockLinks: LinkData[] = [
    {
        name: 'OpenAI',
        url: 'https://www.openai.com',
        description: 'AI research lab',
    },
    {
        name: 'Google',
        url: 'https://www.google.com',
        description: 'Search engine',
    },
    {
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
                    link => link.url === updatedLink.url
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
     * Удаление ссылки по URL
     * @param url - URL ссылки
     * @returns Promise<void>
     */
    async deleteLink(url: string): Promise<void> {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                const index = mockLinks.findIndex(link => link.url === url);
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
     * @param newLink - Данные новой ссылки
     * @returns Promise<LinkData>
     */
    async createLink(newLink: Omit<LinkData, 'id'>): Promise<LinkData> {
        return new Promise(resolve => {
            setTimeout(() => {
                mockLinks.push(newLink);
                resolve({ ...newLink });
            }, 1000);
        });
    },
};
