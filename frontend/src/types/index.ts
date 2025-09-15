// Tipos gerais da aplicação

export * from './chat';

// Tipos de autenticação
export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface AuthUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login?: string;
}

export interface AuthToken {
  access: string;
  refresh: string;
}

export interface AuthState {
  user: AuthUser | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Tipos de resposta da API
export interface ApiResponse<T = any> {
  data: T;
  message?: string;
  status: number;
}

export interface ApiError {
  message: string;
  errors?: Record<string, string[]>;
  status: number;
}

// Tipos para navegação
export interface NavItem {
  label: string;
  path: string;
  icon?: React.ComponentType;
  badge?: number;
  children?: NavItem[];
}

// Tipos para tema
export interface ThemeColors {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  surface: string;
  text: {
    primary: string;
    secondary: string;
    disabled: string;
  };
  border: string;
  error: string;
  warning: string;
  success: string;
  info: string;
}

export interface Theme {
  name: 'light' | 'dark';
  colors: ThemeColors;
}

// Estados de loading
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

// Tipos para formulários
export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea' | 'checkbox';
  placeholder?: string;
  required?: boolean;
  options?: { value: string | number; label: string }[];
  validation?: {
    min?: number;
    max?: number;
    pattern?: RegExp;
    message?: string;
  };
}

// Tipos para notificações
export interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message?: string;
  duration?: number;
  action?: {
    label: string;
    handler: () => void;
  };
}

// Estados globais
export interface GlobalState {
  theme: 'light' | 'dark';
  notifications: Notification[];
  isOnline: boolean;
  currentCampaign?: number;
}

// Tipos utilitários
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;
export type RequiredFields<T, K extends keyof T> = T & Required<Pick<T, K>>;

// Tipos para componentes
export interface BaseComponentProps {
  className?: string;
  children?: React.ReactNode;
}

export interface IconProps extends BaseComponentProps {
  size?: number;
  color?: string;
}

// Tipos para eventos
export interface ChatEvent {
  type: 'message' | 'join' | 'leave' | 'typing' | 'command';
  data: any;
  timestamp: Date;
  userId?: number;
}

// Configurações da aplicação
export interface AppConfig {
  apiBaseUrl: string;
  wsBaseUrl: string;
  enableDevTools: boolean;
  theme: {
    default: 'light' | 'dark';
    allowToggle: boolean;
  };
  chat: {
    maxMessageLength: number;
    typingTimeout: number;
    reconnectAttempts: number;
    historyPageSize: number;
  };
  notifications: {
    defaultDuration: number;
    maxNotifications: number;
    enableSound: boolean;
  };
}