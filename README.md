# GESTELL · Brand Operating System — Web

Static site wrapping the GESTELL brandbook volumes with a unified
navigation chrome. Designed to be deployed to Vercel (or any static host).

## Contenido

```
.
├── index.html              # Landing / hub con los 5 volúmenes
├── vol-1.html              # Vol. I  — ADN Estratégico         (12 secs ·  38 págs)
├── vol-2.html              # Vol. II — Arquitectura de Marca   ( 7 secs ·  25 págs)
├── vol-3.html              # Vol. III — Identidad Visual       ( 9 secs · 110 págs)
├── vol-4.html              # Vol. IV — Identidad Verbal        ( 7 secs ·  50 págs)
├── vol-6.html              # Vol. VI — Infraestructura Digital ( 8 secs · 120 págs) ★ NUEVO
├── assets/
│   ├── chrome.css          # Nav bar, drawer, mobile scaling
│   └── chrome.js           # Navigation behavior
├── vercel.json             # Vercel static config (clean URLs, caching)
├── build.py                # Regenerador no-destructivo (lee masters, escribe vol-N.html)
└── README.md
```

**Nota:** el contenido original de cada volumen NO se modifica. El
sistema sólo inyecta una barra superior fija, un cajón lateral con el
índice y un envoltorio para escalar las páginas A4 en pantallas móviles.

**Vol. V está reservado.** Los volúmenes en producción son I, II, III, IV y VI.
La numeración respeta el master del brandbook; el navegador del chrome
salta de IV a VI sin saltos visuales para el usuario final.

## Atajos de teclado

| Tecla      | Acción                                |
|------------|---------------------------------------|
| `I`        | Abrir / cerrar índice                 |
| `← / →`    | Volumen anterior / siguiente          |
| `Esc`      | Cerrar índice                         |
| `1`–`4`, `6` | (Sólo en la portada) ir al Vol.     |

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
  iPhone SE (375 px) y tablets (768 px). Verifica rendering real en
  el dispositivo después del deploy.

## Impresión

El chrome se oculta automáticamente con `@media print`. Los
`page-break-after: always` originales de cada volumen se respetan.

## Build (re-generar páginas desde el master)

Si necesitas re-generar las páginas desde los HTML originales:

```bash
python3 build.py            # regenera los 5 volúmenes
python3 build.py vol-6      # regenera sólo Vol. VI
```

El script:
- Lee los HTML crudos desde la misma carpeta donde vive `build.py`.
- Extrae títulos de cada `section-title-page` (código, título, subtítulo).
- Inyecta IDs de ancla (`sec-0`, `sec-1`, …, `cover`).
- Añade `<link>` a `assets/chrome.css` y `<script>` a `assets/chrome.js` antes de `</head>`.
- Embebe la configuración del volumen en `window.__GBOS__`.
- Vol. IV usa `<h2 class="stp__title">` en lugar de `<h1>` — el script lo respeta.
- Determinista: misma entrada ⇒ misma salida.

## Notas de la actualización Vol. VI

- **Color de chrome**: Vol. VI usa el acento DASEIN text-safe `#B99BD6`,
  el mismo que Vol. II. Los volúmenes se diferencian por su numeral y
  título en la barra de navegación. Si se requiere mayor distinción visual,
  ajustar `VOLUMES[vol-6].color` en `build.py` y re-generar.
- **Secciones ancladas vs. portada**: la portada del Vol. VI declara
  "14 SECCIONES" pero el master entregado contiene 8 portadillas
  (`section-title-page`). El chrome enlaza únicamente lo que existe en el
  DOM. Al añadir las 6 portadillas restantes en el master, basta correr
  `python3 build.py vol-6` para que el índice del cajón se actualice solo.

---

**Confidencial · Uso Interno · 2026**
