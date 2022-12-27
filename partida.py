# -*- coding: utf-8 -*-
"""
Created on Tue dez 02 20:42:21 2022

@author: Erike Simon
"""
# import das bibliotecas
import pandas as pd
import numpy as np
import random
from scipy.stats import poisson
import streamlit as st

# Configurações iniciais

# 'selecoes' e 'jogos' são do tipo Series
selecoes = pd.read_excel('C:/Users/Erike Simon/Documents/repos/projeto_copa2022/DadosCopaDoMundoQatar2022.xlsx', sheet_name ='selecoes', index_col = 0) # 'index_col = 0' indica o número da coluna
                                                                                                  # que deve ser utilizada com índice ao carregar
                                                                                                  # o arquivo. nesse caso, índice 0 = 'selecoes'
jogos = pd.read_excel('C:/Users/Erike Simon/Documents/repos/projeto_copa2022/DadosCopaDoMundoQatar2022.xlsx', sheet_name ='jogos')

# As duas estruturas de dados principais que a biblioteca pandas utiliza são: DataFrame e Series. O DataFrame é uma estrutura
# bidimensional com linhas e colunas nomeadas, similar a uma tabela SQL. Já a estrutura Series é um array
# nomeado e unidimensional. As chaves (nomes) dos valores no Series são referenciados como index, e ambas as estruturas são capazes
# de armazenar qualquer tipo de dados (inteiro, string, float, objetos, etc.)

# Ajuste de força dos 'PontosRankingFIDA' de cada seleção através de uma transformação linear de escala numérica
fifa = selecoes['PontosRankingFIFA'] # A variável 'fifa' é atribuido os valores da coluna 'PontosRankingFIFA'

a, b = min(fifa), max(fifa)
fa, fb = 0.15, 1
b1 = (fb - fa)/(b-a) # Coeficiente angular do ajuste
b0 = fb - b*b1       # Coeficiente linear do ajuste
forca = b0 + b1*fifa # Função de força ajustada. 'forca' também é do tipo 'Series'

forca.sort_values(ascending = False) # Ordena dados da seleção mais forte para a menos forte

# Funções para cálculo do resultado de uma única partida entre duas seleções (selecao1, selecao2)

# Função que define a média da ocorrência de gols das seleções
def MediasPoisson(selecao1, selecao2):
    forca1 = forca[selecao1]            # 'selecao1' e 'selecao2' são as chaves da Series 'forca', que é um Array, como já mencionado. os valores das forças são os valores
    forca2 = forca[selecao2]            # das chaves 'selecao1' ou 'selecao2'

    mgols = 2.75                        # Taxa de ocorrência, esperança, frequência média ou esperada... das copas
    l1 = mgols*forca1/(forca1 + forca2) # Média de gols da 'selecao1'
    l2 = mgols*forca2/(forca1 + forca2) # Média de gols da 'selecao2' | poderia ser: l2 = mgols - l1, pois l1+l2 = mgols
    return [l1, l2]                     # Já retorna em formato de lista

# Chamada dentro da função Pontos(), onde os parâmetros gols1 e gols2 são gerados dentro da função Pontos()
def Resultado(gols1, gols2):
    if gols1 > gols2:
        res = 'V'
    if gols1 < gols2:
        res = 'D'
    if gols1 == gols2:
        res = 'E'
    return res

# Função que através do número de gols, define se a selecao1 vendeu, perdeu ou empatou com a selecao2
def Pontos(gols1, gols2):
    rst = Resultado(gols1, gols2)  # Atribui a 'rst' o resultado da partida através da função Resultado()

    if rst == 'V':                 # Condicionais para armazenar a pontuação feita em cada partida. A comparação do resultado é feita em referência a seleção1.
        pontos1, pontos2 = 3, 0    # Por exemplo, se 'rst' ='V', significa que a fez mais gols e venceu a partida. Logo, pontos1 = 3 (selecao1), pontos2 = 0 (selecao2)
    if rst == 'E':
        pontos1, pontos2 = 1, 1
    if rst == 'D':
        pontos1, pontos2 = 0, 3
    return pontos1, pontos2, rst

# Função para simulações de jogos (função mestra)
def Jogo(selecao1, selecao2):
    l1, l2 = MediasPoisson(selecao1, selecao2)             # Atribui a l1 e l2 as médias de gols calculadas na função MediasPoisson
    gols1 = int(np.random.poisson(lam = l1, size = 1))     # Parâmetro 'lam' é o número esperado de eventos (gols) da 'selecao1' ou 'selecao2' ocorrendo
    gols2 = int(np.random.poisson(lam = l2, size = 1))     # em um intervalo de tempo fixo. Deve ser >= 0. Por exemplo, para l1 = 1.9 como valor esperado,
                                                           # uma única amostra de número (size = 1) será gerada em uma distriuição do tipo Poisson.
                                                           # A amostra numérica é arredondada pelo int()

    saldo1 = gols1 - gols2                                 # Saldo de gols da seleco1 na partida
    saldo2 = -saldo1                                       # saldo de gols da seleco2 na partida
    pontos1, pontos2, result = Pontos(gols1, gols2)        # Chamada da função Pontos() para guardar a pontuação das seleções na partida
    placar = '{}x{}'.format(gols1, gols2)
    # Retorna numa lista todos os dados de uma partida
    return [gols1, gols2, saldo1, saldo2, pontos1, pontos2, result, placar] # Retorna numa lista todos os dados de uma partida

# Funções para calcular a tabela de distribuição de probabilidades para possíveis placares entre duas seleções

def Distribuicao(media):
    probs = []
    for i in range(7):                     # Range de 7, para considerar placar de até 7 gols
        probs.append(poisson.pmf(i,media)) # Função poisson.pmf() calcula os valores de uma distribuição poisson para uma dada média e um dado valor 'i'.
                                           # O for() vai adicionar na lista 'probs' os valores da distribuição poisson gerados por 'poisson.pmf()'
    probs.append(1-sum(probs))             # Adiciona por último o valor da probabilidade da ocorrência de 7+ gols, que é 1 - soma de todas as
                                           # probabilidades da lista 'probs'
    return pd.Series(probs, index = ['0', '1', '2', '3', '4', '5', '6', '7+']) # Transforma a lista 'probs' para o tipo 'Series' e atribui índices, que indicam os gols

def ProbabilidadesPartida(selecao1, selecao2):
    l1, l2 = MediasPoisson(selecao1, selecao2)          # Atribui valores a l1 e l2 chamando a função MediasPoisson()
    d1, d2 = Distribuicao(l1), Distribuicao(l2)         # Atribui a d1 e d2 a distribuição poisson, para médias l1 e l2, através da função 'Distribuição()'

    matriz = np.outer(d1, d2)                           # Monta a matriz de probabilidades. Função outer() faz um produto vetorial entre d1 e d2
                                                        #  Usar pd.DataFrame(np.outer(d1, d2)) para uma melhor visualização da matriz

    vitoria = np.tril(matriz).sum()-np.trace(matriz)    # Soma a triangulo inferior 'np.tril()'. 'np.trace()' calcula a soma dos elementos diagonais da matriz (empate)
    derrota = np.triu(matriz).sum()-np.trace(matriz)    # Soma a triangulo superior 'np.triu()'. Distribuição de gols da selecao1 é referenciada por 'd1', por isso 'np.tril()'
    empate = 1 - (vitoria + derrota)                    # ou empate = np.trace(matriz)

    probs = np.around([vitoria, empate, derrota], 3)    # 'np.Around()' arredonda os valores da lista 'probs', com 3 casas decimais
    probsp = [f'{100*i:.1f}%' for i in probs]           # Multiplica cada valor da lista 'probs' por 100, para ter o valor das probabilidades %

    nomes = ['0', '1', '2', '3', '4', '5', '6', '7+']                           # Será utilizada como índices
    matriz = pd.DataFrame(matriz, columns = nomes, index = nomes)               # Transforma a matriz em um dataframe
    matriz.index = pd.MultiIndex.from_product([[selecao1], matriz.index])       # Torna a seleção 1 como índice. 'pd.MultiIndex().from_product()' cria dois índices
    matriz.columns = pd.MultiIndex.from_product([[selecao2], matriz.columns])   # Torna a seleção 2 como coluna

    output = {'Seleção 1': selecao1, 'Seleção2': selecao2,
             'força 1': forca[selecao1], 'força 2': forca[selecao2],
             'Média gols 1': l1, 'Média gols 2': l2,
             'Probabilidades': probsp, 'Probabilidade de placares': matriz}     # 'output' é um dicionário
    return output

# Tarefa 1: previsões dos jogos da copa

# Criação de três novas colunas no sheet_name 'jogos'
jogos['vitória'] = None
jogos['empate'] = None
jogos['derrota'] = None

# laço para verificar as probabilidades dos jogos no sheet 'jogos', onde o 'i' vai acessar cada uma das linhas do conjunto de dados
for i in range(jogos.shape[0]):                                             # A função shape() vai retornar o número de linhas e colunas de uma matriz. O índice '0' recupera as linhas apenas
    selecao1 = jogos['seleção1'][i]                                         # 'selecao1' será do conjunto de dados 'jogos', a coluna 'seleção1' e a linha 'i'
    selecao2 = jogos['seleção2'][i]
    v, e, d = ProbabilidadesPartida(selecao1, selecao2)['Probabilidades']   # Do output da função 'ProbabilidadesPartida()', pegamos 'probabilidades' (que é a lista 'porbsp') e armazenamos
                                                                            # em 'v', 'e' e 'd'

    jogos.at[i,'vitória'] = v                                               # Use DataFrame.at[posição da linha, nome da coluna] se você precisar apenas obter ou definir um único
    jogos.at[i,'empate'] = e                                                # valor em um DataFrame ou Series. No caso em questão, além de obter o valor, estamos atribuindo 'v', 'e' ou 'd'
    jogos.at[i,'derrota'] = d

jogos.to_excel('C:/Users/Erike Simon/Documents/repos/projeto_copa2022/outputEstimativasJogosCopa.xlsx', index = False)            # Salva um arquido .xlsx com os dados e porcentagem implementados

# INICIO DO APP

st.title('Previsão Estatística dos Jogos da Copa 2022')

listaselecoes1 = selecoes.index.tolist()
listaselecoes1.sort()
listaselecoes2 = listaselecoes1.copy()

j1, j2 = st.columns(2)

selecao1 = j1.selectbox('Escolha a primeira seleção', listaselecoes1)
listaselecoes2.remove(selecao1)

selecao2 = j2.selectbox('Escolha a segunda seleção', listaselecoes2, index = 1)
st.markdown('---')

jogo = ProbabilidadesPartida(selecao1, selecao2)
prob = jogo['Probabilidades']
matriz = jogo['Probabilidade de placares']

col1, col2, col3, col4, col5 = st.columns(5)
col1.image(selecoes.loc[selecao1, 'LinkBandeiraGrande'])  
col2.metric(selecao1, prob[0])                              # 'metric' é uma maneira de por infos em dashboard
col3.metric('Empate', prob[1])                              # parâmetros .metric(nome da metrica, valor da métrica)
col4.metric(selecao2, prob[2]) 
col5.image(selecoes.loc[selecao2, 'LinkBandeiraGrande'])

st.markdown('---')
st.markdown("## 📊 Probabilidades dos Placares") 

def aux(x):
	return f'{str(round(100*x,2))}%'
st.table(matriz.applymap(aux))          # .applymap(aux) aplica valor de % em todos os valores da matriz


st.markdown('---')
st.markdown("## 🌍 Probabilidades dos Jogos da 1 ª Fase") 

jogoscopa = pd.read_excel('C:/Users/Erike Simon/Documents/repos/projeto_copa2022/outputEstimativasJogosCopa.xlsx', index_col = 1)
st.table(jogoscopa[['grupo', 'seleção1', 'seleção2', 'vitória', 'empate', 'derrota']])


st.markdown('---')
st.markdown('Trabalho desenvolvido no Minicurso FLAI Data Science na Copa do Mundo!')

#bandeira1, nome1, prob, empate, prob, nome2, bandeira2
#matriz de probabilidades do jogo
#placar mais provável
