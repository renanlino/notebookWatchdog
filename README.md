Bibliotecas Python que devem ser instalados no Galileo antes do uso:
 - pexpect
 - ptyprocess
 - PyBluez
 - termcolor

Utilização
 - No Galileo:
	- Instalar as bilbiotecas Python necessárias
	- Instalar a biblioteca Arduino MFRC522 (https://github.com/miguelbalboa/rfid)
	- Enviar a sketch a pasta watchdogSketch ao Galileo
	- Copie o conteudo da pasta galileo para o segunte caminho de seu cartão SD: /notebookWatchdog/
	- Copie a pasta blue para dentro do diretorio /notebookWatchdog/
	- No script sendData.py, altere o nome do servidor para corresponder ao local de instalação da pasta

 - No servidor web:
	- Copie toda a pasta servidor para o diretorio desejado do websie
	- IMPORTANTE: Este repositório não fornece as imagens! Você deve providenciar as seguintes imagens, de acordo com sua preferência: alert.png, check.png, dog.png, error.png, logo.png, wait.png.
