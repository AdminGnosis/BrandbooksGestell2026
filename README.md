# GESTELL · Brand Operating System — Web

Static site wrapping the four GESTELL brandbook volumes with a unified
navigation chrome. Designed to be deployed to Vercel (or any static host).

## Contenido

```
.
├── index.html              # Landing / hub with the 4 volumes
├── vol-1.html              # Vol. I — ADN Estratégico (12 secs · 38 págs)
├── vol-2.html              # Vol. II — Arquitectura de Marca (7 secs · 25 págs)
├── vol-3.html              # Vol. III — Identidad Visual (9 secs · 110 págs)
├── vol-4.html              # Vol. IV — Identidad Verbal (7 secs · 50 págs)
├── assets/
│   ├── chrome.css          # Nav bar, drawer, mobile scaling
│   └── chrome.js           # Navigation behavior
├── vercel.json             # Vercel static config (clean URLs, caching)
└── README.md
```

**Nota:** el contenido original de cada volumen NO fue modificado. El
sistema sólo inyecta una barra superior fija, un cajón lateral con el
índice y un envoltorio para escalar las páginas A4 en pantallas móviles.

## Atajos de teclado

| Tecla      | Acción                           |
|------------|----------------------------------|
| `I`        | Abrir / cerrar índice            |
| `← / →`    | Volumen anterior / siguiente     |
| `Esc`      | Cerrar índice                    |
| `1`–`4`    | (Sólo en la portada) ir al Vol.  |

## Deploy en Vercel — 3 opciones

### Opción 1 · Drag-and-drop (más fácil)
1. Entra a [vercel.com/new](https://vercel.com/new).
2. Arrastra este folder (o el `.zip` descomprimido) al navegador.
3. Vercel detecta un proyecto estático. Click **Deploy**.
4. Listo. Te dan un URL tipo `gestell-xxxxx.vercel.app`.

### Opción 2 · CLI
```bash
npm i -g vercel
vercel --prod
```

### Opción 3 · GitHub + Vercel
1. Sube el folder a un repo de GitHub.
2. Entra a Vercel, **Import Project**, selecciona el repo.
3. Framework preset: **Other**. Build command: vacío. Output dir: `./`.
4. Deploy.

## Testing local

```bash
# Python 3
python3 -m http.server 8080
# o con npx
npx serve .
```

Abre `http://localhost:8080`.

## Responsive

- **Desktop (≥ 840 px):** páginas A4 a tamaño real con chrome superior.
- **Mobile (< 840 px):** las páginas A4 se escalan proporcionalmente al
  ancho del viewport usando `transform: scale()`. Reserva de altura
  calculada en JS para no romper el scroll-flow.
- Probado conceptualmente contra Samsung Galaxy S-series (360–412 px),
  iPhone SE (375 px) y tablets (768 px).

## Impresión

El chrome se oculta automáticamente con `@media print`. Los
`page-break-after: always` originales de cada volumen se respetan.

## Build

Si necesitas re-generar las páginas desde los HTML originales:

```bash
python3 build.py
```

El script:
- Lee los 4 HTML crudos desde `/mnt/project/`.
- Extrae los títulos de cada `section-title-page` (código, título, subtítulo).
- Inyecta IDs de ancla (`sec-0`, `sec-1`, …, `cover`).
- Añade `<link>` a `chrome.css` y `<script>` a `chrome.js` en el `<head>`.
- Embebe la configuración del volumen en `window.__GBOS__`.

---

**Confidencial · Uso Interno · 2026**
