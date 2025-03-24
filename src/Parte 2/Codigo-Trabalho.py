
#POLUIÇÃO ATMOSFERICA AVALIAÇÃO 
#%%
import xarray as xr
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn import preprocessing
import statsmodels.api as sm
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf  
from statsmodels.tsa.arima.model import ARIMA


#%%

data = xr.open_mfdataset(r'/home/arquivos_trab/MERRA/*.nc4')

#%%  #criando um arquivo para o Estado do Ceará
lon = data.variables['lon'][:]
lat = data.variables['lat'][:]
lon,lat = np.meshgrid(lon,lat)
var = np.array(data.variables['BCSMASS'][0,:,:])
lon2D = lon.flatten()
lat2D = lat.flatten()
var2D = pd.DataFrame(var.flatten()).rename(columns={0:'pol'})
geo_pol = gpd.GeoDataFrame(var2D,geometry=gpd.points_from_xy(lon2D,lat2D),crs='EPSG:4326')
br_vetor = gpd.read_file(r'/home/arquivos_trab/SHAPE/gadm36_BRA_1.shp')
estado = br_vetor[br_vetor['HASC_1'] == 'BR.CE']
pol_estado = gpd.sjoin(geo_pol,estado)
pol_estado = pd.DataFrame(pol_estado['pol'])
pol_estado.reset_index(inplace=True,drop=True)


#%%  #Juntar o Dado de Cada um dos meses

for i in range(1,len(np.array(data.variables['BCSMASS'][:,0,0]))):
    var = np.array(data.variables['BCSMASS'][i,:,:])
    var2D = pd.DataFrame(var.flatten()).rename(columns={0:i})
    geo_pol = gpd.GeoDataFrame(var2D,geometry=gpd.points_from_xy(lon2D,lat2D),crs='EPSG:4326')
    estado = br_vetor[br_vetor['HASC_1'] == 'BR.CE']
    pol_temp = gpd.sjoin(geo_pol,estado)
    pol_temp.reset_index(inplace=True,drop=True)
    pol_estado = pol_estado.join(pol_temp[i])
pol_estado = pol_estado.mean()
pol_estado.reset_index(inplace=True,drop=True)


#%% carregar os dados de obitos e calcular mortalidade

#carregar dados
mort_cardio = pd.read_csv(r'/home/arquivos_trab/CARDIO_CE.csv')
#criar nova coluna e calcular taxa de mortalidade
mort_cardio['taxa_mort_cardio'] = (mort_cardio['AIH_aprovadas']/mort_cardio['POP'])*10000
#fazer copia da tabela
mort_pol =  mort_cardio.copy()
#Acrescenta uma nova coluna na tabela e armazena os dados de poluição (ajustanto a unidade)
mort_pol['pol'] = pol_estado*(10**9)
#Transforma a tabela para numpy 
pol_norm = mort_pol['pol'].to_numpy().reshape(-1, 1) 
#Carrega a transformação BOX-COX
box = preprocessing.PowerTransformer(method='box-cox')
#Normaliza os dados com BOX-COX
pol_norm = box.fit_transform(pol_norm)
#Carrega a transformação Min Max (padronização)
min_max_scaler = preprocessing.MinMaxScaler(feature_range = (0,1))
#Aplica a transformação Min Max
pol_norm = min_max_scaler.fit_transform(pol_norm)

#%%
#Acrescenta uma nova coluna na tabela e armazena os dados normalizados e padronizados
mort_pol['pol_norm'] = pol_norm.copy()
#Armazena as colunas de taxa de mortalidade e poluição normalizada em novas variáveis
mortes = mort_pol['taxa_mort_cardio'].to_numpy().copy()
pol_normalizado = mort_pol['pol_norm'].to_numpy().copy()
#Carrega a regressão de Poisson
possion_model = sm.GLM(mortes, pol_normalizado, family=sm.families.Poisson())
#Aplicando a regressão
poisson_results = possion_model.fit(cov_type='HC1')
#Armazenando os resíduos de pearson
resid_poisson= poisson_results.resid_pearson.copy()

#%%
#Plota o gráfico de autocorrelação
plot_acf(resid_poisson,zero=False)
#Plota o gráfico de autocorrelação parcial
plot_pacf(resid_poisson,zero=False)

#%%
#Carrega a autoregressão
model = ARIMA(resid_poisson, order=(1,0,0))
#Aplica a autoregressão
model_fit = model.fit()
#Plota o gráfico de autocorrelação
plot_acf(model_fit.resid,zero=False)
#Plota o gráfico de autocorrelação parcial
plot_pacf(model_fit.resid,zero=False)

#%%
#Armazenando os resíduos transformados
resid_poisson_diff = model_fit.predict()
#Ajusta os resíduos transformados para não ter números negativos 
resid_poisson_diff = (model_fit.predict() + (-(model_fit.predict().min()))+1)
#Escreve o registro transformado para o formato correto
resid_poisson_diff = resid_poisson_diff.reshape(-1, 1)


#%%
#Carrega a transformação BOX-COX
box = preprocessing.PowerTransformer(method='box-cox')
#Normaliza os resíduos transformados com BOX-COX
resid_poisson_diff = box.fit_transform(resid_poisson_diff)
#Carrega a transformação Min Max (padronização)
min_max_scaler = preprocessing.MinMaxScaler(feature_range = (0,1))
#Aplica a transformação Min Max
resid_poisson_diff = min_max_scaler.fit_transform(resid_poisson_diff)

#%%
#Concatena os dados de poluição normalizados com os resíduos transformados
dados_regressao= np.c_[pol_normalizado, resid_poisson_diff]
#Armazena as variáveis de regressão em um dataframe ( vamos usar depois)
resultados_BC = pd.DataFrame(dados_regressao.copy())
#Carrega a regressão de Poisson
possion_model = sm.GLM(mortes, dados_regressao, family=sm.families.Poisson())
#Aplicando a regressão
poisson_results = possion_model.fit(cov_type='HC1')
#Armazenando os resíduos de Pearson da nova regressão
resid_poisson2 = poisson_results.resid_pearson.copy()

#%%

#Plota o gráfico de autocorrelação
plot_acf(resid_poisson2,zero=False)
#Plota o gráfico de autocorrelação parcial
plot_pacf(resid_poisson2,zero=False)

#%%

#Armazena o pvalor da regressão de poisson
pvalue_poisson = poisson_results.pvalues
#Armazena o Beta
beta = poisson_results.params[0]
#Armazena o intervalo de confiança
CI_min = poisson_results.conf_int()[0]
CI_max = poisson_results.conf_int()[1]
#Da uma olhadinha no beta
print('Beta é igual a ' + str(beta))
#%%
#Armazena o percentil 75 e 25
q75, q25 = np.percentile(mort_pol['pol_norm'], [75 ,25])
#Calcula o delta
delta = (q75-q25)
#Da uma olhadinha no delta
print('Delta é igual a ' + str(delta))

#%%
#Armazena o percentil 75 e 25
q75, q25 = np.percentile(mort_pol['pol_norm'], [75 ,25])
#Calcula o delta
delta = (q75-q25)
#Da uma olhadinha no delta
print('Delta é igual a ' + str(delta))
#%%
#Calcula RR
RR = np.e**(beta.copy()*delta.copy())
#Da uma olhadinha no RR
print('O risco relativo é igual a ' + str(RR))
#Calcula o intervalo de confiança do RR
RR_CI_min = np.e**(CI_min.copy()*delta.copy())
RR_CI_max = np.e**(CI_max.copy()*delta.copy())
#Da uma olhadinha no intervalo de confiança
print('O risco relativo minimo é igual a ' + str(RR_CI_min[0]))
print('O risco relativo maximo é igual a ' + str(RR_CI_max[1]))
#%%