import requests
import json
from keys import *
import torch
import torch.nn.functional as F
from transformers import BertForTokenClassification, BertTokenizer, BertModel
import pandas as pd
from bs4 import BeautifulSoup

def get_key_labels(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt")
    with torch.no_grad():
        outputs = model(**inputs)
    
    predicted_labels = outputs.logits.argmax(dim=2)
    return inputs, predicted_labels

def generate_token(ClientId, ClientSecret):
    token_endpoint = 'https://icdaccessmanagement.who.int/connect/token'
    client_id = ClientId
    client_secret = ClientSecret
    scope = 'icdapi_access'
    grant_type = 'client_credentials'
    
    # set data to post
    payload = {'client_id': client_id, 
               'client_secret': client_secret, 
               'scope': scope, 
               'grant_type': grant_type}
    
    # make request
    r = requests.post(token_endpoint, data=payload, verify=True).json()
    token = r['access_token']
    
    return token

def key_labels_to_text(inputs, predicted_labels, model, tokenizer):
    predicted_phrases = []
    current_phrase = []

    # Assumes tokenizer is biobert
    
    for token_id, label_id in zip(inputs["input_ids"][0], predicted_labels[0]):
        token = tokenizer.convert_ids_to_tokens(token_id.item())
        label = model.config.id2label[label_id.item()]
        if (token != tokenizer.pad_token and token != tokenizer.sep_token and token != tokenizer.cls_token):
            if label == "B-DISEASE":
                if current_phrase:
                    predicted_phrases.append(" ".join(current_phrase))
                    current_phrase = []
                current_phrase.append(token)
            elif label == "I-DISEASE" and current_phrase:
                current_phrase.append(token)
            elif current_phrase:
                predicted_phrases.append(" ".join(current_phrase))
                current_phrase = []
        
    if current_phrase:
        predicted_phrases.append(" ".join(current_phrase))
    
    # Post-process to join subword tokens
    final_predicted_phrases = []
    for phrase in predicted_phrases:
        phrase = phrase.replace(" ##", "")
        final_predicted_phrases.append(phrase)
    
    return final_predicted_phrases

def get_keywords(text, model, tokenizer):
    inputs, predicted_labels = get_key_labels(text, model, tokenizer)
    keywords = key_labels_to_text(inputs, predicted_labels, model, tokenizer)
    return keywords

def seq_to_context_vec(input_text, model, tokenizer):
    # assumes bert model
    inputs = tokenizer(input_text, return_tensors='pt', padding=True, truncation=True)
    outputs = model(**inputs)
    last_hidden_state = outputs.last_hidden_state
    context_vec = last_hidden_state[:, 0, :]  # Using [CLS] token embedding for pooling
    return context_vec

def get_top_icd_codes(text, model, tokenizer, token):
    keywords = get_keywords(text, model, tokenizer)
    keywords.extend([text])
    dfs = []
    for keys in keywords:
        dfs.append(get_top_icd_matches(keys, token))
    master_df = pd.concat(dfs)
    return master_df

def bolster_top_scores(df, text, model, tokenizer):
    cos_sim = []
    vec1 = seq_to_context_vec(text, model, tokenizer)
    for index, row in df.iterrows():
        vec2 = seq_to_context_vec(row['title'], model, tokenizer)
        cos_sim.append(F.cosine_similarity(vec1, vec2).item())
    df['cos_sim'] = cos_sim
    return df

def get_icd11_from_query(text, biobert_model, biobert_tokenizer, bert_model, bert_tokenizer):
    df = get_top_icd_codes(text, biobert_model, biobert_tokenizer)
    df = bolster_top_scores(df, text, bert_model, bert_tokenizer)
    df['final_score'] = df['score'] * df['cos_sim']
    df.sort_values(by = 'final_score', ascending = False)
    return df.head(4)

def get_top_icd_matches(query, token):
    uri = f'https://id.who.int/icd/release/11/2023-01/mms/search?q={query}'

    # HTTP header fields to set
    
    headers = {'Authorization':  'Bearer '+token, 
               'Accept': 'application/json', 
               'Accept-Language': 'en',
               'API-Version': 'v2',
               }
    
    # make request           
    r = requests.get(uri, headers=headers, verify=True)
    
    # print the result
    out = r.json()
    try:
        df = pd.DataFrame(sorted(out['destinationEntities'], key = lambda x: x['score'], reverse = True))
        df['title'] = df['title'].apply(lambda x: BeautifulSoup(x, "html.parser").get_text())
        df = df[['title','theCode','score']]
        df['text'] = query
    except:
        df = pd.DataFrame()
    return df

biobert_model_name = "alvaroalon2/biobert_diseases_ner"
bert_model_name = "bert-base-uncased"

class ICD_Fetcher:
    def __init__(self,
                ClientId,
                ClientSecret):
        self.token = generate_token(ClientId, ClientSecret)

        print(f'Downloading model {biobert_model_name}')
        self.biobert = BertForTokenClassification.from_pretrained(biobert_model_name)
        self.biobert_tokenizer = BertTokenizer.from_pretrained(biobert_model_name)

        print(f'Downloading model {bert_model_name}')
        self.bert = BertModel.from_pretrained(bert_model_name)
        self.bert_tokenizer = BertTokenizer.from_pretrained(bert_model_name)




    def get_icd11_from_query(self, text):
        biobert_model = self.biobert
        biobert_tokenizer = self.biobert_tokenizer

        bert_model = self.bert
        bert_tokenizer = self.bert_tokenizer

        df = get_top_icd_codes(text, biobert_model, biobert_tokenizer, self.token)
        df = bolster_top_scores(df, text, bert_model, bert_tokenizer)
        df['final_score'] = df['score'] * df['cos_sim']
        df.sort_values(by = 'final_score', ascending = False)
        df = df.head(4)
        to_dict = df.to_dict(orient = 'records')
        return to_dict

