import { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { 
  getAuth, 
  signInAnonymously, 
  signInWithCustomToken, 
  onAuthStateChanged,
  Auth
} from 'firebase/auth';
import { 
  getFirestore, 
  Firestore
} from 'firebase/firestore';
import { getFirebaseConfig } from '../constants/generator';

export const useFirebase = () => {
  const [db, setDb] = useState<Firestore | null>(null);
  const [auth, setAuth] = useState<Auth | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [isAuthReady, setIsAuthReady] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    try {
      const { firebaseConfig, initialAuthToken } = getFirebaseConfig();
      const app = initializeApp(firebaseConfig);
      const firestore = getFirestore(app);
      const authInstance = getAuth(app);
      
      setDb(firestore);
      setAuth(authInstance);

      // Attempt to sign in using the provided token or anonymously
      const attemptAuth = async () => {
        try {
          if (initialAuthToken) {
            await signInWithCustomToken(authInstance, initialAuthToken);
          } else {
            await signInAnonymously(authInstance); 
          }
        } catch (authError) {
          console.error("Firebase Auth Error:", authError);
          await signInAnonymously(authInstance); 
        }
      };

      attemptAuth();

      // Auth state listener to set userId
      const unsubscribe = onAuthStateChanged(authInstance, (user) => {
        if (user) {
          setUserId(user.uid);
        } else {
          setUserId(null);
        }
        setIsAuthReady(true);
      });

      return () => unsubscribe();
      
    } catch (e: any) {
      console.error("Firebase Init Error:", e.message);
      setIsAuthReady(true); 
      setError(`Initialization Failed: ${e.message}`);
    }
  }, []);

  return { db, auth, userId, isAuthReady, error };
};

