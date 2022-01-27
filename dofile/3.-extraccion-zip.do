
*Paso 2: extraccion zip
 
forvalues i=$ini/$fin{

	local year=2000
	local year=`year' + `i'
	local t = `year'+1-$inicio

	cd "$dataset"
	cap mkdir `year'
	cd `year'
	
	cap mkdir "Download"
	cd "Download"
	
	scalar r_enaho=ENAHO[`t',1]
*		forvalue j=1/5{
		foreach j in  2  {
		scalar r_menaho=MENAHO[`t',`j']
		display "`year'" " " r_enaho " " r_menaho
		local mod=r_enaho
		local i=r_menaho
		display "`i'" " " "`year'" " " "`mod'"
		cap copy http://iinei.inei.gob.pe/iinei/srienaho/descarga/STATA/`mod'-Modulo0`i'.zip enaho_`year'_mod_`i'.zip 
		cap unzipfile enaho_`year'_mod_`i'.zip, replace
		cap erase enaho_`year'_mod_`i'.zip
		}		
		
	scalar r_enaho=ENAHO[`t',1]
*		forvalue j=1/5{
		foreach j in 26 {
		scalar r_menaho=MENAHO[`t',`j']
		display "`year'" " " r_enaho " " r_menaho
		local mod=r_enaho
		local i=r_menaho
		display "`i'" " " "`year'" " " "`mod'"
		cap copy http://iinei.inei.gob.pe/iinei/srienaho/descarga/STATA/`mod'-Modulo`i'.zip enaho_`year'_mod_`i'.zip 
		cap unzipfile enaho_`year'_mod_`i'.zip, replace
		cap erase enaho_`year'_mod_`i'.zip
		}		

		}
