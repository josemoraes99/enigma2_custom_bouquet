import datetime
import sys
import os
import io
from urllib.request import urlopen

customBouquetName = 'userbouquet.netcabo.tv'
customBouquetFile = '/etc/enigma2/' + customBouquetName
bouquetList       = '/etc/enigma2/bouquets.tv'
lambedbFile       = '/etc/enigma2/lamedb5'
caboBouquet       = "/etc/enigma2/userbouquet..tv"

if len(sys.argv) > 1:
	for ar in sys.argv:
		if ar == 'debug':
			lambedbFile = 'lamedb5'
			customBouquetFile = customBouquetName
			bouquetList = 'bouquets.tv'
			caboBouquet = "userbouquet..tv"


def read_LameDB():
	print(f"{datetime.datetime.now()} Lendo lamedb5 em {lambedbFile}")
	if os.path.isfile(lambedbFile):
		channelListLameDB=[]
		with io.open(lambedbFile, encoding='utf-8', errors='ignore') as f:
			for line in f:
				lineUTF8 = line.encode('utf-8').decode('utf-8').rstrip()
				row = lineUTF8.split(",")
				if len(row) > 1:
					if row[0].startswith('s:') and row[1] != '':
						lCsv = row[0].split(":")

						# lCsv[5] == '2' // canais de radio
						if lCsv[5] == '1' or lCsv[5] == '25':
							strFinal = '1:0:'
							if lCsv[5] == '1':
								strFinal = strFinal + '1'
							elif lCsv[5] == '2':
								strFinal = strFinal + '2'
							elif lCsv[5] == '25':
								strFinal = strFinal + '19'
							strFinal = strFinal + ':' + lCsv[1].lstrip("0") + ':' + lCsv[3].lstrip("0") + ':' + lCsv[4].lstrip("0") + ':' + lCsv[2] + ':0:0:0:'
							nomeCanal = row[1].lstrip('"').rstrip('"')

							channelListLameDB.append([strFinal.upper(),nomeCanal])

			print(f"{datetime.datetime.now()} Terminado.")
			return channelListLameDB

def load_cabo_bouquet():
	print(f"{datetime.datetime.now()} Lendo busca por cabo em {caboBouquet}")
	listaCabo = []
	if os.path.isfile(caboBouquet):
		with io.open(caboBouquet, encoding='utf-8', errors='ignore') as f:
			for line in f:
				if line.startswith('#SERVICE'):
					if not line.startswith('#SERVICE 1:320') and not line.startswith('#SERVICE 1:0:CA') and not line.startswith('#SERVICE 1:0:90'):
						ln = line.replace("1:0:80", "1:0:1").split(' ')[1].strip()
						channel_number = int(ln.split(':')[3], 16)
						listaCabo.append([channel_number,ln])

	print(f"{datetime.datetime.now()} Terminado.")
	return listaCabo

def gerar_custom_bouquet(lamedb, lista):
	# bouquet format
	# https://www.opena.tv/english-section/43964-iptv-service-4097-service-1-syntax.html#post376271

	for i in lista:
		channel_name = ''
		for l in lamedb:
			if i[1] == l[0]:
				channel_name = l[1]
				i.append(channel_name)
				break
		if len(i) < 3:
			i.append("")
		# print(f"{i}  --> {channel_name}")
	return lista

def save_custom_bouquet(listaP):
	print(f"{datetime.datetime.now()} Criando custom bouquet: {customBouquetFile}")

	custom_bouquet = []
	custom_bouquet.append('#NAME NEW')
	count = 1
	for l in listaP:
		while count < l[0]:
			#SERVICE 1:320:0:0:0:0:0:0:0:0::-
			custom_bouquet.append(f"#SERVICE 1:320:0:0:0:0:0:0:0:0::-")
			count += 1

		custom_bouquet.append(f"#SERVICE {l[1]}:{l[2]}")
		count += 1

	arquivo_custom = open(customBouquetFile, 'w')
	arquivo_custom.write( "\n".join(custom_bouquet) )
	arquivo_custom.close()


	if not customBouquetName in open(bouquetList).read():
		with open(bouquetList, "a") as myfile:
			myfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + customBouquetName + '" ORDER BY bouquet\r\n')

	# print("\n".join(custom_bouquet) )
	try:
		refreshBouquet = urlopen('http://127.0.0.1/web/servicelistreload?mode=0')
	except:
		print(f"{datetime.datetime.now()} erro atualizando e2")

	print(f"{datetime.datetime.now()} Terminado.")

lameDb_channels = read_LameDB()
lista_cabo = load_cabo_bouquet()
lista_custom = gerar_custom_bouquet(lameDb_channels,lista_cabo)
save_custom_bouquet(lista_custom)
