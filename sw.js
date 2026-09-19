/* 前のアプリの後片づけ用。自分自身を登録解除し、保存していたキャッシュを全部消す。 */
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", (e) => {
  e.waitUntil((async () => {
    const keys = await caches.keys();
    await Promise.all(keys.map((k) => caches.delete(k)));
    await self.registration.unregister();
    const clients = await self.clients.matchAll({ type: "window" });
    for (const c of clients) c.navigate(c.url);
  })());
});
