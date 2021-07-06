# -*- coding: utf-8 -*-
"""
Created on Sat Jan 30 14:07:38 2021
'''Funciones para utilizar en el pre procesamiento de los datos de los mecanizados del CFRP''
@author: agust
"""
import pandas as pd
import copy
from sklearn.decomposition import PCA 

def separar_mecanizados(data): 
    
    '''Separa los mecanizados. Usa como referencia la duración 
       de cada mecanizado y el tiempo entre mecanizados.
       
    Pre: La entrada debe ser un DataFrame. Se debe filtrar el ruido.
    Post:DataFrame con cada uno de los mecanizados etiquetados
    '''     
    datafiltrada = copy.deepcopy(data)
    datafiltrada = datafiltrada[(datafiltrada.ENER>140)]
    mecanizados=[]
    dt= 0
    tc=[]
    
    for t in datafiltrada.Tiempo: #se fija cuando hay saltos de tiempos muy largos
        dt=t-dt          
        if dt>6.5 and dt<10: #Entre cada mecanizado hay un espacio temporal mayor a 6.5 pero menor a 10
            tc.append(t)
        dt=t
    tc= list(map(lambda x: x-5, tc)) # Como la condición se cumple ni bien comienza el otro mecanizado
    #nos movemos 5seg para atras así el corte cae justo en el medio de ambos mecanizados
    tcortes=[ tc[0]-6, tc[0], tc[1], tc[2], tc[2]+11] # Agrego el primer y ultimo corte 
    #(antes del primer mecanizado y despues del ultimo)
    
    for i in range(4):         
        mecanizadofiltrado = datafiltrada[(datafiltrada.Tiempo>tcortes[i]) & (datafiltrada.Tiempo<tcortes[i+1])]
        primero = mecanizadofiltrado.index[0]
        ultimo = mecanizadofiltrado.index[-1]
        mecanizado = data.iloc[primero:ultimo].copy()
        mecanizado['Mecanizado']=i+1    
        cols= mecanizado.columns.tolist()
        cols= cols[-2:]+cols[:-2] 
        mecanizado= mecanizado[cols]
        mecanizado['Tiempo'] = mecanizado['Tiempo']-min(mecanizado.Tiempo)
        
        mecanizados.append(mecanizado)


    return pd.concat(mecanizados)

def normalizar(df, columnas, metodo):
    
    '''Función que escala los datos. 
    
       Pre:
           df: DataFrame con toda la información.
           columnas a normalizar
           método que se va a utilizar 'MinMaxScaler' o 'StandardScaler'.
                      
       Post:
           Nuevo DataFrame con las columnas normalizadas
                 
    '''
    import copy
    if metodo == 'MinMaxScaler':
        from sklearn.preprocessing import MinMaxScaler
        scaler = MinMaxScaler()
    elif metodo == 'StandardScaler':
        from sklearn.preprocessing import StandardScaler     
        scaler = StandardScaler()
    
    df_norm = copy.deepcopy(df)
    
    for col in columnas:

        for n_ch in df.CH.unique():

            for mec in df.Mecanizado.unique():
                               
                index_df = df[(df.CH==n_ch) & (df.Mecanizado==mec)].index
                if len(index_df) == 0:
                    continue

                df_norm.loc[index_df, col]= scaler.fit_transform(df.loc[index_df, col].to_numpy().reshape(-1,1))
    
    return df_norm

def timezero(data): 
    '''Función para llevar a cero el indice y la columna Tiempo''' 
    #data = data.reset_index(drop=True)

    data['Tiempo'] = data['Tiempo'] - data['Tiempo'][data.index[0]] 
    return data

def separar_etapas(data, columna): 
    '''
    Etiqueta las estapas de agujereado y fresado
    
    Pre: dataframe y la columna que indica el mecanizado. 
    Post: dataframe con una nueva columna indicando la etapa   
    '''
    
    n = data[columna].value_counts().count()
    res_Aguj = []
    res_Fres = []
    for i in range(1,n+1):
        data_time = copy.deepcopy(data[data[columna]== i])
        data_time = timezero(data_time)
        
        Agujereado_index = data_time[data_time.Tiempo<0.6].index
        Fresado_index = data_time[(data_time.Tiempo>=0.6)].index

        dat_Aguj = data.loc[Agujereado_index].copy()
        dat_Fres = data.loc[Fresado_index].copy()
        
        dat_Aguj['Etapa']='Agujereado'
        dat_Fres['Etapa']='Fresado'
        
        res_Aguj.append(dat_Aguj)        
        res_Fres.append(dat_Fres)    
    
    return pd.concat([pd.concat(res_Aguj), pd.concat(res_Fres)])

    


def cortar(data, lista): 
    '''
    Función para extraer un conjunto de
    datos a partir de un intervalo de tiempo.   
    
    Pre: dataframe e intervalo de tiempo [a,b]. 
    Post: dataframe del intervalo de tiempo.   
    
    '''
    import copy
    n = data['Mecanizado'].value_counts().count()
    res = []
    
    if n==1:
        
        data_time = copy.deepcopy(data)       
        _index = data_time[(data_time.Tiempo>=lista[0]) & (data_time.Tiempo<=lista[1])].index
        dat_ = data.loc[_index].copy()
                
        return dat_     
    
    else:
        
        for i in range(1,n+1):
            
            data_time = copy.deepcopy(data[data['Mecanizado']== i])
            _index = data_time[(data_time.Tiempo>=lista[0]) & (data_time.Tiempo<=lista[1])].index
            dat_ = data.loc[_index].copy()
            
            res.append(dat_)           

    return pd.concat(res)

def pca(datos, columnas):
    '''Función para aplicar PCA a los datos
    
    Pre: Lista con 3 DataFrame. Uno por cada condición de la herramienta
    Post: DataFrame con las PC '''
    if type(datos) == pd.DataFrame:
        X_df = datos
        
        X_df = datos.reset_index(drop=True)
    
    else:
        X_df = pd.concat([datos[0], datos[1], datos[2]])
        X_df = X_df.reset_index(drop=True)
    
    X = X_df[columnas].to_numpy()
    
    n_comp = len(columnas)
    
    pca_model = PCA(n_components = n_comp )
    pca_model.fit(X)
    
    X_pca = pca_model.transform(X)
    
    col = []
    for i in range(1,n_comp+1):
        col.append('CP'+str(i))
        
    pc_df= pd.DataFrame(data=X_pca, columns=col)
    pc_df['Herramienta']=X_df['Herramienta']
    pc_df['Mecanizado']=X_df['Mecanizado']
    pc_df['CH'] = X_df['CH']
    pc_df['Etapa'] = X_df['Etapa']
    
    return pc_df, pca_model