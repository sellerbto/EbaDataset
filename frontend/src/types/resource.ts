export interface Resource {
    id: string;
    name: string;
    description: string;
    access_rights: 'read' | 'write' | 'admin' | 'unknown';
    size: number;
    host: string;
    created_at_server: string;
    created_at_host: string;
    last_read: string;
    last_modified: string;
    frequency_of_use_in_month: number;
}
