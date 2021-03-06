************************************
***************************************
***Indice de Gini y Curva de lorenz ***
***************************************
***************************************

*********************************************************
** Porfavor, corra esta parte con Stata 16 o superior:  
*********************************************************

clear all
set more off 
global ubicacion   "D:\ANDRES\Documentos\GitHub\IndicadoresStata\Gini\"
global dataset     "$ubicacion\dataset" 
global dofile      "$ubicacion\dofile"
global graficos    "$ubicacion\graficos"

global inicio     2015
global final      2020

cd $dataset/Inicial  
do "${dofile}//6.-unicode.do"
do "${dofile}//7.-verificar-si-corresponde-al-periodo-y-modulo.do"

** instalar comandos nuevos ** 

*unicode 
*findit ineqerr  
*findit ineqdec0 
*ssc install lorenz 
*search glcurve

** ** 

cd $dataset/Inicial 
use enaho01-2017-200.dta, clear
keep if p203==1
save "enaho-cap200-jh.dta",replace 


use enaho-cap200-jh.dta,clear 
merge 1:1 conglome vivienda hogar using sumaria-2017.dta 


*FACTOR DE EXPANSION POBLACIONAL 
do "${dofile}//11.-factor-expansion.do"

*AMBITO URBANO-RURAL
do "${dofile}//8.-area.do"

*DEPARTAMENTO 
do "${dofile}//9.- rDpto y rDpto2.do"

*SEXO 
do "${dofile}//13.-sexo.do"

*GRUPO DE EDADES 
do "${dofile}//14.-grupo-de-edad.do"

*GASTO E INGRESO 
do "${dofile}//10.-gastos-e-ingresos.do"

*DECILES 
do "${dofile}//12.-deciles.do"


************************************************************
**Resultados

*Gasto real promedio per capita mensual, por deciles 
table d_gpcm [aw=facpob], stat( mean gpcm) nformat(%15.0f) 

*ingreso real promedio per capita mensual, por deciles 
table d_ipcm [aw=facpob], stat( mean ipcm) nformat(%15.0f) 


*Indice de Gini-desigualdad de gasto 

*usando ineqerr  
*ineqerr gpcm [w=facpob], reps(50) 
*ineqerr gpcm [w=facpob] if area==1, reps(50)  
*ineqerr gpcm [w=facpob] if area==2, reps(50)  

*usando ineqdec0

*Nacional 
ineqdec0 gpcm [w=facpob]

*Urbano-Rural 
ineqdec0 gpcm [w=facpob], by(area) 

*Departamentos
ineqdec0 gpcm [w=facpob], by(rDpto2) 

*sexo 
ineqdec0 gpcm [w=facpob], by(sexo) 

*grupo de edades 
ineqdec0 gpcm [w=facpob], by(g_edad) 


****

*Indice de Gini-desigualdad de ingreso 

*Nacional 
ineqdec0 ipcm [w=facpob]
*Urbano-Rural 
ineqdec0 ipcm [w=facpob], by(area) 

*Departamentos
ineqdec0 ipcm [w=facpob], by(rDpto2) 

*sexo 
ineqdec0 ipcm [w=facpob], by(sexo) 

*grupo de edades 
ineqdec0 ipcm [w=facpob], by(g_edad) 


**********************
***Curva de lorenz ***
**********************

*Nacional-Urbano-Rural 

glcurve ipcm [aw=facpob] , pvar(p0) glvar(l0) lorenz nograph

glcurve ipcm [aw=facpob] if area==1 , pvar(p1) glvar(l1) lorenz nograph
glcurve ipcm [aw=facpob] if area==2, pvar(p2) glvar(l2) lorenz nograph

replace p0=p0*100
replace p1=p1*100
replace p2=p2*100
replace l0=l0*100
replace l1=l1*100
replace l2=l2*100

graph twoway (line l0 p0, sort yaxis(1 2)) /// 
            (line l1 p1, sort yaxis(1 2))  ///    
            (line l2 p2, sort yaxis(1 2))   /// 
          (function y = x, range(0 100) yaxis(1 2)) ///    
          , aspect(1) xtitle("% acumulado poblaci??n, p") ///    
          title("Comparaci??n de la Curva de Lorenz,2020") ///    
          ytitle("% acumulado ingresos") ///    
          legend(label(1 "L0-Nacional") label(2 "L1-Urbano") label(3 "L2-Rural") label(4 "Equidistribuci??n") ) 

graph export "${graficos}//graph01.png", width(1000) replace
		  
		  
*Por sexo 
drop p1 l1 p2 l2 
glcurve ipcm [aw=facpob] if sexo==1 , pvar(p1) glvar(l1) lorenz nograph
glcurve ipcm [aw=facpob] if sexo==2, pvar(p2) glvar(l2) lorenz nograph

replace p1=p1*100
replace p2=p2*100
replace l1=l1*100
replace l2=l2*100

graph twoway  (line l1 p1, sort yaxis(1 2))  ///    
            (line l2 p2, sort yaxis(1 2))   /// 
          (function y = x, range(0 100) yaxis(1 2)) ///    
          , aspect(1) xtitle("% acumulado poblaci??n, p") ///    
          title("Comparaci??n de la Curva de Lorenz, segun sexo,2020") ///    
          ytitle("% acumulado ingresos") ///    
          legend(label(1 "L1-Varon") label(2 "L2-Mujer") label(3 "Equidistribuci??n") ) 

graph export "${graficos}//graph02.png", width(1000) replace
