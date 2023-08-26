# ICD Fetcher
This is a little tool that uses BERT keyword extraction and cosine-similarity on context vectors as well as the ICD API to suggest 4 ICD-11 codes that can be used when filling out prior authorizations / orders for procedures. Choosing appropriate ICD codes when filling this out is important for insurance agencies to deem medical necessity and provide coverage. 

Currently there is no support for linking these ICD codes to CPT codes, but that is currently a work of progress for me.

## Quickstart

Initialize the `ICD_Fetcher` and add your ClientId and ClientSecret you got from the ICD API:

```
>>> ICD = ICD_Fetcher(ClientId, ClientSecret)
```

Describe a diagnostic profile and ICD codes will be suggested.

```
>>> ICD.get_icd11_from_query('stroke and mitral valve regurgitation')

[{'title': 'Stroke not known if ischaemic or haemorrhagic',
  'theCode': '8B20',
  'score': 0.0625,
  'text': 'stroke',
  'cos_sim': 0.8750547766685486,
  'final_score': 0.054690923541784286},
 {'title': 'Tremor due to certain specified central nervous system diseases',
  'theCode': '8A04.33',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8685241341590881,
  'final_score': 0.027141379192471504},
 {'title': 'Secondary stereotypy',
  'theCode': '8A07.01',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8302322030067444,
  'final_score': 0.025944756343960762},
 {'title': 'Cerebral ischaemic stroke, unspecified',
  'theCode': '8B11.5Z',
  'score': 0.03125,
  'text': 'stroke',
  'cos_sim': 0.8372837901115417,
  'final_score': 0.02616511844098568}]
```

