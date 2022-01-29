#!/bin/python2
# -*- coding: utf-8 -*-

__version__ = "0.1.0"

import argparse
import logging
import os
import sys
import io
import urllib
import urllib2
import re
import unicodedata

CONFIG = {
    'devmode': False,
    'updateurl': "https://raw.githubusercontent.com/josemoraes99/enigma2_custom_bouquet/master/e2_configure_favoritos.py",
    'scriptsurl': "https://raw.githubusercontent.com/josemoraes99/enigma2_custom_bouquet/master/",
    'e2_conf_path': '/etc/enigma2/',
    'customBouquetName': 'userbouquet.netcabo.tv',
    'urlPicons': "https://hk319yfwbl.execute-api.sa-east-1.amazonaws.com/prod",
}

DEV_CONFIG = {
    'devmode': True,
    'updateurl': CONFIG['updateurl'],
    'scriptsurl': CONFIG['scriptsurl'],
    'e2_conf_path': 'tmp/',
    'customBouquetName': CONFIG['customBouquetName'],
    'urlPicons': CONFIG['urlPicons'],
}

def update(dl_url, force_update=False):
    """
https://gist.github.com/gesquive/8363131
Attempts to download the update url in order to find if an update is needed.
If an update is needed, the current script is backed up and the update is
saved in its place.
"""
    def compare_versions(vA, vB):
        """
Compares two version number strings
@param vA: first version string to compare
@param vB: second version string to compare
@author <a href="http_stream://sebthom.de/136-comparing-version-numbers-in-jython-pytho/">Sebastian Thomschke</a>
@return negative if vA < vB, zero if vA == vB, positive if vA > vB.
"""
        if vA == vB:
            return 0

        def num(s):
            if s.isdigit():
                return int(s)
            return s

        seqA = map(num, re.findall('\d+|\w+', vA.replace('-SNAPSHOT', '')))
        seqB = map(num, re.findall('\d+|\w+', vB.replace('-SNAPSHOT', '')))

        # this is to ensure that 1.0 == 1.0.0 in cmp(..)
        lenA, lenB = len(seqA), len(seqB)
        for i in range(lenA, lenB):
            seqA += (0,)
        for i in range(lenB, lenA):
            seqB += (0,)

        rc = cmp(seqA, seqB)

        if rc == 0:
            if vA.endswith('-SNAPSHOT'):
                return -1
            if vB.endswith('-SNAPSHOT'):
                return 1
        return rc

    # dl the first 256 bytes and parse it for version number
    try:
        http_stream = urllib.urlopen(dl_url)
        # update_file = http_stream.read(256)
        update_file = http_stream.read(300)
        http_stream.close()

    except IOError, (errno, strerror):
        logging.info("Unable to retrieve version data")
        logging.info("Error %s: %s" % (errno, strerror))
        return

    match_regex = re.search(r'__version__ *= *"(\S+)"', update_file)
    if not match_regex:
        logging.info("No version info could be found")
        return
    update_version = match_regex.group(1)

    if not update_version:
        logging.info("Unable to parse version data")
        return

    if force_update:
        logging.info("Forcing update, downloading version %s..." %
                     update_version)

    else:
        cmp_result = compare_versions(__version__, update_version)
        if cmp_result < 0:
            logging.info("Newer version %s available, downloading..." %
                         update_version)
        elif cmp_result > 0:
            logging.info("Local version %s newer then available %s, not updating." % (
                __version__, update_version))
            return
        else:
            logging.info("You already have the latest version.")
            return

    # dl, backup, and save the updated script
    app_path = os.path.realpath(sys.argv[0])
    # if __asModule__ == True:
    #     app_path = __file__

    if not os.access(app_path, os.W_OK):
        logging.info("Cannot update -- unable to write to %s" % app_path)

    dl_path = app_path + ".new"
    backup_path = app_path + ".old"
    try:
        dl_file = open(dl_path, 'w')
        http_stream = urllib.urlopen(dl_url)
        total_size = None
        bytes_so_far = 0
        chunk_size = 8192
        try:
            total_size = int(http_stream.info().getheader(
                'Content-Length').strip())
        except:
            # The header is improper or missing Content-Length, just download
            dl_file.write(http_stream.read())

        while total_size:
            chunk = http_stream.read(chunk_size)
            dl_file.write(chunk)
            bytes_so_far += len(chunk)

            if not chunk:
                break

            percent = float(bytes_so_far) / total_size
            percent = round(percent*100, 2)
            sys.stdout.write("Downloaded %d of %d bytes (%0.2f%%)\r" %
                             (bytes_so_far, total_size, percent))

            if bytes_so_far >= total_size:
                sys.stdout.write('\n')

        http_stream.close()
        dl_file.close()
    except IOError, (errno, strerror):
        logging.info("Download failed")
        logging.info("Error %s: %s" % (errno, strerror))
        return

    try:
        os.rename(app_path, backup_path)
    except OSError, (errno, strerror):
        logging.info("Unable to rename %s to %s: (%d) %s" %
                     (app_path, backup_path, errno, strerror))
        return

    try:
        os.rename(dl_path, app_path)
    except OSError, (errno, strerror):
        logging.info("Unable to rename %s to %s: (%d) %s" %
                     (dl_path, app_path, errno, strerror))
        return

    try:
        import shutil
        shutil.copymode(backup_path, app_path)
    except:
        os.chmod(app_path, 0755)

    logging.info("New version installed as %s" % app_path)
    logging.info("(previous version backed up to %s)" % (backup_path))
    return True






def read_LameDB(conf):
    lambedbFile = conf['e2_conf_path'] + 'lamedb5'
    logging.info("Lendo lamedb5 em %s" % lambedbFile)
    # print(f"{datetime.datetime.now()} Lendo lamedb5 em {lambedbFile}")
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

            logging.info("Lendo lamedb5 concluído")
            # print(f"{datetime.datetime.now()} Terminado.")
            return channelListLameDB

    logging.info("Lendo lamedb5 - abortado")
    sys.exit()

def load_cabo_bouquet(conf):
    caboBouquet = conf['e2_conf_path'] + 'userbouquet..tv'
    logging.info("Lendo busca por cabo em %s" % caboBouquet)
    # print(f"{datetime.datetime.now()} Lendo busca por cabo em {caboBouquet}")
    listaCabo = []
    if os.path.isfile(caboBouquet):
        with io.open(caboBouquet, encoding='utf-8', errors='ignore') as f:
            for line in f:
                if line.startswith('#SERVICE'):
                    if not line.startswith('#SERVICE 1:320') and not line.startswith('#SERVICE 1:0:CA') and not line.startswith('#SERVICE 1:0:90'):
                        ln = line.replace("1:0:80", "1:0:1").split(' ')[1].strip()
                        channel_number = int(ln.split(':')[3], 16)
                        listaCabo.append([channel_number,ln])

        logging.info("Lendo busca por cabo concluído")
        # print(f"{datetime.datetime.now()} Terminado.")
        return listaCabo

    logging.info("Lendo busca por cabo - abortado")
    sys.exit()

import uuid
import json

def obter_lista_externa(conf, list_send):
    uuid_one = uuid.getnode()
    picons_list = list(dict.fromkeys(list_send))
    params = {'src': 'kodi', 'node': uuid_one, 'listChannel': picons_list}
    params = json.dumps(params).encode('utf8')

    req = urllib2.Request(conf['urlPicons'], data=params, headers={
                  'content-type': 'application/json'})
    response = urllib2.urlopen(req)
    return json.load(response)
    # return list_url

def desativar_canais_duplicados(lista):
    """
    desativar canais sd quando houver em hd
    """
    logging.info("Desativar canais duplicados")
    list_channel = lista

    channels_to_remove = []
    for i in list_channel:
        iName = i["name"].lower().replace(' hd', '').replace('tv ', '').strip()
        iName = " ".join(iName.split())

        for j in list_channel:

            jName = j["name"].lower().replace(' hd', '').replace('tv ', '').strip()
            jName = " ".join(jName.split())

            if jName == iName and " hd" in i["name"].lower() and " hd" not in j["name"].lower():
                channels_to_remove.append(j)
                break

    for item in channels_to_remove:
        list_channel.remove(item)

    return list_channel

def cleanChannelName(ch):
    ch = unicode(ch)
    return re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', ch.replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))
    # return re.sub(re.compile('\W'), '', ''.join(c.lower() for c in unicodedata.normalize('NFKD', ch.replace("+", "mais")).encode('ascii', 'ignore') if not c.isspace()))

def desativar_canais_adultos(conf, lista):
    """
    desativar canais adultos
    """
    logging.info("Desativar canais adultos")
    list_channel = lista
    lista_envio = []
    for l in list_channel:
        cn_str = cleanChannelName(l['name'])
        if cn_str not in lista_envio:
            lista_envio.append(cn_str)

    list_ext = obter_lista_externa(conf, lista_envio)

    lista_canais_adultos = list_ext['listaCanaisAdultos']

    channels_to_remove = []

    for l in list_channel:
        cn_str = cleanChannelName(l['name'])
        if cn_str in lista_canais_adultos:
            channels_to_remove.append(l)

    for item in channels_to_remove:
        list_channel.remove(item)

    return list_channel

def desativar_canais_internos(conf, lista):
    """
    desativar canais interno
    """
    logging.info("Desativar canais internos")
    list_channel = lista
    lista_envio = []
    for l in list_channel:
        cn_str = cleanChannelName(l['name'])
        if cn_str not in lista_envio:
            lista_envio.append(cn_str)

    list_ext = obter_lista_externa(conf, lista_envio)

    lista_canais_internos = list_ext['listaCanaisInternos']

    # print lista_canais_internos
    # sys.exit()
    channels_to_remove = []

    for l in list_channel:
        cn_str = cleanChannelName(l['name'])
        if cn_str in lista_canais_internos:
            channels_to_remove.append(l)

    for item in channels_to_remove:
        list_channel.remove(item)

    return list_channel

def gerar_custom_bouquet(conf, lamedb, lista):
    # bouquet format
    # https://www.opena.tv/english-section/43964-iptv-service-4097-service-1-syntax.html#post376271

    final_list = []

    logging.info("Gerando lista de canais")
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

    for i in lista:
        final_list.append({
                'number': i[0],
                'uuid': i[1],
                'name': i[2],
            })

    if conf['desativar_canais_sd']:
        final_list = desativar_canais_duplicados(final_list)

    if conf['desativar_canais_adultos']:
        final_list = desativar_canais_adultos(conf, final_list)

    if conf['desativar_canais_internos']:
        final_list = desativar_canais_internos(conf, final_list)

    return final_list



def save_custom_bouquet(conf, listaP):
    customBouquetFile = conf['e2_conf_path'] + conf['customBouquetName']
    bouquetList       = conf['e2_conf_path'] + 'bouquets.tv'

    logging.info("Criando custom bouquet em " + customBouquetFile)
    # print(f"{datetime.datetime.now()} Criando custom bouquet: {customBouquetFile}")

    custom_bouquet = []
    custom_bouquet.append('#NAME NEW')
    count = 1
    for l in listaP:
        # while count < l[0]:
        while count < l['number']:
            #SERVICE 1:320:0:0:0:0:0:0:0:0::-
            custom_bouquet.append("#SERVICE 1:320:0:0:0:0:0:0:0:0::-")
            count += 1

        # custom_bouquet.append(f"#SERVICE {l[1]}:{l[2]}")
        # custom_bouquet.append("#SERVICE " + l[1] + ":" + l[2])
        custom_bouquet.append("#SERVICE " + l['uuid'] + ":" + l['name'])
        count += 1

    arquivo_custom = open(customBouquetFile, 'w')
    arquivo_custom.write( u"\n".join(custom_bouquet).encode('utf-8') )
    arquivo_custom.close()


    if not conf['customBouquetName'] in open(bouquetList).read():
        with open(bouquetList, "a") as myfile:
            myfile.write('#SERVICE 1:7:1:0:0:0:0:0:0:0:FROM BOUQUET "' + conf['customBouquetName'] + '" ORDER BY bouquet\r\n')

    try:
        refreshBouquet = urlopen('http://127.0.0.1/web/servicelistreload?mode=0')
    except:
        logging.info("erro atualizando e2")
        # print(f"{datetime.datetime.now()} erro atualizando e2")

    logging.info("Criando custom bouquet - terminado")
    # print(f"{datetime.datetime.now()} Terminado.")




def main():
    """Main function."""

    global CONFIG, DEV_CONFIG

    parser = argparse.ArgumentParser(
        description='Gerencia canais no Enigma2.')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--no-update', action='store_true',
                       help='não verifica por atualização')
    group.add_argument('--force-update', action='store_true',
                       help='força atualização')

    parser.add_argument(
        '--desativar-canais-sd', action='store_true', help='desativar canais sd quando hover em hd')
    parser.add_argument(
        '--desativar-canais-adultos', action='store_true', help='desativar canais adultos')
    parser.add_argument('--desativar-canais-internos',
                                 action='store_true', help='desativar canais internos da operadora')

    group_debug = parser.add_mutually_exclusive_group()
    group_debug.add_argument('--dev', action='store_true',
                             help='modo de testes - desenvolvimento')


    args = parser.parse_args()

    conf = CONFIG
    if args.dev:
        conf = DEV_CONFIG

    conf['desativar_canais_sd']       = args.desativar_canais_sd
    conf['desativar_canais_adultos']  = args.desativar_canais_adultos
    conf['desativar_canais_internos'] = args.desativar_canais_internos


    if args.dev:
        print(args)
        print(conf)

    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.DEBUG)
    logging.info("version %s", __version__)

    ck_updates = True
    if args.no_update or args.dev:
        ck_updates = False

    if args.force_update:
        update(conf['updateurl'], True)
        logging.info("alert", "Pronto.")
        sys.exit()

    if ck_updates:
        update_return = update(conf['updateurl'])
        if update_return:
            logging.info("alert", "Reiniciando script")
            python = sys.executable
            os.execl(python, python, *sys.argv)

    # check for e2 bouquet tv
    if not os.path.isfile(conf['e2_conf_path'] + 'bouquets.tv'):
        logging.info("bouquets.tv não encontrado, abortando.")
        sys.exit()


    lameDb_channels = read_LameDB(conf)
    lista_cabo = load_cabo_bouquet(conf)

    lista_custom = gerar_custom_bouquet(conf, lameDb_channels, lista_cabo)


    save_custom_bouquet(conf, lista_custom)

if __name__ == '__main__':
    main()
