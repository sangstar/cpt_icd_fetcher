# CPT & ICD Fetcher
This is a little tool that uses BERT keyword extraction and cosine-similarity on context vectors as well as the ICD API to suggest 4 ICD-11 codes that can be used when filling out prior authorizations / orders for procedures. Choosing appropriate ICD codes when filling this out is important for insurance agencies to deem medical necessity and provide coverage. 


## Quickstart

Initialize the `CPT_ICD_Fetcher` and add your ClientId and ClientSecret you got from the ICD API:

```
>>> from cpt_icd_fetcher import *
>>> text = 'stroke and mitral valve regurgitation'
>>> fetcher = CPT_ICD_Fetcher(ClientId, ClientSecret)
```

Describe a diagnostic profile and ICD codes will be suggested with the `get_icd11_from_query` method.

```
>>> fetcher.get_icd11_from_query(text)

[{'title': 'Stroke not known if ischaemic or haemorrhagic',
  'theCode': '8B20',
  'score': 0.0625,
  'text': 'stroke',
  'cos_sim': 0.8191625475883484,
  'final_score': 0.051197659224271774},
 {'title': 'Tremor due to certain specified central nervous system diseases',
  'theCode': '8A04.33',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8513481020927429,
  'final_score': 0.026604628190398216},
 {'title': 'Secondary stereotypy',
  'theCode': '8A07.01',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8245825171470642,
  'final_score': 0.025768203660845757},
 {'title': 'Cerebral ischaemic stroke, unspecified',
  'theCode': '8B11.5Z',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8037499785423279,
  'final_score': 0.025117186829447746}]
```

You can also get suggestions for CPT codes with the `get_cpt_codes` method.

```
>>> fetcher.get_cpt_codes(text, n_retrieve = 4)
[{'CPT': '33750',
  'label': 'Major vessel shunt',
  'cos_sim': 0.8993809819221497},
 {'CPT': '49428', 'label': 'Ligation of shunt', 'cos_sim': 0.8851978182792664},
 {'CPT': '0086T',
  'label': 'L ventricle fill pressure',
  'cos_sim': 0.8845935463905334},
 {'CPT': '92240', 'label': 'Icg angiography', 'cos_sim': 0.8832653760910034}]
```


