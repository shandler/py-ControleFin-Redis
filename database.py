import streamlit as st  # pip install streamlit
#from deta import Deta  # pip install deta
import redis # pip install redis 
import json

# Load the environment variables
#DETA_KEY = st.secrets["DETA_KEY"]

# Initialize with a project key
#deta = Deta(DETA_KEY)

# This is how to create/connect a database
#db = deta.Base("monthly_reports")
db = redis.Redis(
  host='redis-12148.c308.sa-east-1-1.ec2.cloud.redislabs.com',
  port=12148,
  password='EgQ7nsyeQsa139Yi5L5r89lRu72CJb9z')

# def insert_period(period, incomes, expenses, comment):
#     """Returns the user on a successful user creation, otherwise raises and error"""
#     return db.put({"key": period, "incomes": incomes, "expenses": expenses, "comment": comment})

def insert_period(period, incomes, expenses, comment):
    # Converter os dicionários de incomes e expenses em strings JSON
    incomes_json = json.dumps(incomes)
    expenses_json = json.dumps(expenses)
    # Insere um período no Redis
    db.hset(period, "incomes", incomes_json)
    db.hset(period, "expenses", expenses_json)
    db.hset(period, "comment", comment)
    return "Relatório criado com sucesso para o período " + period


# def fetch_all_periods():
#     """Returns a dict of all periods"""
#     res = db.fetch()
#     return res.items

def fetch_all_periods():
    """Recupera todos os períodos do Redis"""
    all_periods = []
    keys = db.keys('*')
    for key in keys:
        period_data = {}
        if db.type(key) == b'hash':  # Verifica se a chave é do tipo HASH
            data = db.hgetall(key)
            period_data['key'] = key.decode('utf-8')  # Adicionando a chave 'key' ao dicionário
            for field, value in data.items():
                field = field.decode('utf-8')
                if field == 'incomes' or field == 'expenses':
                    period_data[field] = json.loads(value.decode('utf-8'))
                else:
                    period_data[field] = value.decode('utf-8')
            all_periods.append(period_data)
    return all_periods


# def get_period(period):
#     """If not found, the function will return None"""
#     return db.get(period)


# Gerar o retorno esperado
def generate_return(period, incomes, expenses, comment):
    """Gera o retorno no formato desejado"""
    return [{
        "key": period,
        "incomes": incomes,
        "expenses": expenses,
        "comment": comment
    }]

# Busca os valores no banco REDIS
def get_period(period):
    # Recuperar os dados do período do Redis
    comment = db.hget(period, "comment")
    incomes_json = db.hget(period, "incomes")
    expenses_json = db.hget(period, "expenses")
    # Verificar se os dados foram encontrados
    if comment is not None and incomes_json is not None and expenses_json is not None:
        # Converter os valores de JSON de volta para dicionários Python
        comment = comment.decode('utf-8')
        incomes = json.loads(incomes_json.decode('utf-8'))
        expenses = json.loads(expenses_json.decode('utf-8'))
    else:
        print("Nenhum dado encontrado para o período", period)
    # Gerar o retorno no formato desejado
    result = generate_return(period, incomes, expenses, comment)
    # Converter o retorno em uma string JSON
    result_json = json.dumps(result)
    return result_json