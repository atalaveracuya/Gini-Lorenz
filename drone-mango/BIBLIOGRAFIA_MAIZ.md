# Bibliografía por tarea: MAÍZ (cultivo con más estudios replicables)

**Por qué maíz:** de los 10 cultivos principales (arroz cáscara, maíz amarillo duro, papa,
avena forrajera, maíz amiláceo, maíz chala, quinua, trigo, maíz choclo y caña de azúcar), el
maíz ocupa 4 líneas y es, con diferencia, el cultivo con más estudios indexados de dron + deep
learning para identificar, entrenar y **contar** (plántulas y panojas). Tiene además datasets
públicos para replicar y antecedentes en Perú. Le siguen arroz y trigo, que se estudian sobre
todo por conteo de espigas y panículas. Para papa, quinua, avena y caña hay muy pocos estudios
de conteo con dron.

Búsqueda del 09/10/2026. ✔ = autores, revista y DOI confirmados en búsqueda web;
◐ = datos parciales. Verifique cada DOI en https://doi.org antes de citar.

## Tarea 1: Identificar el cultivo (maíz) en imágenes de dron
1. ✔ Trujillano, F., Gonzalez, G., Saito, C., Flores, A., & Racoceanu, D. (2021). Corn crops identification using multispectral images from unmanned aircraft systems. *IGARSS 2021*, 4712–4715. https://doi.org/10.1109/IGARSS47720.2021.9553826 (**Áncash, Perú**: segmentación U-Net con Dice de 81,5 %)
2. ✔ Saravia, D., Salazar, W., Valqui-Valqui, L., Quille-Mamani, J., Porras-Jorge, R., Corredor, F.-A., Barboza, E., Vásquez, H. V., Casas Diaz, A. V., & Arbizu, C. I. (2022). Yield predictions of four hybrids of maize (*Zea mays*) using multispectral images obtained from UAV in the Coast of Peru. *Agronomy, 12*(11), 2630. https://doi.org/10.3390/agronomy12112630 (**INIA, Perú**)
3. ✔ Xu, X., Wang, L., Shu, M., Liang, X., Ghafoor, A. Z., Liu, Y., Ma, Y., & Zhu, J. (2022). Detection and counting of maize leaves based on two-stage deep learning with UAV-based RGB image. *Remote Sensing, 14*(21), 5388. https://doi.org/10.3390/rs14215388 (Mask R-CNN separa la planta del fondo)
4. ◐ Revisión: Deep learning models for the classification of crops in aerial imagery: A review. *Agriculture, 13*(5), 965 (2023). https://doi.org/10.3390/agriculture13050965

## Tarea 2: Entrenar el modelo
5. ✔ Jia, Z., Zhang, X., Yang, H., Lu, Y., Liu, J., Yu, X., Feng, D., Gao, K., Xue, J., Ming, B., Nie, C., & Li, S. (2024). Comparison and optimal method of detecting the number of maize seedlings based on deep learning. *Drones, 8*(5), 175. https://doi.org/10.3390/drones8050175 (YOLOv8n, YOLOv5n, Faster R-CNN, DETR; distintas alturas de vuelo)
6. ✔ Lu, C., Nnadozie, E., Camenzind, M. P., Hu, Y., & Yu, K. (2024). Maize plant detection using UAV-based RGB imaging and YOLOv5. *Frontiers in Plant Science, 14*, 1274813. https://doi.org/10.3389/fpls.2023.1274813 (etiquetado semiautomático con SAM)
7. ✔ David, E., Daubige, G., Joudelat, F., Burger, P., Comar, A., de Solan, B., & Baret, F. (2022). Plant detection and counting from high-resolution RGB images acquired from UAVs: comparison between deep-learning and handcrafted methods with application to maize, sugar beet, and sunflower. *bioRxiv*. https://doi.org/10.1101/2021.04.27.441631 (preprint; **16.247 plantas etiquetadas en Zenodo 4890370**)
8. ✔ Pu, H., Chen, X., Yang, Y., Tang, R., Luo, J., Wang, Y., & Mu, J. (2023). Tassel-YOLO: A new high-precision and real-time method for maize tassel detection and counting based on UAV aerial images. *Drones, 7*(8), 492. https://doi.org/10.3390/drones7080492
9. ◐ Feng, Nie & Li (2025). Field-deployable lightweight YOLOv8n for real-time detection and counting of maize seedlings using UAV RGB imagery. *Frontiers in Plant Science*. https://doi.org/10.3389/fpls.2025.1639533

## Tarea 3: Detectar y contar plantas de maíz, con estadísticas
10. ✔ Wang, B., Zhou, J., Costa, M., Kaeppler, S. M., & Zhang, Z. (2023). Plot-level maize early stage stand counting and spacing detection using advanced deep learning algorithms based on UAV imagery. *Agronomy, 13*(7), 1728. https://doi.org/10.3390/agronomy13071728 (conteo con R² = 0,936 y **variabilidad del espaciamiento entre plantas**)
11. ✔ Li, Y., Bao, Z., & Qi, J. (2022). Seedling maize counting method in complex backgrounds based on YOLOV5 and Kalman filter tracking algorithm. *Frontiers in Plant Science, 13*, 1030962. https://doi.org/10.3389/fpls.2022.1030962 (R² = 0,92 frente al conteo manual)
12. ✔ Pu et al. (2023), referencia 8: conteo de panojas con 97,55 % de exactitud.
13. ✔ Jia et al. (2024), referencia 5: efecto de la densidad de siembra, la etapa y la altura de vuelo sobre el conteo.
14. ◐ Detection and identification of tassel states at different maize tasseling stages using UAV imagery and deep learning (2024). *Plant Phenomics*. https://doi.org/10.34133/plantphenomics.0188

## Datos públicos para replicar
- Zenodo 4890370: plántulas de maíz, remolacha y girasol desde dron, 16.247 plantas etiquetadas (David et al.): https://zenodo.org/records/4890370
- Dataset MTC (Maize Tassel Counting) de TasselNet: Lu, H., et al. (2017), *Plant Methods* 13:79 (fuera de la ventana de 5 años, pero es la base de los estudios de conteo de panojas).

## Diferencias con el flujo de mango
- **Altura de vuelo:** las plantas son pequeñas. Para contar plántulas (V2–V6) se necesita un GSD de ≤ 1 cm (vuelos de 10–30 m); para panojas, de 1–2 cm.
- **Momento del vuelo:** contar plántulas entre V3 y V6, antes de que las hileras se cierren, o contar panojas en floración.
- **Método:** el conteo por hileras (Wang et al. 2023; David et al. 2022) aprovecha el marco de siembra. El índice ExG y la segmentación del flujo actual sirven para la máscara de vegetación. Para separar plantas se recomienda un detector YOLO (`yolo_mango.py`, con la clase "maiz").
