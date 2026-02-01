// Service Worker для ZooBozor PWA
// Версия кэша - измени при обновлении
const CACHE_VERSION = 'zoobozor-v1.0.0';
const CACHE_NAME = `zoobozor-cache-${CACHE_VERSION}`;

// Критичные ресурсы для кэширования (офлайн)
const STATIC_ASSETS = [
  '/',
  '/static/img/icon-192.png',
  '/static/img/icon-512.png'
];

// Установка Service Worker
self.addEventListener('install', (event) => {
  console.log('[SW] Установка Service Worker...');
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Кэширование статических ресурсов');
      return cache.addAll(STATIC_ASSETS).catch(err => {
        console.warn('[SW] Не удалось закэшировать некоторые ресурсы:', err);
      });
    })
  );
  
  // Активировать новый SW сразу
  self.skipWaiting();
});

// Активация Service Worker
self.addEventListener('activate', (event) => {
  console.log('[SW] Активация Service Worker...');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          // Удаляем старые версии кэша
          if (cacheName !== CACHE_NAME) {
            console.log('[SW] Удаление старого кэша:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Взять контроль над всеми клиентами
  return self.clients.claim();
});

// Fetch Strategy: Network First, затем Cache (для динамического контента)
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
        
        return fetch(fetchRequest).then((response) => {
          // Check if valid response
          if (!response || response.status !== 200 || response.type !== 'basic') {
            return response;
          }
          
          // Clone the response
          const responseToCache = response.clone();
          
          // Cache static assets only
          if (event.request.url.includes('/static/')) {
            caches.open(CACHE_NAME)
              .then((cache) => {
                cache.put(event.request, responseToCache);
              });
          }
          
          return response;
        });
      })
      .catch(() => {
        // Return offline page if available
        return caches.match('/');
      })
  );
});
