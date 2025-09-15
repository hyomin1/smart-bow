import axios, {
  AxiosError,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios';

export const api = axios.create({
  baseURL: import.meta.env.VITE_BASE_URL,
  withCredentials: true,
});

const handleRequestInterceptor = (
  config: InternalAxiosRequestConfig
): InternalAxiosRequestConfig => {
  return config;
};

const handleResponseInterceptor = async (
  error: AxiosError
): Promise<AxiosResponse> => {
  return Promise.reject(error);
};

api.interceptors.request.use(handleRequestInterceptor, Promise.reject);
api.interceptors.response.use((res) => res, handleResponseInterceptor);
