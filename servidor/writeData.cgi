#!/usr/bin/python
import cgi
import cgitb

cgitb.enable()

info = cgi.FieldStorage()

caminho = "status"
arquivoSaida = open(caminho, "w")

for label in info:
    data = str(info[label].value) + "\n"
    arquivoSaida.write(data)

arquivoSaida.close()

caminho = "log"
arquivoSaida = open(caminho, "a")

for label in info:
    data = str(info[label].value) + " "
    if data == "0 ":
        data = "Cod. 0: Sistema Iniciado    - "
    elif data == "1 ":
        data = "Cod. 1: Monitoramento Ativo - "
    elif data == "2 ":
        data = "Cod. 2: Alarme Acionado!    - "
    elif data == "3 ":
        data = "Cod. 3: Alarme Encerrado    - "
    arquivoSaida.write(data)
arquivoSaida.write("\n")

arquivoSaida.close()

print "Content-type:text/html\r\n\r\n"
print "<html>"
print "<head><title>File writer Python script</title></head>"
print "<body>"
print "File writer Python script"
print "</body>"
print "</html>"
