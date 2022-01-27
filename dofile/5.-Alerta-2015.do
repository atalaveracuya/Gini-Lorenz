
**verificar: 
*1) Alerta 2015
cls 
clear
set more off  
cd $Inicial 
		*+Alerta 2015
		cd $dataset\2015\Download
		cap copy "sumaria-2015.dta" "$Inicial\\sumaria-2015.dta"	
*       cap copy "enaho01a-2015-300.dta" "$Inicial\\enaho01a-2015-300.dta"	
*		cap copy "enaho01a-2015-400.dta" "$Inicial\\enaho01a-2015-400.dta"	
		cd $dataset\2015\Download\498_Modulo02\
    	cap copy "enaho01-2015-200.dta" "$Inicial\\enaho01-2015-200.dta"

		
cd $Inicial
		forvalues i=$inicio/$final{
			  use sumaria-`i'.dta,clear
              use enaho01-`i'-200.dta,clear 
		}
		