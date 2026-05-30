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
├── assets/
│   ├── almar-logo-color.png   ← logo a color (header al hacer scroll + favicon)
│   ├── almar-logo-blanco.png  ← logo blanco (header sobre la foto + footer)
│   ├── hero.jpg               ← foto de fondo del inicio (convoy de contenedores)
│   └── nosotros.jpg           ← foto de la sección Nosotros (atardecer)
└── README.md
```

## Cómo editar lo más común
Todo está en `index.html`. Buscá el texto que querés cambiar y reemplazalo:

- **Teléfono / WhatsApp:** buscá `595971360672` (en los links wa.me) y `0971 360 672` (texto visible).
- **Email:** buscá `avaldz@almarserviciosfluviales.com.py`.
- **Años de experiencia:** buscá `+12` y `más de 12 años`.
- **Servicios:** sección `<section class="services"`, cada tarjeta es un `<div class="card ...">`.
- **Footer / datos legales:** buscá `RUC 7914978-2`.
- **Cambiar una foto:** reemplazá el archivo en `assets/` manteniendo el mismo nombre.

## Formulario de contacto (FormSubmit.co)
El formulario envía a `avaldz@almarserviciosfluviales.com.py`.
La PRIMERA vez que alguien envíe el formulario, FormSubmit manda un email de
activación a esa casilla. Hay que abrirlo y confirmar una sola vez; después
los mensajes llegan directo.

## Deploy
Conectado a Cloudflare Pages. Cada push a la rama `main` republica el sitio
automáticamente en ~30 segundos. No requiere build (es estático).
