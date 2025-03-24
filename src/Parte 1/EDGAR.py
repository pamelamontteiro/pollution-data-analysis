import xarray as xr #importação de arquivos netCDF
import numpy as np #manipulação de arranjos
import pandas as pd #manipulação de dataframe 
import geopandas as gpd #manipulação e plotagem da dataframes georreferenciado
import matplotlib as mpl #normalização para plotagem 
import matplotlib.pyplot as plt #plotagem 

#%%

### LEITURA DOS ARQUIVOS EM NETCDF

#leitura dos dados em nc 
data = xr.open_mfdataset(r'/home/Trabalho/MERRA/*.nc4')

#%%

### EXTRAINDO ARRANJOS DO ARQUIVO NETCDF


#extraindo array de lon e last 
lon = np.array(data.variables['lon'][:])
lat = np.array(data.variables['lat'][:])

#criando array com lon e lat 
lon,lat = np.meshgrid(lon,lat)

#extraindo arranjo com concentraçoes de BC para todas as combinações de lon e lat
BC2015 = np.array(data.variables['BCSMASS'][0:12,:,:]).mean(axis=0)

#extraindo variáveis em dimensão única para criar geodataframe
lon = pd.DataFrame(lon.flatten()).rename(columns={0:'lon'})
lat = pd.DataFrame(lat.flatten()).rename(columns={0:'lat'})
BC_2015 = pd.DataFrame(BC2015.flatten()*1000000000).rename(columns={0:'BC_2015'})

#concateando geodataframe com concentrações de BC anuais e geometrias
BC = pd.concat([BC_2015],axis=1)

print(lon)
print(lat)


#%%

#%%

#leitura de arquivos shape Piaui
ce2 = gpd.read_file('/home/Trabalho/brasilshape/gadm40_BRA_1.shp')
ce3 = ce2[ce2['HASC_1']=='BR.CE']

#recortando os dados da Geoframe do estado do Piauí

#leitura dos arquivos shape
ce = gpd.read_file('/home/Trabalho/CE_shape/CE.shp')
ce_edgar_veicular = gpd.read_file('/home/Trabalho/veicular/veicular.shp')
ce_edgar_ind = gpd.read_file('/home/Trabalho/EmissaoBC/emissao.shp')

#criando geodataframe com concentraçoes de BC anuais e geometrias
geo_BC = gpd.GeoDataFrame(BC,geometry=gpd.points_from_xy(lon,lat))


ceara_ = gpd.sjoin(geo_BC,ce)
CE_BC_VEI = gpd.sjoin(ce_edgar_veicular,ce3)
CE_BC_IND = gpd.sjoin(ce_edgar_ind,ce3)

CE_BC_VEI.plot()
CE_BC_IND.plot()
ce.plot()

###TRABALHANDO COM DADOS ANUAIS  PARA ENCONTRAR ÁREAS PRIORITARIAS NO ESTADO DO CEARA

#Verificando indices dos 5 maiores valores de concentraçao do ceara 
max_val_2015 = ceara_['BC_2015'].nlargest(5)
max_val_2015_veicular = CE_BC_VEI['1'].nlargest(5)
max_val_2015_ind = CE_BC_IND['1'].nlargest(5)

#gerando novo df apenas com pixels encontrados acima 
geo_max_v = ceara_.iloc[ceara_.index.isin([4545,4544,4478,4477,4409])]
geo_max_v_veiculares = CE_BC_VEI.iloc[CE_BC_VEI.index.isin([1203, 1204, 1250, 1202, 1251])]
geo_max_v_industriais = CE_BC_IND.iloc[CE_BC_IND.index.isin([6026,5865,5041,5864,6027])]

geo_max_v_veiculares.centroid.plot()
geo_max_v_industriais.centroid.plot()

#plotando os pixels em areas prioritarias do ceara
ax = plt.gca()
geo_max_v_veiculares.centroid.plot(ax=ax,color='r',markersize=50)
geo_max_v_industriais.centroid.plot(ax=ax,color='b',markersize=50,marker='^')
geo_max_v.plot(ax=ax)
ce.boundary.plot(ax=ax,linewidth=.0,color='m')


linha_veiculares = np.transpose(geo_max_v_veiculares[geo_max_v_veiculares.columns[0:12]])
linha_veiculares.plot()

linha_industriais = np.transpose(geo_max_v_industriais[geo_max_v_industriais.columns[0:12]])
linha_industriais.plot()


#%%


###TRABALHANDO COM DADOS MENSAIS PARA PLOTAR GRÁFICO DE LINHAS

#extraindo valores mensais da variável do arquivo netCDF
BC_mes = []

for i in range (0,12):
    bc_m = pd.DataFrame(np.array(data.variables['BCSMASS'][i,:,:]*1000000000).flatten())
    BC_mes.append(bc_m)

#concateando listas em um dataframe
BC_mes = pd.concat(BC_mes,axis=1)


#transposta para indexar o tempo corretamente 
BC_mes = np.transpose(BC_mes)

#indexando período de tempo correto 
BC_mes = BC_mes.set_index(pd.date_range(start='2015-01-01',end='2015-12-31',freq='M'))

#transposta para deixar os pixels no indice e usar a mesma tecnica de seleção
#áreas prioritarias 
BC_mes = np.transpose(BC_mes)

#Gerando novo df apenas com indices das AP 
#encontrando aneriormente a partir das medias anuais 
max_val_mes = BC_mes.iloc[BC_mes.index.isin([3553,3623,3624,3622,3552])]

max_val_mes = np.transpose(max_val_mes)

#plotando o grafico
max_val_mes.plot(marker='o',markersize=4)
plt.title('medias mensais BC - áreas Prioritárias Ceará')
plt.ylabel('BC(ug/m3)')

BC_mes.max()

#%%


###TRABALHANDO COM DADOS MENSAIS PARA PLOTAR GRÁFICO DE LINHAS

#extraindo valores mensais da variável do arquivo netCDF
BC_mes_veiculares = []

for i in range (0,12):
    BC_m_veiculares = pd.DataFrame(np.array(data.variables['BCSMASS'][i,:,:]*1000000000).flatten())
    BC_mes_veiculares.append(BC_m_veiculares)

#concateando listas em um dataframe
BC_mes_veiculares = pd.concat(BC_mes_veiculares,axis=1)


#transposta para indexar o tempo corretamente 
BC_mes_veiculares = np.transpose(BC_mes_veiculares)

#indexando período de tempo correto 
BC_mes_veiculares = BC_mes_veiculares.set_index(pd.date_range(start='2015-01-01',end='2015-12-31',freq='M'))

#transposta para deixar os pixels no indice e usar a mesma tecnica de seleção
#áreas prioritarias 
BC_mes_veiculares = np.transpose(BC_mes_veiculares)

#Gerando novo df apenas com indices das AP 
#encontrando aneriormente a partir das medias anuais 
max_val_mes_veiculares = BC_mes_veiculares.iloc[BC_mes_veiculares.index.isin([1840,1841,832,1914,1915])]

max_val_mes_veiculares = np.transpose(max_val_mes)

#plotando o grafico
max_val_mes.plot(marker='o',markersize=4)
plt.title('medias mensais BC - áreas Prioritárias CEARÁ')
plt.ylabel('BC(ug/m3')

BC_mes.max()

#%%


###TRABALHANDO COM DADOS MENSAIS PARA PLOTAR GRÁFICO DE LINHAS

#extraindo valores mensais da variável do arquivo netCDF
BC_mes_industriais = []

for i in range (0,12):
    BC_m_industriais = pd.DataFrame(np.array(data.variables['BCSMASS'][i,:,:]*1000000000).flatten())
    BC_mes_industriais.append(BC_m_industriais)

#concateando listas em um dataframe
BC_mes_industriais = pd.concat(BC_mes_industriais,axis=1)


#transposta para indexar o tempo corretamente 
BC_mes_industriais = np.transpose(BC_mes_industriais)

#indexando período de tempo correto 
BC_mes_industriais = BC_mes_industriais.set_index(pd.date_range(start='2015-01-01',end='2015-12-31',freq='M'))

#transposta para deixar os pixels no indice e usar a mesma tecnica de seleção
#áreas prioritarias 
BC_mes_industriais = np.transpose(BC_mes_industriais)

#Gerando novo df apenas com indices das AP 
#encontrando aneriormente a partir das medias anuais 
max_val_mes_industriais = BC_mes_industriais.iloc[BC_mes_industriais.index.isin([3553,3623,3624,3622,3552])]

max_val_mes_industriais = np.transpose(max_val_mes_industriais)


ax = plt.gca()
geo_max_v.plot(ax=ax,color='g',marker='s')
geo_max_v_veiculares.centroid.plot(ax=ax,color='r',marker='o')
geo_max_v_industriais.plot(ax=ax,color='b',marker='^')
ce.boundary.plot(ax=ax,linewidth=.3,color='m')
