// Cliente HTTP para comunicação com a API Django

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, ApiError } from '../types';

// Configuração base da API
const BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Criar instância do Axios
const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor de request para adicionar token de autenticação
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor de response para tratamento global de erros
apiClient.interceptors.response.use(
  (response: AxiosResponse<ApiResponse>) => {
    return response;
  },
  (error) => {
    const apiError: ApiError = {
      message: 'Erro desconhecido',
      status: 500,
    };

    if (error.response) {
      // Erro da API
      apiError.status = error.response.status;
      apiError.message = error.response.data?.message || error.response.data?.detail || 'Erro do servidor';
      apiError.errors = error.response.data?.errors;

      // Tratar erro de autenticação
      if (error.response.status === 401) {
        localStorage.removeItem('authToken');
        localStorage.removeItem('refreshToken');
        window.location.href = '/login';
      }
    } else if (error.request) {
      // Erro de rede
      apiError.message = 'Erro de conexão. Verifique sua internet.';
      apiError.status = 0;
    } else {
      // Erro de configuração
      apiError.message = error.message || 'Erro na configuração da requisição';
    }

    return Promise.reject(apiError);
  }
);

// Funções auxiliares para requests
export const api = {
  get: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.get(url, config).then(response => response.data),
    
  post: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.post(url, data, config).then(response => response.data),
    
  put: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.put(url, data, config).then(response => response.data),
    
  patch: <T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.patch(url, data, config).then(response => response.data),
    
  delete: <T = any>(url: string, config?: AxiosRequestConfig): Promise<T> =>
    apiClient.delete(url, config).then(response => response.data),
};

// Função para configurar token de autenticação
export const setAuthToken = (token: string | null) => {
  if (token) {
    localStorage.setItem('authToken', token);
    apiClient.defaults.headers.Authorization = `Bearer ${token}`;
  } else {
    localStorage.removeItem('authToken');
    delete apiClient.defaults.headers.Authorization;
  }
};

// Função para obter URL base da API
export const getApiBaseUrl = () => BASE_URL;

// Função para obter URL base do WebSocket
export const getWebSocketBaseUrl = () => {
  const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const apiHost = BASE_URL.replace(/^https?:\/\//, '');
  return `${wsProtocol}//${apiHost}`;
};

export default apiClient;