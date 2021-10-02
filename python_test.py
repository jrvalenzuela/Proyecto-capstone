import pandas as pd
from gurobipy import *

xls = pd.ExcelFile('Proyecto_1_TransporteMaritimo_Dataset1.xlsx', engine='openpyxl')
nombres= xls.sheet_names
df1 = pd.read_excel(xls, nombres[0])
df2 = pd.read_excel(xls, nombres[1])
df3= pd.read_excel(xls, nombres[2])
df4= pd.read_excel(xls, nombres[3])
df5= pd.read_excel(xls, nombres[4])
df6= pd.read_excel(xls, nombres[5])


print("Armando conjuntos...")
n_cargos = len(df3)

V= list(df1["ID_Barco"]) ## conjunto barcos
n_barcos = len(V)

Kv= {} # conjunto capacidades de barcos
for i in range(0,len(V)):
    Kv[i+1]= list(df1["Capacidad"])[i]

nodos_carga= list(df3["ID_Cargo"])

nodos_descarga= [i+len(nodos_carga) for i in range(1,len(nodos_carga)+1)] ##conjunto nodos de descarga

cargas = df3[["ID_Cargo","ID_Puerto_Origen", "Tamano", "Costo_SPOT","LT_Carga","RT_Carga"]].rename(columns={"ID_Puerto_Origen": "ID_Puerto ", "LT_Carga":"LT","RT_Carga":"RT"})
descargas = df3[["ID_Cargo","ID_Puerto_Destino", "Tamano", "Costo_SPOT","LT_Descarga","RT_Descarga"]].rename(columns={"ID_Puerto_Destino": "ID_Puerto ", "LT_Descarga":"LT","RT_Descarga":"RT"})
nodos = pd.concat([cargas,descargas],axis=0)
nodos = nodos.reset_index()[["ID_Cargo","ID_Puerto ", "Tamano", "Costo_SPOT","LT","RT"]]
nodos.index+=1
N = nodos.to_dict("index")

puertos_barco = df1["ID_Puerto "]
t_origen = df1["Tiempo_Inicio"].to_dict()
o = {}
d = {}
for i in range(len(puertos_barco.to_dict())):
  o[i+1] = i+1+n_cargos*2 
  N[i+1+n_cargos*2] = {'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': puertos_barco.to_dict()[i],
  'LT': t_origen[i],
  'RT': 10000,
  'Tamano': 0}
  d[i+1]=i+1+n_cargos*2+len(puertos_barco.to_dict())
  N[i+1+n_cargos*2+len(puertos_barco.to_dict())]={'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': 0,
  'LT': 0,
  'RT': 10000,
  'Tamano': 0}
"""
for i in range(len(puertos_barco.to_dict())):
  o[i+1] = {'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': puertos_barco.to_dict()[i],
  'LT': 0,
  'RT': 0,
  'Tamano': 0}
  N[-i-1] = {'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': puertos_barco.to_dict()[i],
  'LT': 0,
  'RT': 0,
  'Tamano': 0}
  d[i+1]={'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': 0,
  'LT': 0,
  'RT': 0,
  'Tamano': 0}
  N[-i-1-len(puertos_barco.to_dict())]={'Costo_SPOT': 0,
  'ID_Cargo': 0,
  'ID_Puerto ': 0,
  'LT': 0,
  'RT': 0,
  'Tamano': 0}
"""
nodos_index = [i for i in N.keys()]

compatibilidad = {}
for i in V:
  compatibilidad[i] = [int(j) for j in list(df2.loc[i-1])[1:] if j>0]
compatibilidad

Nv = {}
for i in V:
  Nv[i] = []
  for j in N.keys():
    if N[j]["ID_Cargo"] in compatibilidad[i] or (j == i+n_cargos*2 or j==i+n_cargos*2+len(V)): 
      Nv[i].append(j)
"""
for i in V:
  Nv[i] = []
  Nv[i].append(-i) # el primer nodo compatible es el nodo origen
  for j in N.keys():
    if N[j]["ID_Cargo"] in compatibilidad[i]:
      Nv[i].append(j)
  Nv[i].append(-i-n_barcos) # el último nodo compatible es el nodo termino
"""
Av={}
for v in V:
  Av[v] = [] 
  for i in Nv[v]:
    for j in Nv[v]:
      if j+n_cargos != i and i<=n_cargos*2+len(V) and j!=i: # no se puede descargar un cargo sin haberlo cargado y i no puede ser un nodo de termino
        if j<=n_cargos*2 or j>n_cargos*2+len(V): # no se puede volver a un nodo de origen
          if not(i>n_cargos*2 and j>n_cargos*2): # no se puede ir de el origen directo al destino ni viceversa
            Av[v].append([i,j])
"""
for v in V:
  Av[v] = [] 
  for i in Nv[v]:
    for j in Nv[v]:
      if j+n_cargos != i and i>-len(V): # no se puede descargar un cargo sin haberlo cargado y i no puede ser un nodo de termino
        if j>0 or j<-n_barcos: # no se puede volver a un nodo de origen
          Av[v].append([i,j])
"""

NP_v = {}
for v in V:
  NP_v[v] = [i for i in nodos_carga if i in Nv[v]]

ND_v = {}
for v in V:
  ND_v[v] = [i for i in nodos_descarga if i in Nv[v]]

LT_i = {i:N[i]["LT"] for i in N.keys()}

RT_i = {i:N[i]["RT"] for i in N.keys()}

T_ijv={}
for i in N.keys():
  T_ijv[i] = {} 
  for j in N.keys():
    T_ijv[i][j] = {} 
    for v in V:
      cargo_i= N[i]["ID_Cargo"]
      cargo_j = N[j]["ID_Cargo"]
      if i>n_cargos*2+len(V) or j>n_cargos*2+len(V):
        T_ijv[i][j][v] = 0
      else: 
        puerto_origen = N[i]["ID_Puerto "]
        puerto_destino = N[j]["ID_Puerto "]
        T_ijv[i][j][v] = df4.loc[(df4["Puerto_Origen"]==puerto_origen)&(df4["Puerto_Destino"]==puerto_destino)&(df4["ID_Barco"]==v),["Tiempo_Viaje_hrs"]]["Tiempo_Viaje_hrs"].item()
      if 0<i<=n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Tiempo_Origen_hrs"]]["Tiempo_Origen_hrs"].item()
      if 0<j<=n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Tiempo_Origen_hrs"]]["Tiempo_Origen_hrs"].item()
      if n_cargos*2>=i>n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Tiempo_Destino_hrs"]]["Tiempo_Destino_hrs"].item()
      if n_cargos*2>=j>n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Tiempo_Destino_hrs"]]["Tiempo_Destino_hrs"].item()
"""
for i in N.keys():
  T_ijv[i] = {} 
  for j in N.keys():
    T_ijv[i][j] = {} 
    for v in V:
      cargo_i= N[i]["ID_Cargo"]
      cargo_j = N[j]["ID_Cargo"]
      if i<=-len(V) or j<=-len(V):
        T_ijv[i][j][v] = 0
      else: 
        puerto_origen = N[i]["ID_Puerto "]
        puerto_destino = N[j]["ID_Puerto "]
        T_ijv[i][j][v] = df4.loc[(df4["Puerto_Origen"]==puerto_origen)&(df4["Puerto_Destino"]==puerto_destino)&(df4["ID_Barco"]==v),["Tiempo_Viaje_hrs"]]["Tiempo_Viaje_hrs"].item()
      if 0<i<=n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Tiempo_Origen_hrs"]]["Tiempo_Origen_hrs"].item()
      if 0<j<=n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Tiempo_Origen_hrs"]]["Tiempo_Origen_hrs"].item()
      if i>n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Tiempo_Destino_hrs"]]["Tiempo_Destino_hrs"].item()
      if j>n_cargos:
        T_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Tiempo_Destino_hrs"]]["Tiempo_Destino_hrs"].item()
T_ijv[1][2][v]
"""  

C_ijv={}
for i in N.keys():
  C_ijv[i] = {} 
  for j in N.keys():
    C_ijv[i][j] = {} 
    for v in V:
      if i>n_cargos*2+len(V) or j>n_cargos*2+len(V):
        C_ijv[i][j][v] = 0
      else: 
        puerto_origen = N[i]["ID_Puerto "]
        puerto_destino = N[j]["ID_Puerto "]
        C_ijv[i][j][v] = df4.loc[(df4["Puerto_Origen"]==puerto_origen)&(df4["Puerto_Destino"]==puerto_destino)&(df4["ID_Barco"]==v),["Costo_Viaje_libras"]]["Costo_Viaje_libras"].item()
      if 0<i<=n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Costos_Origen_hrs"]]["Costos_Origen_hrs"].item()
      if 0<j<=n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Costos_Origen_hrs"]]["Costos_Origen_hrs"].item()
      if n_cargos*2>=i>n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Costos_Destino_hrs"]]["Costos_Destino_hrs"].item()
      if n_cargos*2>=j>n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Costos_Destino_hrs"]]["Costos_Destino_hrs"].item()
"""
for i in N.keys():
  C_ijv[i] = {} 
  for j in N.keys():
    C_ijv[i][j] = {} 
    for v in V:
      if i<=-len(V) or j<=-len(V):
        C_ijv[i][j][v] = 0
      else: 
        puerto_origen = N[i]["ID_Puerto "]
        puerto_destino = N[j]["ID_Puerto "]
        C_ijv[i][j][v] = df4.loc[(df4["Puerto_Origen"]==puerto_origen)&(df4["Puerto_Destino"]==puerto_destino)&(df4["ID_Barco"]==v),["Costo_Viaje_libras"]]["Costo_Viaje_libras"].item()
      if 0<i<=n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Costos_Origen_hrs"]]["Costos_Origen_hrs"].item()
      if 0<j<=n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Costos_Origen_hrs"]]["Costos_Origen_hrs"].item()
      if i>n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[i]["ID_Cargo"]),["Costos_Destino_hrs"]]["Costos_Destino_hrs"].item()
      if j>n_cargos:
        C_ijv[i][j][v] += df5.loc[(df5["ID_Barco"]==v)&(df5["ID_Cargo"]==N[j]["ID_Cargo"]),["Costos_Destino_hrs"]]["Costos_Destino_hrs"].item()
"""

Qj={N[i]["ID_Cargo"]:N[i]["Tamano"] for i in N.keys() if N[i]["ID_Cargo"]>0}

Cs = df3["Costo_SPOT"].to_dict()
print(Cs)
print("empezando con el modelo")

# Model
m = Model("Transporte Maritimo")

# variables
x = m.addVars(nodos_index,nodos_index,V,vtype=GRB.BINARY, name="Arco")
y = m.addVars(nodos_carga,vtype=GRB.BINARY,name="Cargo_Spot")
t = m.addVars(nodos_index,V,vtype=GRB.INTEGER, name="tiempo")
l = m.addVars(nodos_index,V,vtype=GRB.INTEGER,name="Inventario")

# Objective function
#m.setObjective(sum((sum((CTt[k,t]+4.5)*st[k,t] for k in LOG)+sum((CFt[k,t])*zt[k,t] for k in LOG)+(sum(CBt[m,t]*wt[m,t] for m in BOARD))) for t in MONTH), GRB.MINIMIZE)
m.setObjective(sum(sum(C_ijv[i][j][v]*x[i,j,v] for [i,j] in Av[v]) for v in V)+sum(Cs[i-1]*y[i] for i in nodos_carga), GRB.MINIMIZE)
 

m.addConstrs(((sum(sum(x[i,j,v] + y[i] for j in Nv[v] if [i,j] in Av[v]) for v in V) == 1) for i in nodos_carga), name = "Todos los cargos son transportados")

m.addConstrs(((sum(x[o[v],j,v] for j in Nv[v] if [o[v],j] in Av[v]) == 1) for v in V), name = "Parte en el origen")

#m.addConstrs(((sum(x[i][j][v] for j in Nv[v])-sum(x[j][i][v] for j in Nv[v])==0) for v in V for i in Nv[v] if i>0), name = "Todos los cargos son transportados")
m.addConstrs(((sum(x[i,j,v] for j in Nv[v] if [i,j] in Av[v])-sum(x[j,i,v] for j in Nv[v] if [i,j] in Av[v])==0) for v in V for i in Nv[v] if (i!=n_cargos*2+v and i!=n_cargos*2+v+n_barcos)), name = "Todos los cargos son transportados")


m.addConstrs(((sum(x[j,d[v],v] for j in Nv[v]if [j,d[v]] in Av[v]) == 1) for v in V), name = "Termina en el destino")

m.addConstrs(((l[i,v]+Qj[j]-l[j,v]<=Kv[v]*(1-x[i,j,v]))  for v in V for [i,j] in Av[v] if j in NP_v[v]), name = "Control flujo 1")

m.addConstrs(((l[i,v]-Qj[j]-l[j+n_cargos,v]<=Kv[v]*(1-x[i,j+n_cargos,v]))  for v in V for j in NP_v[v] for i in NP_v[v] if ([i,j+n_cargos] in Av[v])), name = "Control flujo 2")

m.addConstrs(((l[i,v]<=Kv[v]) for v in V for i in NP_v[v]), name = "Capacidad ub")

m.addConstrs(((l[i,v]>=0) for v in V for i in NP_v[v]), name = "Capacidad lb")

m.addConstrs(((t[i,v]+T_ijv[i][j][v]-t[j,v]<=(RT_i[i]+T_ijv[i][j][v])*(1-x[i,j,v])) for v in V for [i,j] in Av[v]), name = "Tiempo")

m.addConstrs(((sum(x[i,j,v] for j in Nv[v] if [i,j] in Av[v])-sum(x[n_cargos+i,j,v] for j in Nv[v] if [i+n_cargos,j] in Av[v])==0) for v in V for i in NP_v[v]), name = "Todos los cargos llegan a destino")

m.addConstrs(((t[i,v]+T_ijv[i][n_cargos+i][v]-t[n_cargos+i,v]<=0) for v in V for i in NP_v[v] ), name = "Tiempo 2")

m.addConstrs(((t[i,v]<=RT_i[i]) for v in V for i in Nv[v]), name = "Naturaleza Tiempo ub")

m.addConstrs(((t[i,v]>=LT_i[i]) for v in V for i in Nv[v]), name = "Naturaleza Tiempo lb")

# Solve
m.optimize()

valorobjetivo = m.objval

"""for v in m.getVars():
    print('%s %g' % (v.varName, v.x))"""

print('\n Valor óptimo: %8.4f \n' % valorobjetivo)

m.write("Transporte.sol")

