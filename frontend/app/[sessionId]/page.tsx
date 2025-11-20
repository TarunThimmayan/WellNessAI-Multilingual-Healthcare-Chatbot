'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { isAuthenticated } from '../../utils/auth';
import ChatPage from '../page';

export default function SessionPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params?.sessionId as string;
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  useEffect(() => {
    // Check authentication on client side
    if (isMounted) {
      const authenticated = isAuthenticated();
      if (!authenticated) {
        router.push('/auth');
        return;
      }
    }
  }, [router, isMounted]);

  if (!sessionId) {
    if (isMounted) {
      router.push('/');
    }
    return null;
  }

  // Pass sessionId to ChatPage immediately - it will handle auth check and show loading animation
  // ChatPage will show the default loading animation while loading messages
  return <ChatPage initialSessionId={sessionId} />;
}

