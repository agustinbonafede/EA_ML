import pandas as pd
def File2Array(filename):
	with open(filename) as f:
		listFile = f.readlines()	#separa linea por linea el archivo de texto
	listFile = [listFile[n:] for n, i in enumerate(listFile) if 'ID' in listFile[n]][0] #recorta el header
	listFile = list(map(lambda s: s.strip(), listFile))								#elimina los \n de los strings grandes
	listFile = [list(filter(None, listFile[i].split(' '))) for i in range(len(listFile))]	#divide según los espacios en listas
	listFile = ColumnNameCorrector(listFile)
	header = listFile[0]
	listFile = listFile[1:]
	array = [[castIntoIntOrFloatSmartly(i) for i in listFile[j]] for j in range(len(listFile))]

	return array, header

def GetDescriptionFromFile(filename):
	with open(filename) as f:
		listFile = f.readlines()
	description = [listFile[:n] for n, i in enumerate(listFile) if 'ID' in listFile[n]][0]
	return description

def ColumnNameCorrector(listFile):
	if len(listFile[0]) > len(listFile[1]) and 'SIG' in listFile[0]:
		index = listFile[0].index('SIG')
		listFile[0][index: index + 2] = ['-'.join(listFile[0][index:index + 2])]
	return listFile

def castIntoIntOrFloatSmartly(s):
	f = float(s)
	i = int(f)
	return i if i == f else f

def File2PandasTable(filename):
	array, nameOfColumns = File2Array(filename)
	if len(nameOfColumns) != len(array[0]):
		nameOfColumns = nameOfColumns[0].split('\t')
	table = pd.DataFrame(array, columns=nameOfColumns)
	table = table.rename(columns={'SSSSSSSS.mmmuuun': 'Tiempo',  'ABS-ENERGY':'ABS_ENERGY', 'C-FRQ':'C_FRQ',
								  'P-FRQ':'P_FRQ', 'A-FRQ':'A_FRQ', 'R-FRQ':'R_FRQ', 'I-FRQ':'I_FRQ', 'SIG-STRNGTH': 'SIG_STRNGTH'})
	return table
