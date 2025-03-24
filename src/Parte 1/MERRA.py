#CONTROLE DE POLUIÇÃO ATMOSFERICA
#ALUNA: PAMELA MONTEIRO
#%%
#IMPORTAÇÃO DAS BIBLIOTECAS:
#from mpl_toolkits.basemap import Basemap #plotagem dos arquivos netCDF
import pandas as pd #manipulação de dataframes
import geopandas as gpd #manipulação e plotagem de dataframes georreferenciada
import xarray as xr #importacao de arquivos netCDF
import numpy as np #manipulaçao de arranjos
import matplotlib.pyplot as plt #plotagem
from mpl_toolkits.basemap import Basemap
import matplotlib as mpl
#from shapely.geometry import Polygon #criacao de poligono
#import irregularGrid as iG #importando funcao pronta para criar grid irregular

#%%
#Leitura dos arquivos em METCDF
#Leitura dos dados em mc

data = xr.open_mfdataset('/home/Trabalho/MERRA/*.nc4', engine= 'netcdf4')

#É NECESSARIO ALTERAR O CAMINHO PARA A PASTA DO "MERRA"

#%%

#EXTRAINDO ARRANJOS DO ARQUIVO NETCDF

#extraindo array de lon e lat
lon = np.array(data.variables['lon'][:])
lat = np.array(data.variables['lat'][:])

#criando arrau com lon e lat
lon, lat = np.meshgrid(lon,lat)

#extraindo arranjo com concentracoes de BC para todas as combinações de lon e la
bc2015 = np.array(data.variables['BCSMASS'][0:12,:,:]).mean(axis = 0)

#plotando a variavel em 2015 para todas as combinações de lon e lat
plt.figure()  
m = Basemap()
m.drawcoastlines()
m.drawcountries()
c = m.pcolor(lon,lat,bc2015, cmap= 'jet')
m.colorbar(c)
type(lon)

#%%

##EXTRAINDO TODAS AS COMBINAÇÕES DO ARRANJO EM LINHAS UNICAS E CRIANDO GEODATAFRAMES
lon = pd.DataFrame(lon.flatten()).rename(columns ={0:'lon'})
lat = pd.DataFrame(lat.flatten()).rename(columns ={0:'lat'})
bc2015 = pd.DataFrame(bc2015.flatten()*1000000000).rename(columns={0: 'bc_2015'})

#concatenando em colunas as medias de concentrações anuais
bc = pd.concat([bc2015], axis = 1)

#criando geodataframe com concentrações de BC anuais e geometrias (grade pontos)
geo_bc = gpd.GeoDataFrame(bc, geometry=gpd.points_from_xy(lon,lat),crs='EPSG:4326')

#%%

#RECORDANDO OS DADOS DO GEODATAFRAME PARA O ESTADO DO CEARÁ

#leitura de arquivos shapefile do Brasil
ce = gpd.read_file('/home/Trabalho/CE_shape/')

# #separando geometria do Ceará
# ce = bra[bra['HASC_1'] == 'BR.CE']

#recortando os dados do geodataframe para oe stado do Ceará (ce)
ce_bc = gpd.sjoin(geo_bc, ce)

ce.plot()
ce_bc.plot()

#%%

#TRABALHANDO COM DADOS ANUAIS PARA ENCONTRAR AREAS PRIORITARIAS NO ESTADO DO CEARA

#Verificando indices do 5 maiores valores de concentração no Ceará
max_val_2015 = ce_bc['bc_2015'].nlargest(5)

#gerando novo df apenas com pixels encontrados acima
geo_max_v = ce_bc.iloc[ce_bc.index.isin([4545, 4544, 4478, 4477, 4409])]
#NECESSARIO ALTERAR OS NUMEROS ACIMA POIS SAO INDICES INDICADAS PARA O AMAZONAS

ax = plt.gca()
geo_max_v.plot('bc_2015', ax=ax)
ce.boundary.plot(ax=ax)
ce.boundary.plot(ax=ax, linewidth= .0, color= 'm')
#%%

#TRABALHANDO COM DADOS MENSAIS PARA PLOTAR GRAFICO DE LINHAS

#Extraindo valores mensais da variavel do arquivo netCDF
bc_mes = []
for i in range(0,12):
    bc_m = pd.DataFrame(np.array(data.variables['BCSMASS'][i,:,:]*1000000000).flatten())
    bc_mes.append(bc_m)

#concatenando listas em um dataframe
bc_mes = pd.concat(bc_mes, axis=1)

#transposta para indexar o tempo corretamente
bc_mes = np.transpose(bc_mes)

#indexando periodo de tempo correto
bc_mes = bc_mes.set_index(pd.date_range(start='2015-01-01', end='2015-12-31', freq= 'M'))

#transposta para deixar os pixels no indece e usar a mesma tecnica de seleção
#areas prioritarias
bc_mes = np.transpose(bc_mes)

#gerando novo df apenas com indices dos pixels das areas prioritarias
#encontrados anteriormente a partir das medias anuais
max_val_mes = bc_mes.iloc[bc_mes.index.isin([4545, 4544, 4478, 4477, 4409])]
#NECESSARIO ALTERAR OS NUMEROS ACIMA POIS SAO INDICES INDICADOS PARA O AMAZONAS

#transposta para facilitar a plotagem
max_val_mes = np.transpose(max_val_mes)

#plotando grafico de linhas com comportamento temporal dos max_val
max_val_mes.plot(marker='o', markersize=4)
plt.title('medias mensais BC - áreas prioritárias CEARÁ')
plt.ylabel('BC (ug/m3)')

#%%

#plotando mapa com areas prioritarias e lineplot com comportamento mensal necessarios

#normalização da colorbar e colormap
norm = mpl.colors.Normalize(vmin=1.243391, vmax=2.221333)
cbar = mpl.cm.ScalarMappable(norm=norm, cmap='jet')

#Plot medias mensais
ax=plt.subplot(121)
max_val_mes.plot(ax=ax, marker='o', markersize=4)
plt.title('Médias mensais BC = áreas prioritárias CEARÁ')
plt.ylabel('BC (ug/m3)')

#Plot estados BR
ax1 = plt.subplot(222)
geo_max_v.plot('bc_2015', ax=ax1)
ce.boundary.plot(ax=ax1, linewidth=.5, color='c')
plt.axis('off')

#Plot municipios BR
ax2 = plt.subplot(224)
geo_max_v.plot('bc_2015', ax=ax2)
ce.boundary.plot(ax=ax2, linewidth=.3, color='m')
plt.colorbar(cbar)
plt.axis('off')
plt.title('Media Anual 2015')

#%%