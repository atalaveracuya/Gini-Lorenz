
*GRUPOS DE EDAD
***************************
recode p208a (0/5=1) (6/13=2) (14/17=3) (18/29=4) (30/45=5) (46/60=6) (61/99=7), gen (g_edad)
lab def g_edad 1 "De 0 a 5 años" 2 "De 6 a 13 años" 3 "De 14 a 17 años" 4 "De 18 a 29 años" 5 "De 30 a 45 años" 6 "De 46 a 60 años" 7 "Más de 60 años"
lab val g_edad g_edad
la var g_edad "Grupo de edad"