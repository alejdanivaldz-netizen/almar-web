# ALMAR Servicios Fluviales — Web institucional

Sitio web institucional de ALMAR Servicios Fluviales (agencia marítima, Paraguay).

## Stack
- HTML5 + CSS3 + JavaScript vanilla (sin frameworks, sin backend)
- Formulario de contacto vía FormSubmit.co
- Hosting: Cloudflare Pages
- Dominio: almarserviciosfluviales.com.py

## Estructura
```
almar-web/
├── index.html              ← toda la página (estructura, estilos y scripts)
├── gracias.html            ← página que se muestra después de enviar el formulario
├── assets/
│   ├── almar-logo-color.png   ← logo a color, 340px (header al hacer scroll, gracias.html)
│   ├── almar-logo-blanco.png  ← logo blanco, 340px (header sobre la foto + footer)
│   ├── favicon-32.png / favicon-192.png / apple-touch-icon.png  ← íconos de pestaña/celular
│   ├── hero-1600.webp         ← foto de fondo del inicio (escritorio)
│   ├── hero-960.webp          ← foto de fondo del inicio (celular)
│   ├── hero.jpg               ← respaldo para navegadores viejos + imagen al compartir en redes
│   ├── nosotros-1024.webp / nosotros-640.webp  ← foto de la sección Nosotros
│   └── nosotros.jpg           ← respaldo de la anterior
└── README.md
```

## Cómo editar lo más común
Todo está en `index.html`. Buscá el texto que querés cambiar y reemplazalo:

- **Teléfono / WhatsApp:** buscá `595971360672` (en los links wa.me) y `0971 360 672` (texto visible).
- **Email:** buscá `avaldz@almarserviciosfluviales.com.py`.
- **Años de experiencia:** buscá `+12` y `más de 12 años`.
- **Servicios:** sección `<section class="services"`, cada tarjeta es un `<div class="card ...">`.
- **Footer / datos legales:** buscá `RUC 7914978-2`.
- **Mapa de zonas:** es un SVG generado con `tools/make_map.py` a partir de límites oficiales
  (ver `tools/README.md`). Los pines se posicionan en % (`.map-pin`), valores en `pins.json`.
- **Cambiar una foto:** cada foto existe en varias versiones (`.webp` en dos tamaños + `.jpg`).
  Lo más simple es pedirle a Claude que la reemplace pasándole la foto nueva; genera
  todas las versiones y las deja con los mismos nombres.

## Formulario de contacto (FormSubmit.co)
El formulario envía a `avaldz@almarserviciosfluviales.com.py`.
La PRIMERA vez que alguien envíe el formulario, FormSubmit manda un email de
activación a esa casilla. Hay que abrirlo y confirmar una sola vez; después
los mensajes llegan directo.

## Rendimiento (qué NO tocar sin motivo)
- Las fotos se sirven en WebP con `<picture>`; el celular recibe una versión más liviana.
- Todas las `<img>` tienen `width`/`height` para que la página no salte mientras carga.
- Solo se cargan los pesos de fuente que se usan (Oswald 700, Barlow Condensed 600/700, Inter 400/500).
- Las animaciones respetan `prefers-reduced-motion` y usan solo `transform`/`opacity`.

## Deploy
Conectado a Cloudflare Pages. Cada push a la rama `main` republica el sitio
automáticamente en ~30 segundos. No requiere build (es estático).
