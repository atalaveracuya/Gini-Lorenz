# Datasets públicos de imágenes de dron (para descargar)

> Enlaces encontrados en buscadores (octubre 2026). El entorno donde se generó esta lista bloquea
> la red y no se pudo abrir ninguna página. **Revise cada enlace en el navegador antes de descargar
> y confirme la licencia.**

## A. Mango desde dron (prioridad)

| # | Dataset | Enlace | Contenido | Notas |
|---|---|---|---|---|
| 1 | Drone空拍分析影像_芒果 (NYCU, Taiwán) | https://scidm.nchc.org.tw/en/dataset/activity/drone_mango · https://ark.nchc.org.tw/dataset/showcases/drone_mango | `drone_mango.zip`, imágenes de dron de mango | Licencia de datos abiertos del gobierno de Taiwán. Contenido no verificado. **Descargar primero** |
| 2 | Harumanis Mango Leaves and UAV Treetop Imagery (UiTM, Malasia) | https://data.mendeley.com/datasets/cyrwscvwsy/1 | Copas de 140 árboles de mango en 12,6 ha, UAV multiespectral (incluye RGB) | Artículo sobre segmentación de copas de mango con watershed, DOI 10.37934/araset.55.1.4462 |
| 3 | Roboflow: mangotrees | https://universe.roboflow.com/proj-pgxao/mangotrees | Clase "tree" | CC BY 4.0, exporta a YOLO/COCO (requiere cuenta gratuita) |
| 4 | Roboflow: mango-trees | https://universe.roboflow.com/nipunwaas/mango-trees | Árboles de mango | MIT |
| 5 | Roboflow: mango-flyers | https://universe.roboflow.com/mango-flyers | ~250 imágenes, segmentación de árbol | Revisar si son cenitales |
| 6 | Mango Orchard Aerial Image Dataset (India) | https://arccjournals.com/journal/agricultural-science-digest/D-6385 | 3.917 imágenes de DJI Air 2S, cajas YOLO de árbol | DOI 10.18805/ag.D-6385. Buscar el enlace a los datos en el artículo |
| 7 | MangoUAV Video Dataset | https://ieee-dataport.org/documents/mangouav-video-dataset | Videos de dron para detectar **frutos** de mango | Puede requerir cuenta de IEEE |

**Sin datos públicos (se pueden pedir por correo a los autores):**
- Mango Tree Net: https://arxiv.org/pdf/1907.06915
- Copas de mango en Pakistán (YOLOv7 + SAM, ortomosaico a 3 cm): https://www.mdpi.com/2072-4292/16/17/3207
- Sarron et al. 2018 (Senegal): https://agritrop.cirad.fr/589655
- Plantation Monitoring Using Drone Images (incluye mango, India): https://arxiv.org/abs/2502.08233

## B. Frutales y copas de árboles desde dron (respaldo y preentrenamiento)

| # | Dataset | Enlace | Contenido | Licencia |
|---|---|---|---|---|
| 1 | OAM-TCD (Restor/ETH) | https://zenodo.org/record/11617167 · Hugging Face `restor/tcd` | 5.072 teselas RGB a 10 cm, más de 280k copas (COCO) y modelos ya entrenados | no confirmada |
| 2 | OliveTreeCrownsDb (olivo) | https://data.mendeley.com/datasets/xym8rd2srf/3 | Phantom 4 RTK a 1,78 cm, copas anotadas, DEM | no confirmada |
| 3 | Avo-AirDB (palto) | https://data.mendeley.com/datasets/tvhh83r3hj/2 | ~985 fotos RGB, 113 ha | CC BY 4.0 |
| 4 | UAV olivo, albaricoque y viñedo | https://data.mendeley.com/datasets/r4w3b2mfnw | Fotos, ortomosaicos y anotaciones | no confirmada |
| 5 | ReforesTree (Ecuador: cacao, banano, cítricos) | https://zenodo.org/record/6813783 | 100 fotos a 2 cm, 4.600 cajas de copa (7,5 GB) | "free for use" |
| 6 | Oil Palm Anomaly (**Perú**: UTP y UNTRM) | https://data.mendeley.com/datasets/nh7d23dgnw | Fotos de palma aceitera con cajas | no confirmada |
| 7 | Palm-Tree-Dataset | https://github.com/Nour093/Palm-Tree-Dataset | Fotos de dron con cajas (VOC/YOLO) | no confirmada |
| 8 | NeonTreeEvaluation | https://zenodo.org/record/5914554 | 30k cajas RGB a 10 cm (avión, bosque) | CC BY 4.0 |

## B2. Otros en Mendeley Data (búsqueda del 09/10/2026)

- Coconut tree crown: https://data.mendeley.com/datasets/w4t73tvrf8/1 (copas de cocotero; contenido no confirmado)
- Aerial images (UAV) of burned and unburned olive trees: https://data.mendeley.com/datasets/83kpndkrb2/1 (3.624 imágenes de dron, CC BY-NC-ND)
- Avocado-DB: https://data.mendeley.com/datasets/b2d83zft4s/1 (no se confirmó si las imágenes son aéreas)

## C. Frutos de mango desde tierra (no son de dron)

- Mango Dataset: https://data.mendeley.com/datasets/gcgrjvwmm2/1 (1.025 imágenes con etiquetas en vistas Single, Proximal y Far-Field)
- Temporal Mango fruit Dataset: https://data.mendeley.com/datasets/9sb2rbn2g5/1 (~21.000 fotos de árboles de mango tomadas con celular a 2–3 m)

- MangoYOLO (CQU): https://acquire.cqu.edu.au/articles/dataset/MangoYOLO_data_set/13450661 (1.730 imágenes en formato VOC, CC BY 4.0)
- CQU On-tree mango instance segmentation: https://acquire.cqu.edu.au/articles/dataset/On-tree_mango_instance_segmentation_dataset/21655628
- MangoNet: https://datasetninja.com/mangonet-semantic-dataset
