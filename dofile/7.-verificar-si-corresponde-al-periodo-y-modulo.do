
**Verificar: 
*2) ¿la data corresponde al periodo y módulo?

		forvalues i=$inicio(1)$final{
			  use sumaria-`i'.dta,clear
			  tab aÑo if aÑo=="`i'"  
			  mean linea
		}

		forvalues i=$inicio(1)$final{
			  use enaho01-`i'-200.dta,clear
			  tab aÑo if p207==1
			  
		}
