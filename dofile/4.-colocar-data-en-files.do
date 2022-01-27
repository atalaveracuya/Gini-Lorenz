	
*Paso 3 Colocar data en files 		
global Inicial "$dataset\\Inicial"
cap mkdir "$Inicial"


forvalues i=$ini/$fin{

	local year=2000
	local year=`year' + `i'
	local t = `year'+1-$inicio

cd "$dataset"
cd `year'
cd "Download"

	scalar r_enaho=ENAHO[`t',1]
		foreach j in   2 {
		scalar r_menaho=MENAHO[`t',`j']
		local mod=r_enaho
		local i=r_menaho
		local cap=`j'*100
		display "`i'" " " "`year'" " " "`mod'" " " "`cap'"
		
*		cap copy "`mod'-Modulo0`i'\\enaho01a-`year'-`cap'.dta" "$Inicial\\enaho01a-`year'-`cap'.dta"
		cap copy "`mod'-Modulo0`i'\\enaho01-`year'-`cap'.dta" "$Inicial\\enaho01-`year'-`cap'.dta"

		
		}
		
	
	scalar r_enaho=ENAHO[`t',1]
		foreach j in  26 {
		scalar r_menaho=MENAHO[`t',`j']
		local mod=r_enaho
		local i=r_menaho

		cap copy "`mod'-Modulo`i'\\sumaria-`year'.dta" "$Inicial\\sumaria-`year'.dta"
		
		}		
		
		
		
		
		
		
}
