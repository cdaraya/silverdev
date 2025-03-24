#!/usr/bin/env python
# coding: utf-8

# # 1 **Importación de librerías**

# In[1]:

import pandas as pd
import numpy as np
import pyodbc
import pysftp
import holidays
import calendar
from datetime import datetime, date, timedelta
#hola

# # 2 **Definición de parámetros**

# ## 2.1 **Caso incidente**

# In[2]:


Inc = 1000000 #Clientes con provisiones totales mayor a este monto irán con marca "1"


# ## 2.2 **Fecha proceso**

# Obtener los días festivos de Chile para el año actual
festivos_chile = holidays.Chile()

# Obtener la fecha de ayer
fecha_hoy = datetime.today()
fecha_ayer = fecha_hoy - timedelta(days=1)

# Crear un rango de fechas retrocediendo un número arbitrario de días desde la fecha de ayer
rango_fechas_ayer = pd.date_range(end=fecha_ayer, periods=10)

# Iterar a través del rango de fechas para encontrar el último día hábil anterior a la fecha actual
for fecha in reversed(rango_fechas_ayer):
    # Convertir la fecha a un objeto de fecha de Python
    fecha_python = fecha.to_pydatetime()
    # Verificar si la fecha es un día hábil y no es un día festivo
    if fecha_python.weekday() < 5 and fecha_python not in festivos_chile:
        ultimo_dia_habil_anterior = fecha_python
        break

ultimo_dia_habil_anterior = datetime.combine(ultimo_dia_habil_anterior, datetime.min.time())
ultimo_dia_habil_anterior

ult_dia_mes = calendar.monthrange(ultimo_dia_habil_anterior.year, ultimo_dia_habil_anterior.month)[1]
fecha_fin_mes = ultimo_dia_habil_anterior.replace(day=ult_dia_mes)

# Crear un rango de fechas retrocediendo un número arbitrario de días desde el fin de mes según la fecha del último día hábil
rango_fechas_fin = pd.date_range(end=fecha_fin_mes, periods=10)

# Iterar a través del rango de fechas para encontrar el último día hábil del mes según la fecha del último día hábil
for fecha in reversed(rango_fechas_fin):
    # Convertir la fecha a un objeto de fecha de Python
    fecha_python = fecha.to_pydatetime()
    # Verificar si la fecha es un día hábil y no es un día festivo
    if fecha_python.weekday() < 5 and fecha_python not in festivos_chile:
        ultimo_dia_habil_mes = fecha_python
        break

ultimo_dia_habil_mes = datetime.combine(ultimo_dia_habil_mes, datetime.min.time())
ultimo_dia_habil_mes

def es_dia_habil():
    chile_holidays = holidays.Chile()
    
    return fecha_hoy.weekday() < 5 and fecha_hoy not in chile_holidays

if es_dia_habil():


    # In[4]:


    fecha_proceso = ultimo_dia_habil_anterior
    fecha_proyeccion = ultimo_dia_habil_mes
    if fecha_proyeccion == datetime(2024, 12, 31):
        fecha_proyeccion = datetime(2024, 12, 30)
    else:
        fecha_proyeccion
    #fecha_proceso = datetime(2024, 2, 8) #Actualizar a fecha de cierre
    #fecha_proyeccion = datetime(2024, 2, 29) #Actualizar a fecha de proyección


    # ## 2.3 **Resultado fecha proceso**

    # In[5]:


    print('Fecha proceso: ', fecha_proceso)
    print('Fecha proyeccion: ', fecha_proyeccion)


    # # 3 **Lectura orígenes de datos**

    # In[6]:


    nombre_archivo = 'VtosPorRangoFecha_' + str(fecha_proceso.year) + f'{fecha_proceso.month:02d}' + f'{fecha_proceso.day:02d}' + '.xlsx'
    nombre_archivo #nombre de archivo descargado desde servidor SFTP


    # In[7]:


    #Conexión a servidor SFTP y descarga de archivo a carpeta

    cnopts = pysftp.CnOpts()
    cnopts.hostkeys = None #revisar certificado sftp

    with pysftp.Connection('sftp.euro', username='jlucero@eurocapital.cl', password='QL4q/=4=W9U8', cnopts=cnopts) as sftp:

        remote_file = 'InformesCierresDiarios-Factoring/'+nombre_archivo
        local_file = nombre_archivo
        sftp.get(remote_file, local_file)


    # In[8]:


    df = pd.read_excel(nombre_archivo, decimal=',')


    # In[9]:


    mora = pd.read_excel('Inf_MORA.xlsx', decimal=',')


    # In[10]:


    cob = pd.read_excel('Garantías/Garantias.xlsx', sheet_name = 'Detalle de garantías', decimal=',')


    # In[11]:


    fam = pd.read_csv('Parámetros/Familia.csv', sep=';', encoding='UTF-8')


    # In[12]:


    PD = pd.read_csv('Parámetros/PD.csv', sep=';', encoding='UTF-8', decimal=',')


    # In[13]:


    LGD = pd.read_csv('Parámetros/LGD.csv', sep=';', encoding='UTF-8', decimal=',')


    # In[14]:


    tram = pd.read_csv('Parámetros/Tramos_cob.csv', sep=';', encoding='UTF-8', decimal=',')


    # In[15]:


    jer = pd.read_csv('Parámetros/Jerarquía.csv', sep=';', encoding='UTF-8', decimal=',')

    marcas = pd.read_csv('Marcas_pago_prórroga/Marcas.csv', sep=';', encoding='latin1', decimal=',')


    # # 4 **Ajuste de formatos**

    # In[16]:


    df['FEC_VTO'] = pd.to_datetime(df['FEC_VTO'], dayfirst=True)
    df['FEC_OPE'] = pd.to_datetime(df['FEC_OPE'], dayfirst=True)
    df['MON_FAC'] = df['MON_FAC'].replace('\.', '', regex=True)
    df['SAL_DOC'] = df['SAL_DOC'].replace('\.', '', regex=True)
    df['COD_EJE'] = df['COD_EJE'].astype(str)
    df['NUM_DOC'] = df['NUM_DOC'].astype(float)
    df['MON_FAC'] = df['MON_FAC'].astype(float)
    df['SAL_DOC'] = df['SAL_DOC'].astype(float)
    df['NOMBRE_SUCURSAL'] = df['NOMBRE_SUCURSAL'].str.rstrip()
    df['NOMBRE_EJECUTIVO'] = df['NOMBRE_EJECUTIVO'].str.rstrip()
    df.loc[df['DOC_DES'].str.contains('FAC CONFIRMING'), 'RUT_DEU'] = df.loc[df['DOC_DES'].str.contains('FAC CONFIRMING'), 'RUT_CLI']
    df.loc[df['DOC_DES'].str.contains('FAC CONFIRMING'), 'NOMBRE_DEU'] = df.loc[df['DOC_DES'].str.contains('FAC CONFIRMING'), 'NOMBRE_CLI']
    df['SEC_DEU'] = df['SEC_DEU'].fillna('Otro')


    # In[17]:


    mora['FEC.PRX.GES.'] = pd.to_datetime(mora['FEC.PRX.GES.'], dayfirst=True)
    mora = mora[['RUT CLIENTE', 'RUT DEUDOR', 'NºDOCTO.', 'COD.COB.', 'DES.COD.COB.', 'T.D.', 'OBSERVACION', 'FEC.PRX.GES.']]
    mora = mora.rename(columns={'COD.COB.': 'COD_COB', 'DES.COD.COB.': 'DES_COD_COB', 'FEC.PRX.GES.': 'FEC_PRX_GES'})

    #Estandarización tipos de documento
    mora['T.D.'] = mora['T.D.'].replace('XC', 'GC')


    marcas['Fecha_pago'] = pd.to_datetime(marcas['Fecha_pago'], format="%d/%m/%Y")
    marcas['Fecha_prórroga'] = pd.to_datetime(marcas['Fecha_prórroga'], format="%d/%m/%Y")

    ### 4.1 **Convenios Jud. a Renegociación**
    df.loc[(df['DOC_DES'] == 'CONVENIO JUDICIAL') | (df['DOC_DES'] == 'CONVENIO JUDICIAL U'), 'DOC_DES'] = 'RENEGOCIACION DEUDO'
    df.loc[(df['DOC_DES'] == 'RENEGOCIACION DEUDO'), 'TIP_DOC'] = 'C2'

    # # 5 **Cálculo garantías**

    # In[18]:


    #cob = cob[['Tipo producto', 'T/G', 'Grupo', 'Rut', 'Saldo deuda $', 'Gtía, Val liquid $']] 
    cob = cob[['Tipo producto', 'T/G', 'Rut', 'Saldo deuda $', 'Gtía, Val liquid $']] #se elimina grupo por duplicidad
    cob = cob[cob['Tipo producto'].str.contains('|'.join(['FACTORING', 'CREDITO', 'CONFIRMING', 'COMEX']))]
    cob['Rut'] = cob['Rut'].replace('\.', '', regex=True)
    cob['T/G'] = cob['T/G'].str.strip()
    cob['T/G'] = [ "G" if s == "E/G" else "G" if s == "G/E" else s for s in cob['T/G'] ]


    # In[19]:


    cob_g = cob[cob['T/G'] == 'G']
    cob_e = cob[cob['T/G'] == 'E']


    # In[20]:


    #cob_g = cob_g.groupby(['Rut', 'Grupo']).agg({'Saldo deuda $': 'sum', 'Gtía, Val liquid $': 'sum'}).reset_index()
    cob_g = cob_g.groupby(['Rut']).agg({'Saldo deuda $': 'sum', 'Gtía, Val liquid $': 'sum'}).reset_index() #se elimina grupo por duplicidad
    cob_g = cob_g.rename(columns={'Saldo deuda $': 'DEUDA_GENERAL', 'Gtía, Val liquid $': 'TASACION_GENERAL'})
    #cob_e = cob_e.groupby(['Rut', 'Grupo']).agg({'Saldo deuda $': 'sum', 'Gtía, Val liquid $': 'sum'}).reset_index()
    cob_e = cob_e.groupby(['Rut']).agg({'Saldo deuda $': 'sum', 'Gtía, Val liquid $': 'sum'}).reset_index() #se elimina grupo por duplicidad
    cob_e = cob_e.rename(columns={'Saldo deuda $': 'DEUDA_ESPECIFICA', 'Gtía, Val liquid $': 'TASACION_ESPECIFICA'})


    # In[21]:


    cob_e = pd.merge(cob_e, cob_g[['Rut', 'DEUDA_GENERAL', 'TASACION_GENERAL']], left_on = 'Rut', right_on = 'Rut', how = 'left')
    cob_g = pd.merge(cob_g, cob_e[['Rut', 'DEUDA_ESPECIFICA', 'TASACION_ESPECIFICA']], left_on = 'Rut', right_on = 'Rut', how = 'left')


    # In[22]:


    cob_tot = pd.concat([cob_g, cob_e], axis = 0, ignore_index = True, sort = False).fillna(0).drop_duplicates()


    # In[23]:


    cob_tot['GRUPO'] = cob_tot['Rut']


    # In[24]:


    cob_tot['TASACION_GENERAL_GRUPO'] = cob_tot['TASACION_GENERAL']


    # In[25]:


    cob_tot['COBERTURA ESPECIFICA%'] = (cob_tot['TASACION_ESPECIFICA'] / cob_tot['DEUDA_ESPECIFICA']).fillna(0)


    # In[26]:


    dc = df.groupby('RUT_CLI')['SAL_DOC'].sum().reset_index(name = 'DEUDA CARTERA').replace('\.', '', regex=True)
    #dg = df2.groupby('Grupo')['Saldo insoluto'].sum().reset_index(name = 'DEUDA GRUPO')
    #se elimina grupo por duplicidad


    # In[27]:


    cob_tot = pd.merge(cob_tot, dc, left_on = 'Rut', right_on = 'RUT_CLI', how = 'left').drop('RUT_CLI', axis = 1).fillna(0)
    cob_tot['DEUDA GRUPO'] = cob_tot['DEUDA CARTERA'] #se crea columna igual a DEUDA CARTERA
    #cob_tot = pd.merge(cob_tot, dg, left_on = 'Grupo', right_on = 'Grupo', how = 'left').fillna(0)
    #se elimina grupo por duplicidad


    # In[28]:


    cob_tot['DEUDA GAR ESPECIFICA CORRECCION'] = (cob_tot['DEUDA CARTERA']).where(cob_tot['DEUDA CARTERA'] < cob_tot['DEUDA_ESPECIFICA'], cob_tot['DEUDA_ESPECIFICA'] )


    # In[29]:


    cob_tot['PARTICIPACION RUT EN GRUPO'] = (cob_tot['DEUDA CARTERA'] / cob_tot['DEUDA GRUPO']).fillna(0)


    # In[30]:


    cob_tot['MONTO GAR GENERAL'] = cob_tot['PARTICIPACION RUT EN GRUPO'] * cob_tot['TASACION_GENERAL_GRUPO']


    # In[31]:


    cob_tot['MONTO GAR ESPECIFICA'] = cob_tot['COBERTURA ESPECIFICA%'] * cob_tot['DEUDA GAR ESPECIFICA CORRECCION']


    # In[32]:


    cob_tot['MONTO GAR TOTAL'] = cob_tot['MONTO GAR GENERAL'] + cob_tot['MONTO GAR ESPECIFICA']


    # In[33]:


    cob_tot['COBERTURA'] = (cob_tot['MONTO GAR TOTAL'] / cob_tot['DEUDA CARTERA']).fillna(0)


    # In[34]:


    conditions = [
                (cob_tot['COBERTURA'] <= 0.6),
                (cob_tot['COBERTURA'] <= 0.7),
                (cob_tot['COBERTURA'] <= 0.8),
                (cob_tot['COBERTURA'] <= 0.9),
                (cob_tot['COBERTURA'] <= 1.0),
                (cob_tot['COBERTURA'] <= 1.1),
                (cob_tot['COBERTURA'] <= 1.2),
                (cob_tot['COBERTURA'] <= 1.3),
                (cob_tot['COBERTURA'] <= 1.4),
                (cob_tot['COBERTURA'] <= 1.5),
                (cob_tot['COBERTURA'] <= 1.6),
                (cob_tot['COBERTURA'] <= 1.7),
                (cob_tot['COBERTURA'] <= 1.8),
                (cob_tot['COBERTURA'] <= 1.9),
                (cob_tot['COBERTURA'] <= 2.0),
                ]
    choices = ['00[Sin cobertura o < 60%]', '01[60%-70%]', '02[70%-80%]', '03[80%-90%]', '04[90%-100%]', '05[100%-110%]', '06[110%-120%]', '07[120%-130%]', '08[130%-140%]', '09[140%-150%]', '10[150%-160%]', '11[160%-170%]', '12[170%-180%]', '13[180%-190%]', '14[190%-200%]']


    # In[35]:


    cob_tot['TRAMO COBERTURA'] = np.select(conditions, choices, default='15[>200%]')


    # In[36]:


    cob_tot = cob_tot[~cob_tot['Rut'].str.contains('76129826-7')] #Vechiola


    # # 6 **Cálculo provisiones al día**

    # In[37]:


    df2 = df.copy()


    # In[38]:


    df2['Fecha_proceso'] = fecha_proceso
    df2['Dias Fec Vcto.'] = (df2['Fecha_proceso'] - df2['FEC_VTO']).dt.days
    df2['MoraOperacion'] = [0 if s <= 0 else s for s in df2['Dias Fec Vcto.']]
    df2['Plazo'] = [ -s if s <= 0 else 0 for s in df2['Dias Fec Vcto.']]
    df2 = pd.merge(df2, fam[['TIPO DOCTO.', 'Familia2']], left_on = 'DOC_DES', right_on = 'TIPO DOCTO.', how = 'left').drop('TIPO DOCTO.', axis = 1)
    df2['Mora x Saldo'] = (df2['SAL_DOC'] * df2['MoraOperacion']).fillna(0)
    df2['Tripleta'] = df2['RUT_CLI'].astype(str) + "-" + df2['RUT_DEU'].astype(str) + "-" + df2['Familia2'].astype(str)

    #Aislación Tripleta

    #df2.loc[(df2['RUT_CLI'] == '76.248.671-7') & (df2['RUT_DEU'] == '77.424.780-7') & (df2['NUM_DOC'] == 6732), 'Tripleta'] += '(1)'
    #df2.loc[(df2['RUT_CLI'] == '76.248.671-7') & (df2['RUT_DEU'] == '77.424.780-7') & (df2['NUM_DOC'] == 6758), 'Tripleta'] += '(1)'
    #df2.loc[(df2['RUT_CLI'] == '76.248.671-7') & (df2['RUT_DEU'] == '77.424.780-7') & (df2['NUM_DOC'] == 6757), 'Tripleta'] += '(1)'
    #df2.loc[(df2['RUT_CLI'] == '79.540.520-8') & (df2['RUT_DEU'] == '79.540.520-8') & (df2['NUM_DOC'] == 291053), 'Tripleta'] += '(1)'

    df2_sdo_tri = df2.groupby('Tripleta')['SAL_DOC'].sum().reset_index(name = 'Saldo Tripleta')
    df2 = pd.merge(df2, df2_sdo_tri, left_on = 'Tripleta', right_on = 'Tripleta', how = 'left')
    df2_mor_x_sdo = df2.groupby('Tripleta')['Mora x Saldo'].sum().reset_index(name = 'Mora x Saldo Tripleta')
    df2 = pd.merge(df2, df2_mor_x_sdo, left_on = 'Tripleta', right_on = 'Tripleta', how = 'left')
    df2['Mora Tripleta'] = df2['Mora x Saldo Tripleta'] / df2['Saldo Tripleta']
    df2['Mora Parametros'] = df2[['MoraOperacion', 'Mora Tripleta']].max(axis=1)
    jud = 'JUD'
    df2['Judicial'] = df2['DOC_DES'].apply(lambda x: 1 if jud in x else 0)
    rec = 'REC'
    rene = 'RENE'
    df2['Renegociado'] = df2['DOC_DES'].apply(lambda x: 1 if rec in x or rene in x else 0)


    # In[39]:


    conditions1 = [
                (df2['MoraOperacion'] <= 30) & (df2['Renegociado'] == 0) & (df2['Judicial'] == 0),
                (df2['MoraOperacion'] <= 15) & (df2['Renegociado'] == 1) & (df2['Judicial'] == 0),
                (df2['MoraOperacion'] >= 90) | (df2['Judicial'] == 1)
                ]
    choices1 = ["1", "1", "3"]


    # In[40]:


    df2['Stage operación'] = np.select(conditions1, choices1, default='2')


    # In[41]:


    conditions2 = [
                (df2['Mora Tripleta'] <= 30) & (df2['Renegociado'] == 0) & (df2['Judicial'] == 0),
                (df2['Mora Tripleta'] <= 15) & (df2['Renegociado'] == 1) & (df2['Judicial'] == 0),
                (df2['Mora Tripleta'] >= 90) | (df2['Judicial'] == 1)
                ]
    choices2 = ["1", "1", "3"]


    # In[42]:


    df2['Stage tripleta'] = np.select(conditions2, choices2, default='2')
    df2['Stage final'] = df2[['Stage operación', 'Stage tripleta']].max(axis=1)


    # In[43]:


    conditions3 = [
                (df2['Stage final'] == "3"),
                (df2['Familia2'] == 'Cheque') & (df2['Mora Parametros'] <= 0),
                (df2['Familia2'] == 'Cheque') & (df2['Mora Parametros'] <= 89),
                (df2['Familia2'] == 'Credito') & (df2['Mora Parametros'] <= 0),
                (df2['Familia2'] == 'Credito') & (df2['Mora Parametros'] <= 14),
                (df2['Familia2'] == 'Credito') & (df2['Mora Parametros'] <= 89),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 0),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 14),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 29),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 44),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 59),
                (df2['Familia2'] == 'Factura') & (df2['Mora Parametros'] <= 89),
                (df2['Familia2'] == 'Otro') & (df2['Mora Parametros'] <= 0),
                (df2['Familia2'] == 'Otro') & (df2['Mora Parametros'] <= 89)
                ]
    choices3 = ['deterioro', 'Cheque - 0-0', 'Cheque - 1-89', 'Credito - 0-0', 'Credito - 1-14', 'Credito - 15-89', 'Factura - 0-0', 'Factura - 1-14', 'Factura - 15-29', 'Factura - 30-44', 'Factura - 45-59', 'Factura - 60-89', 'Otro - 0-0', 'Otro - 1-89']


    # In[44]:


    df2['Segmento PD'] = np.select(conditions3, choices3, default='deterioro')
    df2 = pd.merge(df2, PD, left_on = 'Segmento PD', right_on = 'Segmento PD', how = 'left')
    df2 = pd.merge(df2, LGD, left_on = 'Familia2', right_on = 'Familia2', how = 'left')
    df2['Tramo Mora'] = [ '00:[0]' if s <= 0 else '01:[1-15]' if s <= 15 else '02:[16-30]' if s <= 30 else '03:[31-40]' if s <= 40 else '04:[41-60]' if s <= 60 else '05:[61-90]' if s <= 90 else '06:[91-120]' if s <= 120 else '07:[>120]' for s in df2['MoraOperacion'] ]
    df2['Vigencia'] = ['Vigente' if s == 0 else 'Morosa' for s in df2['MoraOperacion']]
    df2['Mora_mas_90'] = ['1' if s > 90 else '0' for s in df2['MoraOperacion']]


    # In[45]:


    df2['Provision 12 meses'] = (
                                    (df2['SAL_DOC'] * df2['PD_3'] * df2['LGD']).where(df2['Plazo'] <= 90, 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_6'] * df2['LGD']).where((df2['Plazo'] > 90) & (df2['Plazo'] <= 180), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_9'] * df2['LGD']).where((df2['Plazo'] > 180) & (df2['Plazo'] <= 270), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_12'] * df2['LGD']).where(df2['Plazo'] > 270, 0 )
                                ).fillna(0)


    # In[46]:


    df2['Provision life time'] = (
                                    (df2['SAL_DOC'] * df2['PD_3'] * df2['LGD']).where(df2['Plazo'] <= 90, 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_6'] * df2['LGD']).where((df2['Plazo'] > 90) & (df2['Plazo'] <= 180), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_9'] * df2['LGD']).where((df2['Plazo'] > 180) & (df2['Plazo'] <= 270), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_12'] * df2['LGD']).where((df2['Plazo'] > 270) & (df2['Plazo'] <= 360), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_15'] * df2['LGD']).where((df2['Plazo'] > 360) & (df2['Plazo'] <= 450), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_18'] * df2['LGD']).where((df2['Plazo'] > 450) & (df2['Plazo'] <= 540), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_21'] * df2['LGD']).where((df2['Plazo'] > 540) & (df2['Plazo'] <= 630), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_24'] * df2['LGD']).where((df2['Plazo'] > 630) & (df2['Plazo'] <= 720), 0 ) +
                                    (df2['SAL_DOC'] * df2['PD_24M'] * df2['LGD']).where(df2['Plazo'] > 720, 0 )
                                ).fillna(0)


    # In[47]:


    df2['Provision F.L.'] = (df2['Provision 12 meses']).where(df2['Stage final'] == "1", df2['Provision life time'] )
    df2['RUT'] = df2['RUT_CLI'].replace('\.', '', regex=True)
    df2 = pd.merge(df2, cob_tot[['Rut', 'GRUPO']], left_on = 'RUT', right_on = 'Rut', how = 'left').drop('Rut', axis = 1)
    df2['GRUPO'] = df2['GRUPO'].fillna(df2['RUT'])
    df2['PROV SIN LGD'] = (df2['Provision F.L.'] / df2['LGD']).fillna(0)
    df2 = pd.merge(df2, cob_tot[['Rut', 'TRAMO COBERTURA']], left_on = 'RUT', right_on = 'Rut', how = 'left').drop('Rut', axis = 1)
    df2['TRAMO COBERTURA'] = df2['TRAMO COBERTURA'].fillna('00[Sin cobertura o < 60%]')


    # In[48]:


    #Cobertura CF Polytex
    #cfdim = (df2['FAC_CON'] == 'CFM') & (df2['RUT_CLI'] == '96.777.810-9')
    #df2.loc[cfdim, 'TRAMO COBERTURA'] = '02[70%-80%]'


    # In[50]:


    df2 = pd.merge(df2, tram[['tramo', 'LGD garantías']], left_on = 'TRAMO COBERTURA', right_on = 'tramo', how = 'left').drop('tramo', axis = 1)
    df2['LGD garantías'] = df2['LGD garantías'].fillna(df2['LGD'])
    df2['Provision Garantias'] = df2['PROV SIN LGD'] * df2['LGD garantías']
    df2['Provision Garantias'].sum()


    # # 7 **Cálculo provisiones proyectadas**

    # In[51]:


    df3 = df.copy()


    # In[52]:


    df3['Fecha_proyeccion'] = fecha_proyeccion
    df3['Dias Fec Vcto.'] = (df3['Fecha_proyeccion'] - df3['FEC_VTO']).dt.days
    df3['MoraOperacion'] = [0 if s <= 0 else s for s in df3['Dias Fec Vcto.']]
    df3['Plazo'] = [ -s if s <= 0 else 0 for s in df3['Dias Fec Vcto.']]
    df3 = pd.merge(df3, fam[['TIPO DOCTO.', 'Familia2']], left_on = 'DOC_DES', right_on = 'TIPO DOCTO.', how = 'left').drop('TIPO DOCTO.', axis = 1)
    df3['Mora x Saldo'] = (df3['SAL_DOC'] * df3['MoraOperacion']).fillna(0)
    df3['Tripleta'] = df3['RUT_CLI'].astype(str) + "-" + df3['RUT_DEU'].astype(str) + "-" + df3['Familia2'].astype(str)

    #Aislación Tripleta

    #df3.loc[(df3['RUT_CLI'] == '76.248.671-7') & (df3['RUT_DEU'] == '77.424.780-7') & (df3['NUM_DOC'] == 6732), 'Tripleta'] += '(1)'
    #df3.loc[(df3['RUT_CLI'] == '76.248.671-7') & (df3['RUT_DEU'] == '77.424.780-7') & (df3['NUM_DOC'] == 6758), 'Tripleta'] += '(1)'
    #df3.loc[(df3['RUT_CLI'] == '76.248.671-7') & (df3['RUT_DEU'] == '77.424.780-7') & (df3['NUM_DOC'] == 6757), 'Tripleta'] += '(1)'
    #df3.loc[(df3['RUT_CLI'] == '79.540.520-8') & (df3['RUT_DEU'] == '79.540.520-8') & (df3['NUM_DOC'] == 291053), 'Tripleta'] += '(1)'

    df3_sdo_tri = df3.groupby('Tripleta')['SAL_DOC'].sum().reset_index(name = 'Saldo Tripleta')
    df3 = pd.merge(df3, df3_sdo_tri, left_on = 'Tripleta', right_on = 'Tripleta', how = 'left')
    df3_mor_x_sdo = df3.groupby('Tripleta')['Mora x Saldo'].sum().reset_index(name = 'Mora x Saldo Tripleta')
    df3 = pd.merge(df3, df3_mor_x_sdo, left_on = 'Tripleta', right_on = 'Tripleta', how = 'left')
    df3['Mora Tripleta'] = df3['Mora x Saldo Tripleta'] / df3['Saldo Tripleta']
    df3['Mora Parametros'] = df3[['MoraOperacion', 'Mora Tripleta']].max(axis=1)
    jud = 'JUD'
    df3['Judicial'] = df3['DOC_DES'].apply(lambda x: 1 if jud in x else 0)
    rec = 'REC'
    rene = 'RENE'
    df3['Renegociado'] = df3['DOC_DES'].apply(lambda x: 1 if rec in x or rene in x else 0)


    # In[53]:


    conditions1 = [
                (df3['MoraOperacion'] <= 30) & (df3['Renegociado'] == 0) & (df3['Judicial'] == 0),
                (df3['MoraOperacion'] <= 15) & (df3['Renegociado'] == 1) & (df3['Judicial'] == 0),
                (df3['MoraOperacion'] >= 90) | (df3['Judicial'] == 1)
                ]
    choices1 = ["1", "1", "3"]


    # In[54]:


    df3['Stage operación'] = np.select(conditions1, choices1, default='2')


    # In[55]:


    conditions2 = [
                (df3['Mora Tripleta'] <= 30) & (df3['Renegociado'] == 0) & (df3['Judicial'] == 0),
                (df3['Mora Tripleta'] <= 15) & (df3['Renegociado'] == 1) & (df3['Judicial'] == 0),
                (df3['Mora Tripleta'] >= 90) | (df3['Judicial'] == 1)
                ]
    choices2 = ["1", "1", "3"]


    # In[56]:


    df3['Stage tripleta'] = np.select(conditions2, choices2, default='2')
    df3['Stage final'] = df3[['Stage operación', 'Stage tripleta']].max(axis=1)


    # In[57]:


    conditions3 = [
                (df3['Stage final'] == "3"),
                (df3['Familia2'] == 'Cheque') & (df3['Mora Parametros'] <= 0),
                (df3['Familia2'] == 'Cheque') & (df3['Mora Parametros'] <= 89),
                (df3['Familia2'] == 'Credito') & (df3['Mora Parametros'] <= 0),
                (df3['Familia2'] == 'Credito') & (df3['Mora Parametros'] <= 14),
                (df3['Familia2'] == 'Credito') & (df3['Mora Parametros'] <= 89),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 0),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 14),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 29),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 44),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 59),
                (df3['Familia2'] == 'Factura') & (df3['Mora Parametros'] <= 89),
                (df3['Familia2'] == 'Otro') & (df3['Mora Parametros'] <= 0),
                (df3['Familia2'] == 'Otro') & (df3['Mora Parametros'] <= 89)
                ]
    choices3 = ['deterioro', 'Cheque - 0-0', 'Cheque - 1-89', 'Credito - 0-0', 'Credito - 1-14', 'Credito - 15-89', 'Factura - 0-0', 'Factura - 1-14', 'Factura - 15-29', 'Factura - 30-44', 'Factura - 45-59', 'Factura - 60-89', 'Otro - 0-0', 'Otro - 1-89']


    # In[58]:


    df3['Segmento PD'] = np.select(conditions3, choices3, default='deterioro')
    df3 = pd.merge(df3, PD, left_on = 'Segmento PD', right_on = 'Segmento PD', how = 'left')
    df3 = pd.merge(df3, LGD, left_on = 'Familia2', right_on = 'Familia2', how = 'left')
    df3['Tramo Mora'] = [ '00:[0]' if s <= 0 else '01:[1-15]' if s <= 15 else '02:[16-30]' if s <= 30 else '03:[31-40]' if s <= 40 else '04:[41-60]' if s <= 60 else '05:[61-90]' if s <= 90 else '06:[91-120]' if s <= 120 else '07:[>120]' for s in df3['MoraOperacion'] ]
    df3['Vigencia'] = ['Vigente' if s == 0 else 'Morosa' for s in df3['MoraOperacion']]
    df3['Mora_mas_90'] = ['1' if s > 90 else '0' for s in df3['MoraOperacion']]


    # In[59]:


    df3['Provision 12 meses'] = (
                                    (df3['SAL_DOC'] * df3['PD_3'] * df3['LGD']).where(df3['Plazo'] <= 90, 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_6'] * df3['LGD']).where((df3['Plazo'] > 90) & (df3['Plazo'] <= 180), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_9'] * df3['LGD']).where((df3['Plazo'] > 180) & (df3['Plazo'] <= 270), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_12'] * df3['LGD']).where(df3['Plazo'] > 270, 0 )
                                ).fillna(0)


    # In[60]:


    df3['Provision life time'] = (
                                    (df3['SAL_DOC'] * df3['PD_3'] * df3['LGD']).where(df3['Plazo'] <= 90, 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_6'] * df3['LGD']).where((df3['Plazo'] > 90) & (df3['Plazo'] <= 180), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_9'] * df3['LGD']).where((df3['Plazo'] > 180) & (df3['Plazo'] <= 270), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_12'] * df3['LGD']).where((df3['Plazo'] > 270) & (df3['Plazo'] <= 360), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_15'] * df3['LGD']).where((df3['Plazo'] > 360) & (df3['Plazo'] <= 450), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_18'] * df3['LGD']).where((df3['Plazo'] > 450) & (df3['Plazo'] <= 540), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_21'] * df3['LGD']).where((df3['Plazo'] > 540) & (df3['Plazo'] <= 630), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_24'] * df3['LGD']).where((df3['Plazo'] > 630) & (df3['Plazo'] <= 720), 0 ) +
                                    (df3['SAL_DOC'] * df3['PD_24M'] * df3['LGD']).where(df3['Plazo'] > 720, 0 )
                                ).fillna(0)


    # In[61]:


    df3['Provision F.L.'] = (df3['Provision 12 meses']).where(df3['Stage final'] == "1", df3['Provision life time'] )
    df3['RUT'] = df3['RUT_CLI'].replace('\.', '', regex=True)
    df3 = pd.merge(df3, cob_tot[['Rut', 'GRUPO']], left_on = 'RUT', right_on = 'Rut', how = 'left').drop('Rut', axis = 1)
    df3['GRUPO'] = df3['GRUPO'].fillna(df3['RUT'])
    df3['PROV SIN LGD'] = (df3['Provision F.L.'] / df3['LGD']).fillna(0)
    df3 = pd.merge(df3, cob_tot[['Rut', 'TRAMO COBERTURA']], left_on = 'RUT', right_on = 'Rut', how = 'left').drop('Rut', axis = 1)
    df3['TRAMO COBERTURA'] = df3['TRAMO COBERTURA'].fillna('00[Sin cobertura o < 60%]')


    # In[62]:


    #Cobertura CF Polytex

    #cfdim = (df3['FAC_CON'] == 'CFM') & (df3['RUT_CLI'] == '96.777.810-9')
    #df3.loc[cfdim, 'TRAMO COBERTURA'] = '02[70%-80%]'


    # In[64]:


    df3 = pd.merge(df3, tram[['tramo', 'LGD garantías']], left_on = 'TRAMO COBERTURA', right_on = 'tramo', how = 'left').drop('tramo', axis = 1)
    df3['LGD garantías'] = df3['LGD garantías'].fillna(df3['LGD'])
    df3['Provision Garantias'] = df3['PROV SIN LGD'] * df3['LGD garantías']
    df3['Provision Garantias'].sum()


    # # 8 **Consolidación resultados**

    # In[65]:


    df2['Llave'] = df2['RUT_CLI'].astype(str) + "-" + df2['RUT_DEU'].astype(str) + "-" + df2['NUM_DOC'].astype(str).str.split('.').str[0] + "-" + df2['TIP_DOC'].astype(str)+ df2['SEC_FASE'].astype(str).str.split('.').str[0]
    df3['Llave'] = df3['RUT_CLI'].astype(str) + "-" + df3['RUT_DEU'].astype(str) + "-" + df3['NUM_DOC'].astype(str).str.split('.').str[0] + "-" + df3['TIP_DOC'].astype(str)+ df3['SEC_FASE'].astype(str).str.split('.').str[0]
    df2 = df2.rename(columns={'MoraOperacion': 'Mora_Operacion', 'Tramo Mora': 'Tramo_Mora', 'Provision Garantias': 'Provision_Garantias'})
    df3 = df3.rename(columns={'MoraOperacion': 'Mora_Operacion_p', 'Tramo Mora': 'Tramo_Mora_p', 'Vigencia': 'Vigencia_p', 'Mora_mas_90': 'Mora_mas_90_p', 'Provision Garantias': 'Provision_Garantias_p'})


    # In[66]:


    df4 = pd.merge(df2, df3[['Llave', 'Fecha_proyeccion', 'Mora_Operacion_p', 'Tramo_Mora_p',  'Vigencia_p', 'Mora_mas_90_p', 'Provision_Garantias_p']], left_on = 'Llave', right_on = 'Llave', how = 'left')


    # In[67]:


    #se agrega código de gestión
    mora['Llave'] = mora['RUT CLIENTE'].astype(str) + "-" + mora['RUT DEUDOR'].astype(str) + "-" + mora['NºDOCTO.'].astype(str) + "-" + mora['T.D.'].astype(str)
    df4 = pd.merge(df4, mora[['Llave', 'COD_COB', 'DES_COD_COB', 'OBSERVACION','FEC_PRX_GES']], left_on = 'Llave', right_on = 'Llave', how = 'left')
    df4['COD_COB'] = df4['COD_COB'].fillna(0)
    df4['DES_COD_COB'] = df4['DES_COD_COB'].fillna('Sin código')
    df4['OBSERVACION'] = df4['OBSERVACION'].fillna('')
    na_rows = df4['FEC_PRX_GES'].isna()
    df4.loc[na_rows, 'FEC_PRX_GES'] = pd.to_datetime('1900-01-01')


    # In[68]:


    #se agrega jerarquía
    df4 = pd.merge(df4, jer, left_on = 'NOMBRE_SUCURSAL', right_on = 'Sucursal', how = 'left').drop('Sucursal', axis = 1)


    #se agrega marcas de pago y prórroga
    df4 = pd.merge(df4, marcas[['Llave', 'Fecha_pago', 'Fecha_prórroga']], left_on = 'Llave', right_on = 'Llave', how = 'left')
    df4['Fecha_pago'] = df4['Fecha_pago'].fillna(pd.Timestamp(year=1900, month=1, day=1))
    df4['Fecha_prórroga'] = df4['Fecha_prórroga'].fillna(pd.Timestamp(year=1900, month=1, day=1))


    # In[69]:


    #casos incidentes
    prov_cli_p = df4.groupby('RUT_CLI')['Provision_Garantias_p'].sum()
    df4['Incidente'] = df4['RUT_CLI'].map(prov_cli_p) >= Inc
    df4['Incidente'] = df4['Incidente'].astype(int)
    df4['Incidente'] = df4['Incidente'].astype(str)


    # In[70]:


    df4 = df4[['Fecha_proceso', 'Fecha_proyeccion', 'FAC_CON', 'COD_EJE', 'NOMBRE_EJECUTIVO', 'NOMBRE_SUCURSAL', 'RUT_CLI', 'NOMBRE_CLI', 'RUT_DEU',
               'NOMBRE_DEU', 'TIP_DOC', 'DOC_DES', 'NUM_DOC', 'FEC_VTO', 'MON_FAC', 'SAL_DOC', 'SEC_FASE', 'FEC_OPE', 'SEC_CLI', 'SEC_DEU',
               'Mora_Operacion', 'Vigencia', 'Mora_mas_90', 'Tramo_Mora', 'Provision_Garantias', 'Mora_Operacion_p', 'Vigencia_p', 'Mora_mas_90_p',
               'Tramo_Mora_p', 'Provision_Garantias_p', 'Incidente', 'COD_COB', 'DES_COD_COB', 'OBSERVACION', 'FEC_PRX_GES', 'Jefe_Cobranza_Zonal',
               'Subgerencia', 'Fecha_pago', 'Fecha_prórroga']]


    # In[71]:


    df4['Provision_Garantias'] = df4['Provision_Garantias'].astype(int)
    df4['Provision_Garantias_p'] = df4['Provision_Garantias_p'].astype(int)

    df4['NOMBRE_DEU'] = df4['NOMBRE_DEU'].fillna('')


    # In[72]:


    df4.dtypes


    # # 9 **Guardar resultados**

    # ## 9.1 **Detalle**

    # In[73]:


    conn_str = ("Driver={SQL Server};"
                "Server=HENDRIX.EURO;"
                "Database=Reporteria_Factoring;"
                "UID=jlucero@eurocapital.cl;"
                "PWD=UB,,*P88ZPsJ;"
                "Trusted_connection=no;")


    # In[74]:


    conn = pyodbc.connect(conn_str)


    # In[75]:


    cursor = conn.cursor()


    # In[76]:


    #for index, row in df4.iterrows():
    #     cursor.execute("INSERT INTO Factoring_dia (FECHA_PROCESO, FECHA_PROYECCION, FACTURA_CONFIRMING, CODIGO_EJECUTIVO, NOMBRE_EJECUTIVO, SUCURSAL, RUT_CLIENTE, NOMBRE_CLIENTE, RUT_DEUDOR, NOMBRE_DEUDOR, TIPO_DOCUMENTO, DESCRIPCION_DOCUMENTO, NRO_DOCUMENTO, FECHA_VENCIMIENTO, MONTO_DOCUMENTO, SALDO_DOCUMENTO, NRO_OPERACION, FECHA_OPERACION, SECTOR_CLIENTE, SECTOR_DEUDOR, DIAS_MORA, VIGENCIA, MORA_MAS_90, TRAMO_MORA, PROVISION, DIAS_MORA_PROYECTADA, VIGENCIA_PROYECTADA, MORA_MAS_90_PROYECTADA, TRAMO_MORA_PROYECTADA, PROVISION_PROYECTADA, CODIGO_GESTION, DESCRIPCION_CODIGO_GESTION, OBSERVACION, PROX_GESTION, JEFE_ZONAL, SUBGERENCIA, INCIDENTE, FECHA_PAGO, FECHA_PRORROGA) values(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    #                    row.Fecha_proceso, row.Fecha_proyeccion, row.FAC_CON, row.COD_EJE, row.NOMBRE_EJECUTIVO, row.NOMBRE_SUCURSAL, row.RUT_CLI, row.NOMBRE_CLI, row.RUT_DEU, row.NOMBRE_DEU, row.TIP_DOC, row.DOC_DES, row.NUM_DOC, row.FEC_VTO, row.MON_FAC, row.SAL_DOC, row.SEC_FASE, row.FEC_OPE, row.SEC_CLI, row.SEC_DEU, row.Mora_Operacion, row.Vigencia, row.Mora_mas_90, row.Tramo_Mora, row.Provision_Garantias, row.Mora_Operacion_p, row.Vigencia_p, row.Mora_mas_90_p, row.Tramo_Mora_p, row.Provision_Garantias_p, row.COD_COB, row.DES_COD_COB, row.OBSERVACION, row.FEC_PRX_GES, row.Jefe_Cobranza_Zonal, row.Subgerencia, row.Incidente, row.Fecha_pago, row.Fecha_prórroga)


    # In[77]:


    conn.commit()


    # In[78]:


    conn.close()


    # In[79]:


    df2.to_csv('Resultados_dia/prov_fact_al_dia_' + str(fecha_proceso.year) + f'{fecha_proceso.month:02d}' + f'{fecha_proceso.day:02d}'+'.csv', sep=';', encoding='UTF-8', decimal=",")


    # In[80]:


    df3.to_csv('Resultados_dia/prov_fact_proyectada_' + str(fecha_proceso.year) + f'{fecha_proceso.month:02d}' + f'{fecha_proceso.day:02d}'+'.csv', sep=';', encoding='UTF-8', decimal=",")


    # In[81]:


    df4.to_csv('Resultados_dia/prov_fact_consolidado_' + str(fecha_proceso.year) + f'{fecha_proceso.month:02d}' + f'{fecha_proceso.day:02d}'+'.csv', sep=';', encoding='latin1', decimal=",")


    # In[82]:


    cob_tot.to_csv('Resultados_dia/garantias_' + str(fecha_proceso.year) + f'{fecha_proceso.month:02d}' + f'{fecha_proceso.day:02d}'+'.csv', sep=';', encoding='UTF-8', decimal=",")


    # In[ ]:

else:
    print("Hoy no es día hábil en Chile. No se ejecuta el código.")


