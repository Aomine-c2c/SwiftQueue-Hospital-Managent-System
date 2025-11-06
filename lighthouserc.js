module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
      startServerCommand: 'npm run dev',
      startServerReadyPattern: 'Local:.*:5173',
      url: ['http://localhost:5173'],
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.8 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['error', { minScore: 0.9 }],
        'categories:seo': ['error', { minScore: 0.9 }],
        'categories:pwa': 'off', // Disable PWA checks for now
      },
    },
    upload: {
      target: 'temporary-public-storage',
    },
  },
};
