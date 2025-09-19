export const ROUTES = {
  HOME: '/',
  STREAM: (camId: string = ':camId') => `/stream/${camId}`,
};
