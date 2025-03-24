# -*- coding: utf-8 -*-
"""
Created on Fri Jul  8 09:32:34 2022

@author: robson
"""
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

data = xr.open_mfdataset(r'caminho para a sua pasta do Merra\*.nc4')

#%%
lon = data.variables['lon'][:]
lat = data.variables['lat'][:]
lon,lat = np.meshgrid(lon,lat)
var = np.array(data.variables['BC OU SO2 SMASS'][0,:,:])
lon2D = lon.flatten()
lat2D = lat.flatten()
var2D = pd.DataFrame(var.flatten()).rename(columns={0:'BC OU SO2'})
geo_pol = gpd.GeoDataFrame(var2D,geometry=gpd.points_from_xy(lon2D,lat2D),crs='EPSG:4326')
br_vetor = gpd.read_file(r'caminho para o shape separado por estado')
etd = br_vetor[br_vetor['COLUNA COM A SIGLA DO ESTASDO'] == 'SIGLA DO ESTADO']
pol_etd = gpd.sjoin(geo_pol,etd)
pol_etd = pd.DataFrame(pol_etd['BC OU SO2'])
pol_etd.reset_index(inplace=True,drop=True)
for i in range(1,len(np.array(data.variables['BC OU SO2 SMASS'][:,0,0]))):
    var = np.array(data.variables['BC OU SO2 SMASS'][i,:,:])
    var2D = pd.DataFrame(var.flatten()).rename(columns={0:i})
    geo_pol = gpd.GeoDataFrame(var2D,geometry=gpd.points_from_xy(lon2D,lat2D),crs='EPSG:4326')
    etd = br_vetor[br_vetor['COLUNA COM A SIGLA DO ESTASDO'] == 'SIGLA DO ESTADO']
    pol_temp = gpd.sjoin(geo_pol,etd)
    pol_temp.reset_index(inplace=True,drop=True)
    pol_etd = pol_etd.join(pol_temp[i])
pol_etd = pol_etd.mean()
pol_etd.reset_index(inplace=True,drop=True)