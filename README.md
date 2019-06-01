# Variants annotation data API

## 1. Constraints

### 1.1 Iterms per Request

The maxium mutation number returned per request is 10,000. Any result larger than this number will get a link to get the result for next page.


### 1.2 IP address

All request should from USC inner IP address.



## 2. Responses
API sends a response as a JSON object.

~~~
{
   "status": "success/fail"
   "data": [ ... ],
   "format": "...",
   "header":[...],
   "next_page":""
}
~~~
## 3. Queries

The following table lists all API endpoints currently available at 

`/api`

|API endpoint| Description|
|------------|---------|
|`/`| Retrieve meta-information about dataset.|
|`/header/<string:dataset name>`|Get all headers name and id for a dataset|
|`/anno_tree/<string:dataset name>`|Get structured headers name and id for a dataset|
|`/origin/<string:dataset name>`| Retrieve  links for download origin files.|
|`/variant/<string:dataset name>`|Get single variant by chromosomal position or identifier.|
|`/region/<string:dataset name>`|Get all variants within a chromosomal region.|
|`/gotopage/<string:query id>/<int:page number>`|Get the data for a certain query of certain page number.|
|`/gene`|Get the genome interval for a gene.|
|`/batch/<string:dataset name>`|Get all variants in a region. Store the result in a temporary file and return the link for that file.|
### 3.1 Get annotation headers


#### 3.1.1

To get annotation headers, send `GET` request to 
/header/<string:dataset name>

e.g. `/header/HRC`

**Return example:** 

~~~
{ 
	4:"ANNOVAR_ensembl_Effect",
	5:"ANNOVAR_ensembl_Transcript_ID",
	...
}
~~~

#### 3.1.2 Structured Headers
To get structured annotation headers, send `GET` request to 
/anno_tree/<string:dataset name>

e.g. `/anno_tree/HRC`

**Return example:** 


~~~
{"header_tree_array":[
	{"detail":"",
	 "id":375,
	 "name":"1000Gp3",
	 "parent_id":0},
	 ...
 ]
}
	 
~~~

#### 3.2 Get Original Data Files

To download all original data files, request the download url by 

`/api/origin/<string:dataset name>`

**Return example:**

~~~
{ 
	4:"ANNOVAR_ensembl_Effect",
	5:"ANNOVAR_ensembl_Transcript_ID",
	...
}
~~~


### 3.3 Region query

####3.3.1
To query all variants within a region, send `GET` request to 

`/region/<string:dataset name>`.

 The following table lists all supported parameters.

|Parameter | Required | Description |
|------------|---------|----|
|`chrom `| Yes|Chromosome name.|
|`start`| Yes |Chromosomal start position in base-pairs.|
|`end`| Yes |Chromosomal end position in base-pairs.|
|`headers`|Optional|Header ids, seperated by %20|
**Examples:**

`/region/HRC?chrom=18&start=10&end=50000&headers=1%202%203%204%205`

~~~
{
  "data": [
    [
      "18",
      "10636",
      "A",
      "C",
      "upstream|upstream|downstream|downstream",
      "ENST00000572573|ENST00000575820|ENST00000572062|ENST00000572608"
    ],
    [
      "18",
      "10644",
      "C",
      "G",
      "upstream|upstream|downstream|downstream",
      "ENST00000572573|ENST00000575820|ENST00000572062|ENST00000572608"
    ],
    ...
    
  ],
  "format": "json",
  "headers": {
    "0": "chr",
    "1": "pos",
    "2": "ref",
    "3": "alt",
    "4": "ANNOVAR_ensembl_Effect",
    "5": "ANNOVAR_ensembl_Transcript_ID"
  },
  "next_page": "http://bioghost.usc.edu:5000/nextpage/ca2c39d1-6dfd-4c11-8292-478298a7e9ed",
  "page_id": "ca2c39d1-6dfd-4c11-8292-478298a7e9ed",
  "page_info": {
    "page_num": 1,
    "page_size": 100,
    "total_page": 3
  }
}
~~~

####3.3.2

To get certain page of a query, retrieve it by `page_id`. Send `GET` request to 
`/gotopgae/<string:page id>/<int:page number>`

**Examples:**

`/gotopage/ca2c39d1-6dfd-4c11-8292-478298a7e9ed/2`

**Response**

Same as 3.1.1

### 3.4 Single variant query
To query a single variant, send `GET` request to 

`http://bioghost.usc.edu:5000/api/variant`.The following table lists all supported parameters.

|Parameter | Required | Description |
|------------|---------|----|
|`chrom `| Yes|Chromosome name.|
|`pos`| Yes |Chromosomal position in base-pairs.|
|`ref`| Optional |Reference alle.|
|`alt`| Optional |Alternative alle|

**Examples:**

#### 3.4.1 	Find a variant 

`http://bioghost.usc.edu:5000/api/variant?chrom=chr2&pos=100008&ref=T&alt=A`


#### 3.4.1 	Find all variants at a position 
`http://bioghost.usc.edu:5000/api/variant?chrom=chr2&pos=100008`

### 3.5 Gene query

to do

### 3.6 Batch query
To query a batch of variants, send `GET` request to 

`http://bioghost.usc.edu:5000/api/batch/<string:dataset name>` 

Parameters are the same with region query.


## 4. R package
todo
### 4.1 R package Installation
### 4.2 R package Usage
