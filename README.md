# CodexTest

## Laser Stack Layout Script

This repository contains the `updateStackLayout(padding)` ExtendScript helper for Adobe Illustrator. It spaces items with a space-between layout inside a selected group while centering them vertically.

## CEP Extension Packaging

To load this as a CEP panel in Illustrator, create the following folder structure inside your extensions directory (e.g., `~/Library/Application Support/Adobe/CEP/extensions` on macOS or `C:\Program Files (x86)\Common Files\Adobe\CEP\extensions` on Windows):

```
com.myname.laserstack/
├─ CSXS/
│  └─ manifest.xml
├─ index.html             # Panel entry point referenced by the manifest
├─ main.js                # Panel controller logic
└─ jsx/
   └─ stackLayout.jsx     # This script file
```

Use the provided `CSXS/manifest.xml` as-is to define the Illustrator host range and a fixed 200x400 panel size. Point `index.html` to your UI and have it load `jsx/stackLayout.jsx` through your preferred CEP bridge.
