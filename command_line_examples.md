# command line examples

using `localhost:5000` as API address


## region query
`curl -i -H "Accept: application/json" "http://localhost:5000/region/HRC?chrom=18&start=10000&end=200000"`

## region query with configure file
`cat configure.txt|sed "s/ /%20/g"|curl -i -H "Accept: application/json" "http://localhost:5000/region/HRC?chrom=18&start=10000&end=200000&headers=$(</dev/stdin)"`

## gene query
`curl -i -H "Accept: application/json" "http://localhost:5000/gene/HRC?gene=NP_001073678"`

## gene query with configure file
`cat configure.txt|sed "s/ /%20/g"|curl -i -H "Accept: application/json" "http://localhost:5000/gene/HRC?gene=NP_001073678&headers=$(</dev/stdin)"`

## rsID query
`curl -i -H "Accept: application/json" "http://localhost:5000/rs/rs111739080"`

## vcf file query
`curl -X POST -i -F vcf=@q.vcf -F headers="1 2 3 4 5 6 7 8" http://localhost:5000/vcf`

### files using here

`configure.txt`

~~~
1 2 3 4 5 6 7 8
~~~

`q.vcf `

~~~
#CHROM	POS	ID	REF	ALT
18	10636	18:10636:A:C	A	C
18	10644	18:10644:C:G	C	G
18	10667	18:10667:C:T	C	T
18	10719	18:10719:C:G	C	G
18	10728	18:10728:G:A	G	A
18	10764	18:10764:C:T	C	T
18	10780	18:10780:G:A	G	A
18	10839	18:10839:C:G	C	G
18	10847	18:10847:C:A	C	A
~~~