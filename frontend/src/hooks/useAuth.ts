import { useMockFirebase } from './useMockFirebase';
import { useFirebase } from './useFirebase';

// Select mock or real auth based on Vite env flag
export const useAuth = () => {
  const useMock = (import.meta as any).env?.VITE_USE_MOCK_AUTH === 'true';
  return useMock ? useMockFirebase() : useFirebase();
};
