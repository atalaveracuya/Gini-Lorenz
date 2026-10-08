# Bibliografía indexada de respaldo

Organizada por tarea. Para cada trabajo se indica **qué respalda** en la metodología o el código.
Las revistas citadas están indexadas en Scopus y/o Web of Science (Q1–Q2 en su mayoría).

> **Verificación:** las referencias marcadas con ✔ se confirmaron con búsquedas web
> durante la elaboración (autores, revista, volumen y DOI). El resto proviene de
> conocimiento bibliográfico estándar del área. **Antes de citar en una tesis o artículo,
> verifique cada DOI en https://doi.org o en Scopus/WoS.**

---

## Tarea 1: Identificar el cultivo (mango) en imágenes de dron

### Mango y frutales con UAV (antecedentes directos)

1. ✔ **Sarron, J., Malézieux, É., Sané, C. A. B., & Faye, É. (2018).** Mango yield mapping at the orchard scale based on tree structure and land cover assessed by UAV. *Remote Sensing, 10*(12), 1900. https://doi.org/10.3390/rs10121900
   *Respalda:* identificar copas de mango con fotogrametría UAV + OBIA (análisis de imagen basado en objetos), clasificar especie/cultivar (exactitud global 0,89) y usar la estructura de la copa (altura, área, volumen) como descriptor. Es el antecedente más cercano a las tareas 1 y 3.

2. ✔ **Csillik, O., Cherbini, J., Johnson, R., Lyons, A., & Kelly, M. (2018).** Identification of citrus trees from Unmanned Aerial Vehicle imagery using convolutional neural networks. *Drones, 2*(4), 39. https://doi.org/10.3390/drones2040039
   *Respalda:* identificar árboles frutales individuales en imágenes UAV (CNN + refinamiento con superpíxeles SLIC; exactitud 96 %).

3. **Torres-Sánchez, J., López-Granados, F., Serrano, N., Arquero, O., & Peña, J. M. (2015).** High-throughput 3-D monitoring of agricultural-tree plantations with Unmanned Aerial Vehicle (UAV) technology. *PLoS ONE, 10*(6), e0130479. https://doi.org/10.1371/journal.pone.0130479
   *Respalda:* segmentar copas en plantaciones arbóreas con OBIA a partir de imágenes UAV y medir área y volumen de copa.

4. ✔ **Gurumurthy, V. A., Kestur, R., & Narasipura, O. (2019).** Mango Tree Net: A fully convolutional network for semantic segmentation and individual crown detection of mango trees. *arXiv:1907.06915* (preprint; el mismo grupo publicó después MangoGAN en *Journal of Applied Remote Sensing*, 16(1), 014527, 2022).
   *Respalda:* segmentar copas de mango en imágenes UAV y separar copas que se tocan.

### Segmentación de vegetación y copas (OBIA)

5. **Blaschke, T. (2010).** Object based image analysis for remote sensing. *ISPRS Journal of Photogrammetry and Remote Sensing, 65*(1), 2–16. https://doi.org/10.1016/j.isprsjprs.2009.06.004
   *Respalda:* el paradigma OBIA, que trabaja con objetos (copas) en lugar de píxeles (`segmentacion.py`, `caracteristicas.py`).

6. **Torres-Sánchez, J., López-Granados, F., & Peña, J. M. (2015).** An automatic object-based method for optimal thresholding in UAV images: Application for vegetation detection in herbaceous crops. *Computers and Electronics in Agriculture, 114*, 43–52. https://doi.org/10.1016/j.compag.2015.03.019
   *Respalda:* separar vegetación del suelo con un umbral automático (Otsu) sobre índices RGB en imágenes UAV.

7. **Otsu, N. (1979).** A threshold selection method from gray-level histograms. *IEEE Transactions on Systems, Man, and Cybernetics, 9*(1), 62–66. https://doi.org/10.1109/TSMC.1979.4310076
   *Respalda:* `filters.threshold_otsu`, el umbral automático de vegetación.

8. **Vincent, L., & Soille, P. (1991).** Watersheds in digital spaces: An efficient algorithm based on immersion simulations. *IEEE Transactions on Pattern Analysis and Machine Intelligence, 13*(6), 583–598. https://doi.org/10.1109/34.87344
   *Respalda:* separar copas contiguas con watershed sobre la transformada de distancia.

### Índices de vegetación RGB/NIR

9. **Woebbecke, D. M., Meyer, G. E., Von Bargen, K., & Mortensen, D. A. (1995).** Color indices for weed identification under various soil, residue, and lighting conditions. *Transactions of the ASAE, 38*(1), 259–269. https://doi.org/10.13031/2013.27838 (índice ExG)
10. **Meyer, G. E., & Neto, J. C. (2008).** Verification of color vegetation indices for automated crop imaging applications. *Computers and Electronics in Agriculture, 63*(2), 282–293. https://doi.org/10.1016/j.compag.2008.03.009 (índice ExG−ExR)
11. **Gitelson, A. A., Kaufman, Y. J., Stark, R., & Rundquist, D. (2002).** Novel algorithms for remote estimation of vegetation fraction. *Remote Sensing of Environment, 80*(1), 76–87. https://doi.org/10.1016/S0034-4257(01)00289-9 (índice VARI)
12. **Louhaichi, M., Borman, M. M., & Johnson, D. E. (2001).** Spatially located platform and aerial photography for documentation of grazing impacts on wheat. *Geocarto International, 16*(1), 65–70. https://doi.org/10.1080/10106040108542184 (índice GLI)

### Textura (follaje denso y fino del mango frente a otras especies)

13. **Haralick, R. M., Shanmugam, K., & Dinstein, I. (1973).** Textural features for image classification. *IEEE Transactions on Systems, Man, and Cybernetics, SMC-3*(6), 610–621. https://doi.org/10.1109/TSMC.1973.4309314 (GLCM)
14. **Ojala, T., Pietikäinen, M., & Mäenpää, T. (2002).** Multiresolution gray-scale and rotation invariant texture classification with local binary patterns. *IEEE TPAMI, 24*(7), 971–987. https://doi.org/10.1109/TPAMI.2002.1017623 (LBP)

---

## Tarea 2: Entrenar el modelo (machine learning y deep learning)

### Machine learning clásico (`tarea2_entrenar.py`)

15. **Breiman, L. (2001).** Random forests. *Machine Learning, 45*, 5–32. https://doi.org/10.1023/A:1010933404324
16. **Belgiu, M., & Drăguţ, L. (2016).** Random forest in remote sensing: A review of applications and future directions. *ISPRS Journal of Photogrammetry and Remote Sensing, 114*, 24–31. https://doi.org/10.1016/j.isprsjprs.2016.01.011
    *Respalda:* RF como clasificador de referencia en teledetección (robusto, pocas muestras, importancia de variables).
17. **Cortes, C., & Vapnik, V. (1995).** Support-vector networks. *Machine Learning, 20*, 273–297. https://doi.org/10.1007/BF00994018
18. **Mountrakis, G., Im, J., & Ogole, C. (2011).** Support vector machines in remote sensing: A review. *ISPRS Journal of Photogrammetry and Remote Sensing, 66*(3), 247–259. https://doi.org/10.1016/j.isprsjprs.2010.11.001
19. **Friedman, J. H. (2001).** Greedy function approximation: A gradient boosting machine. *Annals of Statistics, 29*(5), 1189–1232. https://doi.org/10.1214/aos/1013203451

### Validación y métricas

20. **Roberts, D. R., Bahn, V., Ciuti, S., et al. (2017).** Cross-validation strategies for data with temporal, spatial, hierarchical, or phylogenetic structure. *Ecography, 40*(8), 913–929. https://doi.org/10.1111/ecog.02881
21. **Ploton, P., Mortier, F., Réjou-Méchain, M., et al. (2020).** Spatial validation reveals poor predictive performance of large-scale ecological mapping models. *Nature Communications, 11*, 4540. https://doi.org/10.1038/s41467-020-18321-y
    *Respaldan (20–21):* la validación cruzada **espacial por bloques**. Con k-fold aleatorio, copas vecinas y casi idénticas caen en entrenamiento y prueba a la vez, y el desempeño parece mejor de lo que es.
22. **Congalton, R. G. (1991).** A review of assessing the accuracy of classifications of remotely sensed data. *Remote Sensing of Environment, 37*(1), 35–46. https://doi.org/10.1016/0034-4257(91)90048-B (matriz de confusión, exactitud, kappa)

### Deep learning (`yolo_mango.py`)

23. **Kamilaris, A., & Prenafeta-Boldú, F. X. (2018).** Deep learning in agriculture: A survey. *Computers and Electronics in Agriculture, 147*, 70–90. https://doi.org/10.1016/j.compag.2018.02.016
24. **Koirala, A., Walsh, K. B., Wang, Z., & McCarthy, C. (2019).** Deep learning – Method overview and review of use for fruit detection and yield estimation. *Computers and Electronics in Agriculture, 162*, 219–234. https://doi.org/10.1016/j.compag.2019.04.017
25. **Ma, L., Liu, Y., Zhang, X., Ye, Y., Yin, G., & Johnson, B. A. (2019).** Deep learning in remote sensing applications: A meta-analysis and review. *ISPRS Journal of Photogrammetry and Remote Sensing, 152*, 166–177. https://doi.org/10.1016/j.isprsjprs.2019.04.015
26. **Redmon, J., Divvala, S., Girshick, R., & Farhadi, A. (2016).** You Only Look Once: Unified, real-time object detection. *Proc. IEEE CVPR*, 779–788. https://doi.org/10.1109/CVPR.2016.91
27. **Ren, S., He, K., Girshick, R., & Sun, J. (2017).** Faster R-CNN: Towards real-time object detection with region proposal networks. *IEEE TPAMI, 39*(6), 1137–1149. https://doi.org/10.1109/TPAMI.2016.2577031
28. **Ronneberger, O., Fischer, P., & Brox, T. (2015).** U-Net: Convolutional networks for biomedical image segmentation. *MICCAI 2015, LNCS 9351*, 234–241. https://doi.org/10.1007/978-3-319-24574-4_28
29. **Weinstein, B. G., Marconi, S., Bohlman, S., Zare, A., & White, E. (2019).** Individual tree-crown delineation in RGB imagery using semi-supervised deep learning neural networks. *Remote Sensing, 11*(11), 1309. https://doi.org/10.3390/rs11111309 (DeepForest)
30. ✔ **Kestur, R., Meduri, A., & Narasipura, O. (2019).** MangoNet: A deep semantic segmentation architecture for a method to detect and count mangoes in an open orchard. *Engineering Applications of Artificial Intelligence, 77*, 59–69. https://doi.org/10.1016/j.engappai.2018.09.011
31. **Sa, I., Ge, Z., Dayoub, F., Upcroft, B., Perez, T., & McCool, C. (2016).** DeepFruits: A fruit detection system using deep neural networks. *Sensors, 16*(8), 1222. https://doi.org/10.3390/s16081222
32. **Bargoti, S., & Underwood, J. (2017).** Deep fruit detection in orchards. *Proc. IEEE ICRA*, 3626–3633. https://doi.org/10.1109/ICRA.2017.7989417 (incluye un conjunto de datos de mango)

---

## Tarea 3: Detectar y contar mangos en imágenes nuevas, con estadísticas

### Conteo de mango (árbol / fruto) con visión artificial

33. **Koirala, A., Walsh, K. B., Wang, Z., & McCarthy, C. (2019).** Deep learning for real-time fruit detection and orchard fruit load estimation: Benchmarking of 'MangoYOLO'. *Precision Agriculture, 20*, 1107–1135. https://doi.org/10.1007/s11119-019-09642-0
    *Respalda:* detector YOLO adaptado a mango y estimación de carga de fruta por huerta.
34. ✔ **Xiong, J., Liu, Z., Chen, S., Liu, B., Zheng, Z., Zhong, Z., Yang, Z., & Peng, H. (2020).** Visual detection of green mangoes by an unmanned aerial vehicle in orchards based on a deep learning method. *Biosystems Engineering, 194*, 261–272. https://doi.org/10.1016/j.biosystemseng.2020.04.006
    *Respalda:* conteo de mango **desde dron** con YOLOv2 (precisión 96,1 %, recall 89,0 %, error de conteo 1,1 % en 10 árboles). Los autores y el año se confirmaron en AGRIS/FAO; revista, volumen y DOI deben verificarse.
35. **Stein, M., Bargoti, S., & Underwood, J. (2016).** Image based mango fruit detection, localisation and yield estimation using multiple view geometry. *Sensors, 16*(11), 1915. https://doi.org/10.3390/s16111915
36. **Payne, A. B., Walsh, K. B., Subedi, P. P., & Jarvis, D. (2013).** Estimation of mango crop yield using image analysis – Segmentation method. *Computers and Electronics in Agriculture, 91*, 57–64. https://doi.org/10.1016/j.compag.2012.11.009
37. ✔ **Wang, Z., Walsh, K. B., & Verma, B. (2017).** On-tree mango fruit size estimation using RGB-D images. *Sensors, 17*(12), 2738. https://doi.org/10.3390/s17122738
38. **Anderson, N. T., Walsh, K. B., & Wulfsohn, D. (2021).** Technologies for forecasting tree fruit load and harvest timing—From ground, sky and time. *Agronomy, 11*(7), 1409. https://doi.org/10.3390/agronomy11071409 (revisión: conteo desde tierra, dron y satélite)
39. ✔ **Birla, L., Bharadwaj, A., Jain, R., Deb, C. K., Sehgal, V. K., & Ramasubramanian, V. (2025).** Mango (*Mangifera indica*) tree detection and counting in mango orchard with satellite images using deep learning model YOLO: A comparative analysis. *Indian Journal of Agricultural Sciences, 95*(6), 678–683. https://doi.org/10.56093/ijas.v95i6.161451
    *Respalda:* comparación de YOLOv5–v8 para contar **árboles de mango** (YOLOv8 obtuvo el mejor resultado). Usa imágenes satelitales, no de dron.

### Conteo de árboles con UAV (otros cultivos, misma metodología)

40. ✔ **Osco, L. P., de Arruda, M. dos S., Marcato Junior, J., et al. (2020).** A convolutional neural network approach for counting and geolocating citrus-trees in UAV multispectral imagery. *ISPRS Journal of Photogrammetry and Remote Sensing, 160*, 97–106. https://doi.org/10.1016/j.isprsjprs.2019.12.010
    *Respalda:* contar y geolocalizar árboles con UAV y validar con métricas de conteo (MAE, precisión, recall, F1) sobre 37 353 árboles.
41. ✔ **Neupane, B., Horanont, T., & Hung, N. D. (2019).** Deep learning based banana plant detection and counting using high-resolution red-green-blue (RGB) images collected from unmanned aerial vehicle (UAV). *PLoS ONE, 14*(10), e0223906. https://doi.org/10.1371/journal.pone.0223906
    *Respalda:* efecto de la **altura de vuelo / GSD** sobre la detección (96,4 % a 40 m frente a 75,8 % a 60 m), útil para planificar el vuelo.

### Estadística espacial y de conteo

42. **Clark, P. J., & Evans, F. C. (1954).** Distance to nearest neighbor as a measure of spatial relationships in populations. *Ecology, 35*(4), 445–453. https://doi.org/10.2307/1931034 (índice de Clark-Evans en `tarea3_contar.py`)
43. **Efron, B., & Tibshirani, R. J. (1993).** *An Introduction to the Bootstrap.* Chapman & Hall/CRC. ISBN 978-0-412-04231-7 (intervalo de confianza del conteo)
44. **Kuhn, H. W. (1955).** The Hungarian method for the assignment problem. *Naval Research Logistics Quarterly, 2*(1–2), 83–97. https://doi.org/10.1002/nav.3800020109 (emparejamiento uno a uno entre detección y árbol de campo en la evaluación)

---

## Matriz tarea ↔ código ↔ referencias

| Tarea | Paso | Archivo | Referencias |
|---|---|---|---|
| 1 | Índices de vegetación RGB/NIR | `mango_uav/indices.py` | 9–12 |
| 1 | Máscara de vegetación (Otsu) y copas (watershed) | `mango_uav/segmentacion.py` | 3, 5–8 |
| 1 | Descriptores de forma, color y textura por copa | `mango_uav/caracteristicas.py` | 1, 13, 14 |
| 1 | Etiquetado con puntos GPS de campo | `mango_uav/utilidades.py` | 1, 40, 44 |
| 2 | RF / SVM / Gradient Boosting / regresión logística | `tarea2_entrenar.py` | 15–19 |
| 2 | Validación cruzada espacial y métricas | `tarea2_entrenar.py` | 20–22 |
| 2 | Detector YOLO (deep learning) | `yolo_mango.py` | 23–27, 29, 33 |
| 3 | Conteo, densidad, cobertura, tamaño de copa | `tarea3_contar.py` | 1, 33, 34, 38, 40 |
| 3 | Patrón espacial (Clark-Evans) e IC bootstrap | `tarea3_contar.py` | 42, 43 |
| 3 | Validación contra conteo de campo | `utilidades.evaluar_conteo` | 40, 41, 44 |
