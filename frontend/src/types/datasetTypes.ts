// src/types/datasetTypes.ts

/**
 * Интерфейс для одного DatasetInfo.
 * Соответствует бэкенд-модели DatasetInfo.
 */
export interface DatasetInfo {
    id: number;
    file_path: string;
    size: number;
    host: string;
    created_at_server?: string; // nullable - значит, может прийти null => в TS указываем необязательное поле
    created_at_host?: string;
    last_read?: string;
    last_modified?: string;
    frequency_of_use_in_month?: number;
}

/**
 * Интерфейс для одного DatasetsSummary.
 * Соответствует бэкенд-модели DatasetsSummary.
 */
export interface DatasetsSummary {
    dataset_general_info_id: number;
    name: string;
    description: string;
    datasets_infos: DatasetInfo[];
}
