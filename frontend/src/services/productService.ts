import { Resource } from '../types/resource';

// Определяем интерфейсы, соответствующие данным из бэкенда (Swagger)
interface DatasetInfo {
    id: number; // бэкенд возвращает число, а у нас во фронте в Resource — id: string
    file_path: string;
    size: number;
    host: string;
    created_at_server: string | null;
    created_at_host: string | null;
    last_read: string | null;
    last_modified: string | null;
    frequency_of_use_in_month: number | null;
}

interface DatasetsSummary {
    dataset_general_info_id: number;
    name: string;
    description: string;
    datasets_infos: DatasetInfo[];
}

export const ProductService = {
    /**
     * Получаем все датасеты (бэкенд: GET /dashboard/datasets),
     * преобразуем их в формат Resource[], чтобы потом отобразить в вашей таблице.
     */
    async getServers(): Promise<Resource[]> {
        const response = await fetch('/dashboard/datasets', {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        });

        if (!response.ok) {
            throw new Error('Не удалось загрузить ресурсы с сервера');
        }

        // Бэкенд возвращает DatasetsSummary[]
        const datasets: DatasetsSummary[] = await response.json();

        // Преобразуем DatasetsSummary[] -> Resource[]
        const resources: Resource[] = [];

        for (const ds of datasets) {
            // ds.datasets_infos — массив DatasetInfo
            for (const info of ds.datasets_infos) {
                // Собираем объект Resource
                const resource: Resource = {
                    id: String(info.id), // number -> string
                    // В вашем фронтовом интерфейсе 'name' и 'description' находятся в Resource,
                    // а на бэкенде эти поля в DatasetsSummary
                    name: ds.name,
                    description: ds.description,
                    // Так как в Swagger нет поля "access_rights", задаём дефолт:
                    access_rights: 'unknown',
                    // Остальные поля берем из DatasetInfo
                    size: info.size ?? 0,
                    host: info.host ?? '',
                    created_at_server: info.created_at_server ?? '',
                    created_at_host: info.created_at_host ?? '',
                    last_read: info.last_read ?? '',
                    last_modified: info.last_modified ?? '',
                    frequency_of_use_in_month:
                        info.frequency_of_use_in_month ?? 0,
                };
                resources.push(resource);
            }
        }

        return resources;
    },

    /**
     * Пример: Создание нового "датасета" (PUT /dashboard/datasets)
     * (Вы сами решаете, как будете «сопоставлять» эти данные с Resource или другими полями.)
     */
    async createServer(newServer: Omit<Resource, 'id'>): Promise<Resource> {
        // newServer содержит только name и description (по вашей логике).
        // Бэкенд ожидает { "name": string, "description": string }
        const body = {
            name: newServer.name,
            description: newServer.description,
        };

        const response = await fetch('/dashboard/datasets', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error('Не удалось создать ресурс на сервере');
        }

        // Согласно Swagger, ответ `200` даёт пустой объект `{}` (или пустой),
        // поэтому нам нужно возвращать что-то для Resource.
        // Пока что можно вернуть «заглушку» или повторно вызвать getServers.
        // Для простоты вернем объект с полями, которые были отправлены:
        const createdResource: Resource = {
            // Придется сгенерировать некий id,
            id: 'temp-id-' + Date.now(),
            name: newServer.name,
            description: newServer.description,
            access_rights: 'unknown',
            size: 0,
            host: '',
            created_at_server: '',
            created_at_host: '',
            last_read: '',
            last_modified: '',
            frequency_of_use_in_month: 0,
        };

        return createdResource;
    },

    /**
     * Пример: Обновление описания датасета (POST /dashboard/datasets)
     */
    async updateServer(updatedServer: Resource): Promise<Resource> {
        // По Swagger, сервер ожидает { "id": number, "name": string, "description": string }
        // У вас updatedServer.id — строка, нужно преобразовать в число.
        const body = {
            id: Number(updatedServer.id),
            name: updatedServer.name,
            description: updatedServer.description,
        };

        const response = await fetch('/dashboard/datasets', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });

        if (!response.ok) {
            throw new Error('Не удалось обновить ресурс');
        }

        // Сервер возвращает { "message": "Dataset description updated successfully" }
        // Нам нужно самим «придумать», что возвращать в коде. Пусть будет тот же updatedServer.
        return updatedServer;
    },

    /**
     * Пример: Удаление датасета (у вас нет явного эндпоинта DELETE /dashboard/datasets/{id}?)
     * Возможно, нужно другое решение. Или вообще нет логики удаления на бэкенде?
     */
    async deleteServer(id: string): Promise<void> {
        // Если у вас нет DELETE /dashboard/datasets/{id}, придётся написать свой эндпоинт.
        // Или как-то иначе обрабатывать. Здесь - просто пример запроса:
        const response = await fetch(`/dashboard/datasets/${id}`, {
            method: 'DELETE',
        });
        if (!response.ok) {
            throw new Error('Не удалось удалить ресурс');
        }
    },
};
