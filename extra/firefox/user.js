// --- OPTIMASI SCROLLING MACOS & TOUCHSCREEN DELL LATITUDE 7210 ---
// Profil: Fluid macOS Trackpad & Smooth Wheel Scrolling

// 1. Sinkronisasi Hardware VSync & APZ Physics (Mulus 60Hz tanpa micro-stutter)
user_pref("layout.frame_rate", -1); // Auto-sync dengan hardware display refresh rate (VSync)
user_pref("general.smoothScroll", true);
user_pref("general.smoothScroll.msdPhysics.enabled", true); // Natural Mass-Spring-Damper physics seperti macOS native
user_pref("apz.overscroll.enabled", true); // Native macOS rubber-band bounce effect

// 2. Reset Sensitivitas & Akselerasi Scroll (Menghilangkan loncatan patah-patah)
user_pref("mousewheel.min_line_scroll_amount", 5);
user_pref("mousewheel.acceleration.factor", -1);
user_pref("mousewheel.acceleration.start", -1);
user_pref("mousewheel.default.delta_multiplier_y", 100);

// 3. Reset Momentum APZ ke Standar yang Halus
user_pref("apz.fling_friction", "0.002");
user_pref("apz.max_velocity_inches_per_ms", "-1.0");
user_pref("apz.fling_accel_interval", 0);

// 4. Layar Sentuh Tablet (Touchscreen W3C Gestures)
user_pref("dom.w3c_touch_events.enabled", 1);
user_pref("apz.touch_start_tolerance", "0.03");

// 5. Akselerasi Grafis Metal & WebRender
user_pref("gfx.webrender.all", true);
user_pref("gfx.canvas.accelerated", true);
user_pref("gfx.webrender.compositor", true);
user_pref("gfx.webrender.compositor.force-enabled", false);
user_pref("gfx.webrender.layer-compositor", false);
user_pref("layers.acceleration.force-enabled", false);

// 6. Efisiensi RAM
user_pref("browser.tabs.unloadOnLowMemory", true);

// 7. Eliminasi Lag Peluncuran Awal (Lazy Tab Loading)
user_pref("browser.sessionstore.restore_on_demand", true);
user_pref("browser.sessionstore.restore_pinned_tabs_on_demand", true);
user_pref("browser.sessionstore.interval", 60000);

// 8. Nonaktifkan Telemetri Startup & Polling Mozilla
user_pref("toolkit.telemetry.enabled", false);
user_pref("toolkit.telemetry.unified", false);
user_pref("experiments.activeExperiment", false);
user_pref("experiments.supported", false);
user_pref("app.normandy.enabled", false);
user_pref("app.shield.optoutstudies.enabled", false);

// 9. Paksa Native H.264 Hardware Acceleration (Intel QuickSync GPU)
user_pref("media.hardware-video-decoding.enabled", true);
user_pref("media.hardware-video-decoding.force-enabled", true);
user_pref("media.webm.enabled", false); // Matikan WebM container agar semua web (YouTube dsb) wajib fallback ke MP4/H.264
user_pref("media.mediasource.vp9.enabled", false); // Matikan VP9 (karena macOS VideoToolbox tidak support VP9 di UHD 620)
user_pref("media.av1.enabled", false); // Matikan AV1 (karena UHD 620 tidak memiliki hardware AV1)
user_pref("media.webrtc.hw.h264.enabled", true);

// 10. Multi-Process & Content Process Tuning (Sesuaikan dengan 4 Core Fisik i7-10610U)
user_pref("dom.ipc.processCount", 4);
user_pref("dom.ipc.processCount.webIsolated", 4);
user_pref("image.mem.decode_bytes_at_a_time", 262144);
user_pref("image.async_decode.enabled", true);

// 11. Native WebRender Compositor & Cache
user_pref("browser.cache.memory.capacity", 1048576);
user_pref("network.http.max-connections", 1500);
user_pref("network.http.max-persistent-connections-per-server", 10);

// 12. Optimasi Smooth Scrolling untuk Halaman Media Berat (Anti-Lag Video & Gambar)
user_pref("media.autoplay.default", 5); // Blokir video berputar otomatis diam-diam saat scroll
user_pref("media.autoplay.blocking_policy", 2);
user_pref("media.block-autoplay-until-in-foreground", true);
user_pref("layout.css.backdrop-filter.enabled", false); // Matikan blur kaca berat di web agar iGPU 620 tetap 60 FPS
user_pref("dom.image-lazy-loading.enabled", true);
