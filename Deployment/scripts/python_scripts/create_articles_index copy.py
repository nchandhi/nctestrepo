#Get Azure Key Vault Client

key_vault_name = 'to-be-replaced'

#hardcoded values
index_name = "pubmedinfluenza"
file_system_client = "data"
directory = 'data/sampledata/pubmed_articles' 

from azure.keyvault.secrets import SecretClient  
from azure.identity import DefaultAzureCredential  

def get_secrets_from_kv(kv_name, secret_name):
    
  # Set the name of the Azure Key Vault  
  key_vault_name = kv_name 
    
  # Create a credential object using the default Azure credentials  
  credential = DefaultAzureCredential()  
    # Create a secret client object using the credential and Key Vault name  
  secret_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net/", credential=credential)  
    
  # Retrieve the secret value  
  return(secret_client.get_secret(secret_name).value)


#Utils 
 # Import required libraries  
import os  
import json  
import openai

import os  
from azure.core.credentials import AzureKeyCredential  
# from azure.ai.textanalytics import TextAnalyticsClient  

from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient, SearchIndexingBufferedSender  
from azure.search.documents.indexes import SearchIndexClient  
from azure.search.documents.models import (
    QueryAnswerType,
    QueryCaptionType,
    QueryCaptionResult,
    QueryAnswerResult,
    SemanticErrorMode,
    SemanticErrorReason,
    SemanticSearchResultsType,
    QueryType,
    VectorizedQuery,
    VectorQuery,
    VectorFilterMode,    
)
from azure.search.documents.indexes.models import (  
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticPrioritizedFields,
    SemanticField,  
    SearchField,  
    SemanticSearch,
    VectorSearch,  
    HnswAlgorithmConfiguration,
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    VectorSearchProfile,
    SearchIndex,
    SearchField,
    SearchFieldDataType,
    SimpleField,
    SearchableField,
    VectorSearch,
    ExhaustiveKnnParameters,
    SearchIndex,  
    SearchField,  
    SearchFieldDataType,  
    SimpleField,  
    SearchableField,  
    SearchIndex,  
    SemanticConfiguration,  
    SemanticField,  
    SearchField,  
    VectorSearch,  
    HnswParameters,  
    VectorSearch,
    VectorSearchAlgorithmKind,
    VectorSearchAlgorithmMetric,
    VectorSearchProfile,
)  
search_endpoint =  get_secrets_from_kv(key_vault_name,"AZURE-SEARCH-SERVICE-ENDPOINT")
search_key =  get_secrets_from_kv(key_vault_name,"AZURE-SEARCH-ADMIN-KEY")

openai.api_type = get_secrets_from_kv(key_vault_name,"OPENAI-API-TYPE")
openai.api_key  = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-API-KEY")
openai.api_base = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-ENDPOINT")
openai.api_version = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-API-VERSION")

openai_api_type = get_secrets_from_kv(key_vault_name,"OPENAI-API-TYPE")
openai_api_key  = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-API-KEY")
openai_api_base = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-ENDPOINT")
openai_api_version = get_secrets_from_kv(key_vault_name,"AZURE-OPENAI-API-VERSION")

# Set up your Azure Text Analytics service and credentials  
COG_SERVICES_NAME = get_secrets_from_kv(key_vault_name,"COG-SERVICES-NAME")
COG_SERVICES_ENDPOINT = get_secrets_from_kv(key_vault_name,"COG-SERVICES-ENDPOINT")
COG_SERVICES_KEY = get_secrets_from_kv(key_vault_name,"COG-SERVICES-KEY")

cog_services_credential = AzureKeyCredential(COG_SERVICES_KEY)  

# Create a TextAnalyticsClient using your endpoint and credentials  
cog_services_client = TextAnalyticsClient(endpoint=COG_SERVICES_ENDPOINT, credential=cog_services_credential)  

def get_named_entities(cog_services_client,input_text): 
    # Call the named entity recognition API to extract named entities from your text  
    result = cog_services_client.recognize_entities(documents=[input_text])  
    
    # return the named entities for each document 
    # full list of categories #https://learn.microsoft.com/en-us/azure/ai-services/language-service/named-entity-recognition/concepts/named-entity-categories?tabs=ga-api 

    Person = [] 
    Location = []
    Organization = [] 
    DateTime = []
    URL = [] 
    Email = []
    PersonType = []
    Event = []
    Quantity = []

    for idx, doc in enumerate(result):
        if not doc.is_error:
            for entity in doc.entities: 
                if entity.category == "DateTime":
                    DateTime.append(entity.text)
                elif entity.category == "Person":
                    Person.append(entity.text)
                elif entity.category == "Location":
                    Location.append(entity.text)
                elif entity.category == "Organization":
                    Organization.append(entity.text)
                elif entity.category == "URL":
                    URL.append(entity.text)
                elif entity.category == "Email":
                    Email.append(entity.text)
                elif entity.category == "PersonType":
                    PersonType.append(entity.text)
                elif entity.category == "Event":
                    Event.append(entity.text)
                elif entity.category == "Quantity":
                    Quantity.append(entity.text)

        else:  
            print("  Error: {}".format(doc.error.message)) 
    return(list(set(DateTime)),list(set(Person)),list(set(Location)),list(set(Organization)),list(set(URL)),list(set(Email)),list(set(PersonType)),list(set(Event)),list(set(Quantity)))
    

from openai import AzureOpenAI

# Function: Get Embeddings
def get_embeddings(text: str,openai_api_base,openai_api_version,openai_api_key):
    model_id = "text-embedding-ada-002"
    client = AzureOpenAI(
        api_version='2023-07-01-preview',
        azure_endpoint=openai_api_base,
        api_key = openai_api_key
    )
    
    # embedding = openai.Embedding.create(input=text, deployment_id=model_id)["data"][0]["embedding"]
    embedding = client.embeddings.create(input=text, model=model_id).data[0].embedding

    return embedding

from langchain.text_splitter import MarkdownTextSplitter, RecursiveCharacterTextSplitter, PythonCodeTextSplitter
import tiktoken

import re

def clean_spaces_with_regex(text):
    # Use a regular expression to replace multiple spaces with a single space
    cleaned_text = re.sub(r'\s+', ' ', text)
    # Use a regular expression to replace consecutive dots with a single dot
    cleaned_text = re.sub(r'\.{2,}', '.', cleaned_text)
    return cleaned_text

def estimate_tokens(text):
    GPT2_TOKENIZER = tiktoken.get_encoding("gpt2")
    return(len(GPT2_TOKENIZER.encode(text)))

def chunk_data(text):
    text = clean_spaces_with_regex(text)
    SENTENCE_ENDINGS = [".", "!", "?"]
    WORDS_BREAKS = ['\n', '\t', '}', '{', ']', '[', ')', '(', ' ', ':', ';', ',']
    num_tokens = 1024 #500
    min_chunk_size = 10
    token_overlap = 0

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(separators=SENTENCE_ENDINGS + WORDS_BREAKS,chunk_size=num_tokens, chunk_overlap=token_overlap)

    return(splitter.split_text(text))

# Create the search index
search_credential = AzureKeyCredential(search_key)

index_client = SearchIndexClient(
    endpoint=search_endpoint, credential=credential)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="chunk_id", type=SearchFieldDataType.String),
    SearchableField(name="pubmed_id", type=SearchFieldDataType.String),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="abstract", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="sourceurl", type=SearchFieldDataType.String),
    SearchableField(name="publicurl", type=SearchFieldDataType.String),
    # SearchableField(name="sourcefile", type=SearchFieldDataType.String),
    SimpleField(name="dateTime", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Person", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Location", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Organization", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="URL", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Email", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="PersonType", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Event", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SimpleField(name="Quantity", type=SearchFieldDataType.Collection(SearchFieldDataType.String),Filterable=True,Sortable=True, Facetable=True),
    SearchField(name="titleVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile"),
    SearchField(name="contentVector", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=1536, vector_search_profile_name="myHnswProfile")
]

# Configure the vector search configuration  
vector_search = VectorSearch(
    algorithms=[
        HnswAlgorithmConfiguration(
            name="myHnsw",
            kind=VectorSearchAlgorithmKind.HNSW,
            parameters=HnswParameters(
                m=4,
                ef_construction=400,
                ef_search=500,
                metric=VectorSearchAlgorithmMetric.COSINE
            )
        ),
        ExhaustiveKnnAlgorithmConfiguration(
            name="myExhaustiveKnn",
            kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
            parameters=ExhaustiveKnnParameters(
                metric=VectorSearchAlgorithmMetric.COSINE
            )
        )
    ],
    profiles=[
        VectorSearchProfile(
            name="myHnswProfile",
            algorithm_configuration_name="myHnsw",
        ),
        VectorSearchProfile(
            name="myExhaustiveKnnProfile",
            algorithm_configuration_name="myExhaustiveKnn",
        )
    ]
)

semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        title_field=SemanticField(field_name="title"),
        content_fields=[SemanticField(field_name="content")]
    )
)

# Create the semantic settings with the configuration
semantic_search = SemanticSearch(configurations=[semantic_config])

# Create the search index with the semantic settings
index = SearchIndex(name=index_name, fields=fields,
                    vector_search=vector_search, semantic_search=semantic_search)
result = index_client.create_or_update_index(index)
print(f' {result.name} created')


#add documents to the index

from azure.core.credentials import AzureKeyCredential  
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient
)
from azure.identity import ClientSecretCredential  
import PyPDF2  
from io import BytesIO
import base64
import time
import pandas as pd


account_name = get_secrets_from_kv(key_vault_name, "ADLS-ACCOUNT-NAME")
tenant_id = get_secrets_from_kv(key_vault_name, "TENANT-ID")
client_id = get_secrets_from_kv(key_vault_name, "SPN-CLIENTID")  
client_secret = get_secrets_from_kv(key_vault_name, "SPN-CLIENTSECRET") 

account_url = f"https://{account_name}.dfs.core.windows.net"
adls_credential = ClientSecretCredential(tenant_id, client_id, client_secret)  
service_client = DataLakeServiceClient(account_url, credential=adls_credential,api_version='2023-01-03') 


file_system_client = service_client.get_file_system_client(file_system_client)  
directory_name = directory + '/pdfs'
paths = file_system_client.get_paths(path=directory_name)

# Azure Cognitive Search Vector Index
search_credential = AzureKeyCredential(search_key)
# Get Search Client
client = SearchClient(search_endpoint, index_name, search_credential)
# get index client
index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)

# Read the CSV file into a Pandas DataFrame
file_path = directory + '/pubmed_articles.csv'
file_client = file_system_client.get_file_client(file_path)
csv_file = file_client.download_file()
df_metadata = pd.read_csv(csv_file, encoding='utf-8')

docs = []
num_pdfs = 0
counter = 0
for path in paths:
    num_pdfs += 1
    file_client = file_system_client.get_file_client(path.name)
    pdf_file = file_client.download_file()
    stream = BytesIO()
    pdf_file.readinto(stream)
    pdf_reader = PyPDF2.PdfReader(stream)
    filename = path.name.split('/')[-1]
    pubmedid = filename.replace('.pdf','')

    df_file_metadata = df_metadata[df_metadata['pubmed_id']==int(pubmedid)].iloc[0]
   
    text = "" 

    n = 2 #len(pdf_reader.pages)
    if len(pdf_reader.pages) < 10:
        n = len(pdf_reader.pages)
    for page_num in range(n): #range(len(pdf_reader.pages)):
        public_url = df_file_metadata['publicurl'] + '#page=' + str(page_num) 

        page = pdf_reader.pages[page_num]
        text = page.extract_text()         
        
        chunks = chunk_data(text)
        chunk_num = 0
        for chunk in chunks:
            chunk_num += 1
            d = {
                "chunk_id" : path.name.split('/')[-1] + '_' + str(page_num).zfill(2) +  '_' + str(chunk_num).zfill(2),
                "pubmed_id": str(df_file_metadata['pubmed_id']),
                 "content": chunk,       
                 "title": df_file_metadata['title'],
                 "abstract": df_file_metadata['abstract'] } #path.name.split('/')[-1] + '_' + str(page_num).zfill(2) +  '_' + str(chunk_num).zfill(2)} 

            d["dateTime"],d["Person"],d["Location"],d["Organization"],d["URL"],d["Email"],d["PersonType"],d["Event"],d["Quantity"] = get_named_entities(cog_services_client,d["content"])

            counter += 1

            try:
                v_titleVector = get_embeddings(d["title"])
            except:
                time.sleep(30)
                v_titleVector = get_embeddings(d["title"])
            
            try:
                v_contentVector = get_embeddings(d["content"])
            except:
                time.sleep(30)
                v_contentVector = get_embeddings(d["content"])


            docs.append(
            {
                    "id": base64.urlsafe_b64encode(bytes(d["chunk_id"], encoding='utf-8')).decode('utf-8'),
                    "chunk_id": d["chunk_id"],
                    "pubmed_id": d["pubmed_id"],
                    "title": d["title"],
                    "abstract": d["abstract"],
                    "content": d["content"],
                    "sourceurl": path.name.split('/')[-1], #d["url"],
                    "publicurl": public_url, #d["url"],
                    "dateTime": d["dateTime"],
                    "Person": d["Person"],
                    "Location": d["Location"],
                    "Organization": d["Organization"],
                    "URL": d["URL"],
                    "Email": d["Email"],
                    "PersonType": d["PersonType"],
                    "Event": d["Event"],
                    "Quantity": d["Quantity"],
                    "titleVector": v_titleVector,
                    "contentVector": v_contentVector
            }
            )
            
            if counter % 10 == 0:
                result = client.upload_documents(documents=docs)
                docs = []
                print(f' {str(counter)} uploaded')
    break
#upload the last batch
if docs != []:
    client.upload_documents(documents=docs)


# import os
# from azure.core.credentials import AzureKeyCredential  
# from azure.storage.filedatalake import (
#     DataLakeServiceClient,
#     DataLakeDirectoryClient,
#     FileSystemClient
# )
# from azure.identity import ClientSecretCredential  
# import PyPDF2  
# from io import BytesIO
# import base64
# import time
# import pandas as pd

# account_name = get_secrets_from_kv(key_vault_name,"ADLS-ACCOUNT-NAME")
# tenant_id = get_secrets_from_kv(key_vault_name,"TEANT-ID")
# client_id = get_secrets_from_kv(key_vault_name,"SPN-CLIENTID")
# client_secret = get_secrets_from_kv(key_vault_name,"SPN-CLIENTSECRET")

# account_url = f"https://{account_name}.dfs.core.windows.net"
# adls_credential = ClientSecretCredential(tenant_id, client_id, client_secret)  
# service_client = DataLakeServiceClient(account_url, credential=adls_credential) 

# file_system_client = service_client.get_file_system_client("demodata")  
# # directory_name = '/kbasesmall'

# # Read the CSV file into a Pandas DataFrame
# file_path = 'userguides/Metadata.csv'
# file_client = file_system_client.get_file_client(file_path)
# csv_file = file_client.download_file()
# df_metadata = pd.read_csv(csv_file, encoding='utf-8')

# paths = file_system_client.get_paths(path=directory_name)

# # Azure Cognitive Search Vector Index
# search_credential = AzureKeyCredential(search_key)
# # Get Search Client
# client = SearchClient(search_endpoint, index_name, search_credential)
# # get index client
# index_client = SearchIndexClient(endpoint=search_endpoint, credential=search_credential)

# docs = []
# counter = 0
# for path in paths:
#     # counter += 1
#     # print(path.name + '\n')
#     file_client = file_system_client.get_file_client(path.name)
#     pdf_file = file_client.download_file()
#     stream = BytesIO()
#     pdf_file.readinto(stream)
#     pdf_reader = PyPDF2.PdfReader(stream)

#     text = ""  
#     for page_num in range(5): #range(2): #range(pdf_reader.getNumPages()):  #page_num in range(5):
#         public_url = df_metadata[df_metadata['FileName'].str.contains(str(path.name.split('/')[-1].split('.')[0]), case=False)].iloc[0]['Url']+ '#page=' + str(page_num) 

#         page = pdf_reader.pages[page_num]  
#         text = page.extract_text()
#         chunks = chunk_data(text)
#         chunk_num = 0
#         for chunk in chunks:
#             # time.sleep(2)
#             chunk_num += 1

#             d = {"content": chunk,
#                 "title":path.name.split('/')[-1] + '_' + str(page_num).zfill(2) +  '_' + str(chunk_num).zfill(2)} 

#             d["dateTime"],d["Product"],d["Person"],d["Location"],d["Organization"],d["URL"],d["Email"],d["PersonType"],d["Event"],d["Quantity"] = get_named_entities(cog_services_client,d["content"])

#             counter += 1
#             try:
#                 title_vector = get_embeddings(d["title"])
#                 content_vector = get_embeddings(d["content"])
#             except:
#                 time.sleep(8)
#                 title_vector = get_embeddings(d["title"])
#                 content_vector = get_embeddings(d["content"])
                
#             docs.append(
#             {
#                     "id": base64.urlsafe_b64encode(bytes(d["title"], encoding='utf-8')).decode('utf-8'), 
#                     "title": d["title"],
#                     "content": d["content"],
#                     "sourceurl": path.name, 
#                     "publicurl": public_url, 
#                     "dateTime": d["dateTime"],
#                     "Product": d["Product"],
#                     "Person": d["Person"],
#                     "Location": d["Location"],
#                     "Organization": d["Organization"],
#                     "URL": d["URL"],
#                     "Email": d["Email"],
#                     "PersonType": d["PersonType"],
#                     "Event": d["Event"],
#                     "Quantity": d["Quantity"],
#                     "titleVector": title_vector,
#                     "contentVector": content_vector,
#             }
#             )
            
#             if counter % 100 == 0:
#                 result = client.upload_documents(documents=docs)
#                 docs = []
                
    
# #upload the last batch
# if docs != []:
#    res = client.upload_documents(documents=docs)
#    print(res)


