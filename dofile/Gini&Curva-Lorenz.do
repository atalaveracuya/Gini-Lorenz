
***************************************
***Indice de Gini y Curva de lorenz ***
***************************************
*Autor: Andrés Talavera Cuya 

*Referencia:
*Janet Porras  
*https://www.youtube.com/watch?v=bJV4MTKYKmM

*Luis Ulloa -Curso Intermedio de Stata

*Stephen Jenkins
*https://www.statalist.org/forums/forum/general-stata-discussion/general/288264-multiple-lorenz-curve-and-graph-line-45

*-------------------------------------------*


cls  
clear all
set more off 
global ubicacion  "D:\ANDRES\Documentos\GitHub\IndicadoresStata"

global dofile     "$ubicacion\\Gini\dofile"
global dataset    "D:\Dropbox\BASES\ENAHO\Inicial2\"
global graficos   "$ubicacion\\Gini\graficos"

cd $dataset 

dir*dta 
use sumaria-2020.dta 


*cortes geográficos 

****CORTES GEOGRAFICOS Y POLITICOS****

*AMBITO URBANO-RURAL
replace estrato = 1 if dominio ==8 
gen area = estrato <6
replace area=2 if area==0
label define area 2 "Rural" 1 "Urbana"
label val area area

*gasto nominal per capita 
gen gnpcm=(gashog2d/(12*mieperho))
*gasto real per capita 
gen gpcm=(gashog2d/(12*mieperho))/ld
*ingreso real per capita 
gen ipcm=(inghog1d/(12*mieperho))/ld
 
*factor de población
gen facpob=factor07*mieperho 

*deciles de gasto
xtile d_gpcm=gpcm [aw=facpob], nq(10)
tab d_gpcm [aw=facpob]

table d_gpcm [aw=facpob], stat( mean gpcm) nformat(%15.0f) 

*deciles de ingreso 
xtile d_ipcm=ipcm [aw=facpob], nq(10)
tab d_ipcm [aw=facpob]

table d_ipcm [aw=facpob], stat( mean ipcm) nformat(%15.0f) 



*Indice de Gini-desigualdad de gasto 

*Instalar ineqerr
*findit ineqerr
*findit ineqdec0

gen facpob1=int(facpob)

*usando ineqerr  
ineqerr gpcm [w=facpob1], reps(50) 
ineqerr gpcm [w=facpob1] if area==1, reps(50)  
ineqerr gpcm [w=facpob1] if area==2, reps(50)  

*usando ineqdec0

*Nacional 
ineqdec0 gpcm [w=facpob1]

*Urbano-Rural 
ineqdec0 gpcm [w=facpob1], by(area) 


****

*Indice de Gini-desigualdad de ingreso 

*Nacional 
ineqdec0 ipcm [w=facpob1]
*Urbano-Rural 
ineqdec0 ipcm [w=facpob1], by(area) 



**********************
***Curva de lorenz ***
**********************

*findit lorenz
*ssc install lorenz 
search glcurve
h lorenz 
h glcurve

*Nacional 
lorenz ipcm [w=facpob],g 
*Urbano 
lorenz ipcm [w=facpob] if area==1,g 
*Rural 
lorenz ipcm [w=facpob] if area==2,g 


*2da forma:

glcurve ipcm [aw=facpob] if area==1 , pvar(p1) glvar(l1) lorenz nograph
glcurve ipcm [aw=facpob] if area==2, pvar(p2) glvar(l2) lorenz nograph

replace p1=p1*100
replace p2=p2*100
replace l1=l1*100
replace l2=l2*100

graph twoway (line l1 p1, sort yaxis(1 2))  ///    
           (line l2 p2, sort yaxis(1 2)) ///    
          (function y = x, range(0 100) yaxis(1 2)) ///    
          , aspect(1) xtitle("% acumulado población, p") ///    
          title("Comparación de la Curva de Lorenz,2020") ///    
          ytitle("% acumulado ingresos") ///    
          legend(label(1 "L1-Urbano") label(2 "L2-Rural") label(3 "Equidistribución") )

graph export "${graficos}//graph01.png", width(1000) replace
		  
		  
