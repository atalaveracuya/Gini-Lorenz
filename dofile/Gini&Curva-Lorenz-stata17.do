
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
global excel       "$ubicacion\excel"

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

global ini=$inicio-2000 
global fin=$final-2000  
global periodo=$final - $inicio + 1


*Generamos matrices vacias para almacenar resultados:
mat gini=J($periodo,2,0)
mat area=J(3,6,.)
mat dpto=J(27,6,.)
mat sexo=J(3,6,.)
mat gedad=J(5,6,.)


*Secuencia de proceso
		forvalues i=$ini(1)$fin{

	local year=2000
	local year=`year' + `i'
	local t = `year'+1-$inicio

use enaho01-`year'-200.dta, clear
keep if p203==1
save "enaho-cap200-jh.dta",replace 

use enaho-cap200-jh.dta,clear 
merge 1:1 conglome vivienda hogar using sumaria-`year'.dta 


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
*table d_gpcm [aw=facpob], stat( mean gpcm) nformat(%15.0f) 

*ingreso real promedio per capita mensual, por deciles 
*table d_ipcm [aw=facpob], stat( mean ipcm) nformat(%15.0f) 


*Indice de Gini-desigualdad de gasto 

*usando ineqerr  
*ineqerr gpcm [w=facpob], reps(50) 
*ineqerr gpcm [w=facpob] if area==1, reps(50)  
*ineqerr gpcm [w=facpob] if area==2, reps(50)  

*usando ineqdec0

*Nacional 
ineqdec0 gpcm [w=facpob] 
local gini=`r(gini)' 
mat gini`year'=J(1,2,0)
mat gini`year'[1,1]=`year'
mat gini`year'[1,2]=`gini'

*Urbano-Rural 
ineqdec0 gpcm [w=facpob], by(area) 
local urbano=`r(gini_1)'
local rural=`r(gini_2)' 
mat area`year'=J(3,1,.)
mat area`year'[1,1]=`year'
mat area`year'[2,1]=`urbano' 
mat area`year'[3,1]=`rural' 


*Departamentos
ineqdec0 gpcm [w=facpob], by(rDpto2) 
mat dpto`year'=J(27,1,.)
mat dpto`year'[1,1]=`year'
mat dpto`year'[2,1]=`r(gini_1)'
mat dpto`year'[3,1]=`r(gini_2)'
mat dpto`year'[4,1]=`r(gini_3)'
mat dpto`year'[5,1]=`r(gini_4)'
mat dpto`year'[6,1]=`r(gini_5)'
mat dpto`year'[7,1]=`r(gini_6)'
mat dpto`year'[8,1]=`r(gini_7)'
mat dpto`year'[9,1]=`r(gini_8)'
mat dpto`year'[10,1]=`r(gini_9)'
mat dpto`year'[11,1]=`r(gini_10)'
mat dpto`year'[12,1]=`r(gini_11)'
mat dpto`year'[13,1]=`r(gini_12)'
mat dpto`year'[14,1]=`r(gini_13)'
mat dpto`year'[15,1]=`r(gini_14)'
mat dpto`year'[16,1]=`r(gini_15)'
mat dpto`year'[17,1]=`r(gini_16)'
mat dpto`year'[18,1]=`r(gini_17)'
mat dpto`year'[19,1]=`r(gini_18)'
mat dpto`year'[20,1]=`r(gini_19)'
mat dpto`year'[21,1]=`r(gini_20)'
mat dpto`year'[22,1]=`r(gini_21)'
mat dpto`year'[23,1]=`r(gini_22)'
mat dpto`year'[24,1]=`r(gini_23)'
mat dpto`year'[25,1]=`r(gini_24)'
mat dpto`year'[26,1]=`r(gini_25)'
mat dpto`year'[27,1]=`r(gini_26)'

*Sexo 
ineqdec0 gpcm [w=facpob], by(sexo) 
local Hombre=`r(gini_1)'
local Mujer=`r(gini_2)' 
mat sexo`year'=J(3,1,.)
mat sexo`year'[1,1]=`year'
mat sexo`year'[2,1]=`Hombre' 
mat sexo`year'[3,1]=`Mujer' 


*grupo de edades 
ineqdec0 gpcm [w=facpob], by(g_edad) 
mat gedad`year'=J(5,1,.)
local 18a29 `r(gini_4)' 
local 30a45 `r(gini_5)' 
local 46a60 `r(gini_6)' 
local mas60   `r(gini_7)' 
mat gedad`year'[1,1]=`year'
mat gedad`year'[2,1]=`18a29'
mat gedad`year'[3,1]=`30a45'
mat gedad`year'[4,1]=`46a60'
mat gedad`year'[5,1]=`mas60'

		}
		
forvalues i=$ini(1)$fin{

	local year=2000
	local year=`year' + `i'
	local t = `year'+1-$inicio
mat gini[`t',1]=gini`year'
mat area[1,`t']=area`year'
mat dpto[1,`t']=dpto`year'
mat sexo[1,`t']=sexo`year'
mat gedad[1,`t']=gedad`year'
		}
	
//Nacional 
*(matrix cortada. Empieza en 1° fila, 1° columna)
mat gini=gini' 
matrix C=[gini[2..., 1...]]  	
putexcel set "${excel}\reportJanuary272022.xlsx", sheet("1.1") modify 
putexcel C6 = matrix(C),nformat(0,#.00) hcenter  


//Area 
matrix C=[area[2..., 1...]]  	
putexcel set "${excel}\reportJanuary272022.xlsx", sheet("1.1") modify 
putexcel C8 = matrix(C),nformat(0,#.00) hcenter  


//Departamento 
matrix C=[dpto[2..., 1...]]  
putexcel set "${excel}\reportJanuary272022.xlsx", sheet("1.1") modify 
putexcel C11= matrix(C),nformat(0,#.00) hcenter  

//Sexo 
matrix C=[sexo[2..., 1...]]  
putexcel set "${excel}\reportJanuary272022.xlsx", sheet("1.1") modify 
putexcel C38= matrix(C),nformat(0,#.00) hcenter  


//Grupo de edad
matrix C=[gedad[2..., 1...]]  	
putexcel set "${excel}\reportJanuary272022.xlsx", sheet("1.1") modify 
putexcel C41= matrix(C),nformat(0,#.00) hcenter  

**********************
***Curva de lorenz ***
**********************

*Nacional-Urbano-Rural 

glcurve gpcm [aw=facpob] , pvar(p0) glvar(l0) lorenz nograph

glcurve gpcm [aw=facpob] if area==1 , pvar(p1) glvar(l1) lorenz nograph
glcurve gpcm [aw=facpob] if area==2, pvar(p2) glvar(l2) lorenz nograph

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
          , aspect(1) xtitle("% acumulado población, p") ///    
          title("Comparación de la Curva de Lorenz,2020") ///    
          ytitle("% acumulado ingresos") ///    
          legend(label(1 "L0-Nacional") label(2 "L1-Urbano") label(3 "L2-Rural") label(4 "Equidistribución") ) 

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
          , aspect(1) xtitle("% acumulado población, p") ///    
          title("Comparación de la Curva de Lorenz, segun sexo,2020") ///    
          ytitle("% acumulado ingresos") ///    
          legend(label(1 "L1-Varon") label(2 "L2-Mujer") label(3 "Equidistribución") ) 

graph export "${graficos}//graph02.png", width(1000) replace
		  
		  