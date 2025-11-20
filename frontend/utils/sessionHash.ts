/**
 * Utility functions for hashing session IDs for URL-safe display
 * Uses SHA-256 hashing with a secret to create short, URL-safe identifiers
 */

/**
 * Hash a session ID to create a URL-safe identifier
 * Uses Web Crypto API for secure hashing
 * 
 * @param sessionId - The original session ID (UUID)
 * @returns A hashed, URL-safe identifier (16 characters)
 */
export async function hashSessionId(sessionId: string): Promise<string> {
  if (typeof window === 'undefined' || !window.crypto || !window.crypto.subtle) {
    // Fallback for environments without Web Crypto API
    return fallbackHash(sessionId);
  }

  try {
    // Use a simple secret (in production, this should be consistent)
    // For frontend, we'll use a fixed salt since we can't store secrets client-side
    // The backend will use the same secret to verify
    const secret = 'healthcare-chatbot-session-hash-v1';
    const encoder = new TextEncoder();
    const data = encoder.encode(sessionId + secret);
    
    // Hash using SHA-256
    const hashBuffer = await window.crypto.subtle.digest('SHA-256', data);
    
    // Convert to hex string
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    
    // Use first 16 characters for shorter URLs
    // Base64 encode the first 12 bytes for URL-safe characters
    const base64 = btoa(String.fromCharCode(...hashArray.slice(0, 12)))
      .replace(/\+/g, '-')
      .replace(/\//g, '_')
      .replace(/=/g, '');
    
    return base64.substring(0, 16);
  } catch (error) {
    console.warn('Error hashing session ID, using fallback:', error);
    return fallbackHash(sessionId);
  }
}

/**
 * Fallback hash function for environments without Web Crypto API
 * Uses a simple hash function (not cryptographically secure, but sufficient for URL obfuscation)
 */
function fallbackHash(sessionId: string): string {
  let hash = 0;
  const secret = 'healthcare-chatbot-session-hash-v1';
  const str = sessionId + secret;
  
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // Convert to 32-bit integer
  }
  
  // Convert to positive hex and take first 16 chars
  const hex = Math.abs(hash).toString(16).padStart(8, '0');
  // Add some characters from the session ID for uniqueness
  const unique = sessionId.substring(0, 8).replace(/-/g, '');
  return (hex + unique).substring(0, 16);
}

/**
 * Check if a string looks like a hashed session ID (not a UUID)
 * UUIDs have format: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
 */
export function isHashedSessionId(id: string): boolean {
  // UUIDs have dashes, hashed IDs don't
  return !id.includes('-') && id.length <= 16;
}

