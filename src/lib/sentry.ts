import * as Sentry from '@sentry/react';

const isProduction = import.meta.env.PROD;
const dsn = import.meta.env.VITE_SENTRY_DSN;

if (isProduction && dsn) {
  Sentry.init({
    dsn,
    integrations: [
      Sentry.browserTracingIntegration(),
      Sentry.replayIntegration({
        maskAllText: true,
        blockAllMedia: true,
      }),
    ],
    // Performance Monitoring
    tracesSampleRate: 1.0, // Capture 100% of the transactions
    // Session Replay
    replaysSessionSampleRate: 0.1, // This sets the sample rate at 10%
    replaysOnErrorSampleRate: 1.0, // If you're not already sampling the entire session, change the sample rate to 100% when sampling sessions where errors occur.
    environment: import.meta.env.MODE,
    beforeSend(event, hint) {
      // Filter out development errors in production
      if (event.exception) {
        console.error('Sentry Error:', event.exception);
      }
      return event;
    },
  });

  // Set user context
  Sentry.setUser({
    id: 'anonymous', // Will be updated when user logs in
  });

  // Set tags
  Sentry.setTag('component', 'frontend');
  Sentry.setTag('version', import.meta.env.VITE_APP_VERSION || '1.0.0');
}

// Performance monitoring helper
export const startTransaction = (name: string, op: string) => {
  if (!isProduction) return null;

  const span = Sentry.startInactiveSpan({
    name,
    op,
  });
  
  return span;
};

// Error boundary for React components
export const SentryErrorBoundary = Sentry.ErrorBoundary;

// Custom error reporting
export const reportError = (error: Error, context?: Record<string, any>) => {
  if (isProduction) {
    Sentry.captureException(error, {
      tags: {
        component: 'frontend',
        ...context,
      },
    });
  } else {
    console.error('Error:', error, context);
  }
};

// Performance measurement
export const measurePerformance = (name: string, fn: () => void) => {
  const transaction = startTransaction(name, 'function');
  try {
    fn();
  } finally {
    transaction?.end();
  }
};

// Update user context when user logs in
export const setUserContext = (user: { id: string; email: string; role: string }) => {
  if (isProduction) {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      role: user.role,
    });
    Sentry.setTag('user_role', user.role);
  }
};

// Clear user context on logout
export const clearUserContext = () => {
  if (isProduction) {
    Sentry.setUser(null);
    Sentry.setTag('user_role', undefined);
  }
};

export { Sentry };
export default Sentry;
