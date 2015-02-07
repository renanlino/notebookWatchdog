#!/usr/bin/python
import cgi
import cgitb
from datetime import datetime
from datetime import timedelta

error = False
try:
    lastStatus = open("status","r")
except:
    error = True
info = []
for linha in lastStatus:
    info.append(linha)
lastStatus.close()
try:
    status = int(info[0])
    dataeHora = info[1]
    dataeHora = dataeHora.split("-")
    dataCopy = dataeHora[0]
    data = dataCopy.split("/")
    hora = dataeHora[1]
    tempo = hora.split(":")
except:
    error = True

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head><title>Notebook Watchdog - Painel</title>"
print '<meta http-equiv="refresh" content="10">'
print '<style>p    {font-family:arial}</style></head>'
print "<body>"
print '<p align="center"><img src="web/dog.png">'
print '<img src="web/logo.png"></p><br>'
if error == 0:
    if status == 0:
        img = "web/wait.png"
        text = "Sistema iniciado, aguardando para monitorar!"
    elif status == 1:
        img = "web/check.png"
        text = "Monitoramento ativo. <br>Tudo tranquilo por aqui :)"
    elif status == 2:
        img = "web/alert.png"
        text = "ALARME ACIONADO!<br>Houston, we have a problem!"
    elif status == 3:
        img = "web/wait.png"
        text = "Alarme encerrado. Reiniciando sistema..."
else:
    img = "web/error.png"
    text = "Problemas na leitura de informa&ccedil;&otilde;es"
print '<p align="center"><img src="%s"></p>' %img
print '<p align="center"><b>%s</b></p>' %text
if error == 0:
    print '<p align="center">&Uacute;ltima atualiza&ccedil;&atilde;o em %s &agrave;s %s <br>' %(dataCopy, hora)
    tAtual = datetime.now()
    tLeitura = datetime(int(data[2]), int(data[1]), int(data[0]), int(tempo[0]), int(tempo[1]), int(tempo[2]))
    tDelta = tAtual - tLeitura

    deltaSegundos = tDelta.seconds % 60
    deltaMinutos = tDelta.seconds//60
    deltaHoras = deltaMinutos//60
    deltaMinutos = deltaMinutos % 60
    deltaDias = deltaHoras//24
    deltaHoras = deltaHoras % 24

    deltas = [deltaDias, deltaHoras, deltaMinutos, deltaSegundos]
    unidades = ["dia", "hora", "minuto", "segundo"]
    print '(h&aacute '
    string = ""
    for i in range(4):
        if deltas[i] != 0:
            string += "%d %s" %(deltas[i], unidades[i])
            if deltas[i] > 1:
                  string += "s"
            string += "#"
    string = string.split("#")
    if len(string) > 2:
        for i in range (len(string)-3):
            string[i] += ", "
        string[len(string)-3] += " e "
    for palavra in string:
        print palavra
    print ")"
print "</body>"
print "</html>"
