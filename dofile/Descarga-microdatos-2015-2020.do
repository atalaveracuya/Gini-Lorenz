*DESCARGA DE DATOS SUMARIA & MOD200 -2015 2020 . 
*Autor: Andrés Talavera Cuya 

*Referencia:
*Janet Porras  
*https://www.youtube.com/watch?v=bJV4MTKYKmM

*Luis Ulloa -Curso Intermedio de Stata

*Stephen Jenkins
*https://www.statalist.org/forums/forum/general-stata-discussion/general/288264-multiple-lorenz-curve-and-graph-line-45

*-------------------------------------------*

** Descarga **

clear all
set more off 
global ubicacion   "D:\ANDRES\Documentos\GitHub\IndicadoresStata\Gini\"
global dataset     "$ubicacion\dataset" 
global dofile      "$ubicacion\dofile"
*--------------------------------------*
*Porfavor agregue año de inicio y fin: 
*Ojo: El programa esta diseñado para que descargue solo sumaria para algunos 
*años entre el 2015 y 2020. 
 
global inicio     2015
global final      2020
*--------------------------------------*

*Ejecute con Stata versión 13.
*Sólo si descarga 2015 - corra: 5.-Alerta-2015.do
 
do "${dofile}//1.-codigo-encuestas.do"
do "${dofile}//2.-codigo-modulo.do"
do "${dofile}//3.-extraccion-zip.do"
do "${dofile}//4.-colocar-data-en-files.do"
do "${dofile}//5.-Alerta-2015.do"
+ 
