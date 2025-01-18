export interface Specialty {
    id: string;
    title: string;
    title_ar: string;
    icon: string;
    background_color: string;
    color_class: string;
    description: string;
    description_ar: string;
    total_time_call: number;
    warning_time_call: number;
    alert_time_call: number;
    status: boolean;
    updated_at: string;
}

export interface SpecialtyResponse {
    status: string;
    data: {
        specialty: Specialty;
    };
}

export interface SpecialtiesListResponse {
    status: string;
    data: {
        specialties: Specialty[];
        pagination: {
            count: number;
            total_pages: number;
            current_page: number;
            page_size: number;
            next: string | null;
            previous: string | null;
        };
    };
}

export interface CreateSpecialtyRequest {
    title: string;
    title_ar: string;
    icon?: string;
    background_color?: string;
    color_class?: string;
    description?: string;
    description_ar?: string;
    total_time_call?: number;
    warning_time_call?: number;
    alert_time_call?: number;
    status?: boolean;
} 