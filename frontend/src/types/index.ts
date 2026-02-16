export interface User {
    id: number;
    email: string;
    full_name: string;
    role: 'PATIENT' | 'CLINICIAN' | 'ADMIN';
    has_consented: boolean;
    is_active: boolean;
}

export interface TokenResponse {
    access_token: string;
    refresh_token: string;
    token_type: string;
}

export interface ChatMessage {
    id: number;
    role: 'user' | 'assistant';
    content: string;
    intent?: string;
    entities?: string;
    is_emergency: boolean;
    created_at: string;
}

export interface Conversation {
    id: number;
    title: string;
    is_active: boolean;
    created_at: string;
    updated_at: string;
    message_count?: number;
    messages?: ChatMessage[];
}

export interface Appointment {
    id: number;
    title: string;
    doctor_name?: string;
    location?: string;
    notes?: string;
    scheduled_at: string;
    created_at: string;
}

export interface Medication {
    id: number;
    medication_name: string;
    dosage: string;
    frequency: string;
    time_of_day?: string;
    notes?: string;
    start_date: string;
    end_date?: string;
    created_at: string;
}

export interface Feedback {
    id: number;
    user_id: number;
    message_id?: number;
    rating: number;
    comment?: string;
    created_at: string;
}

export interface SymptomQuestion {
    session_id?: string;
    node_id: string;
    question: string;
    options: { text: string }[];
    category: string;
    is_final: boolean;
}

export interface SymptomResult {
    is_final: true;
    result: {
        conditions: {
            name: string;
            probability: number;
            description: string;
            recommendation: string;
        }[];
        recommendation: string;
        urgency: string;
        disclaimer: string;
    };
}

export interface SystemMetrics {
    total_users: number;
    total_conversations: number;
    total_messages: number;
    total_appointments: number;
    total_feedbacks: number;
    average_rating?: number;
}

export interface ClinicianNote {
    id: number;
    clinician_id: number;
    patient_id: number;
    conversation_id?: number;
    content: string;
    created_at: string;
}
