#region query
#curl -i -H "Accept: application/json" "http://localhost:5000/region/HRC?chrom=18&start=10000&end=200000"

#region query with configure file
#cat configure.txt|sed "s/ /%20/g"|curl -i -H "Accept: application/json" "http://localhost:5000/region/HRC?chrom=18&start=10000&end=200000&headers=$(</dev/stdin)"

#gene query
#curl -i -H "Accept: application/json" "http://localhost:5000/gene/HRC?gene=NP_001073678"

#gene query with configure file
#cat configure.txt|sed "s/ /%20/g"|curl -i -H "Accept: application/json" "http://localhost:5000/gene/HRC?gene=NP_001073678&headers=$(</dev/stdin)"

#rsID query
#curl -i -H "Accept: application/json" "http://localhost:5000/rs/rs111739080"

#vcf file query
#curl -X POST -i -F vcf=@q.vcf -F headers="1 2 3 4 5 6 7 8" http://localhost:5000/vcf

