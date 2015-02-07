/*
NOTEBOOK WATCHDOG - ALARME PARA NOTEBOOK BASEADO EM RF

Sistema capaz de monitorar a presença de um dispositivo devidamente equipado com uma tag RF do tipo MIFARE.
Utiliza a Intel Galileo Gen 2, o modulo RF MFRC522, o kit de Conectividade Telefonica e o kit Wearable da Telefonica.
Exige conexao a Internet.

Este sketch exige a instalacao da biblioteca MFRC522 disponivel em https://github.com/miguelbalboa/rfid

Os scripts Python executados tambem possuem dependencias que devem ser observadas. Leia a documentacao para
maiores informacoes
*/

#include <SPI.h>
#include <MFRC522.h>
#include <TimerOne.h>

//Pinagem do MFRC522
#define SS_PIN 10
#define RST_PIN 9

//Codigos internos
#define ACIONA_NOTEBOOK_REMOVIDO 10
#define ACIONA_BASE_REMOVIDA 20
#define wearLedR 0
#define wearLedG 1
#define wearLedB 2

//Contado da funcao heartbeat()
#define maxCount 30

//Informacoes do cartao: Preencha com os 18 bytes correspondentes ao setor e bloco desejado para servir como chave.
uint8_t cartaoNotebook[] = {0x30,0x30,0x30,0x38,0x35,0x38,0x36,0x37,0x33,0x32,0x30,0x32,0x31,0x30,0x31,0x0,0x1A,0xE1};
uint8_t cartaoDono[] = {0x30,0x30,0x30,0x38,0x35,0x38,0x36,0x37,0x33,0x32,0x30,0x32,0x31,0x30,0x31,0x0,0x1A,0xE1};
const int setor = 0, bloco = 1;

//Endereco BLE do dispositivo wearable
char wearBLEAdd[] = "00:0E:0B:00:39:CF";

const int ledRed = 4, ledGreen = 5, ledBlue = 6;
volatile int monitorar = 0, globalCount = 0;
int acoesSetup = 1, globalStatus = 0;

char comando[50];

MFRC522 mfrc522(SS_PIN, RST_PIN);	// Cria a instancia do leitor MFRC522.

void setup() {
	Serial.begin(9600);	// Inicia a comunicacao Serial com o computador (debug)
	SPI.begin();		// Inicia o barramento SPI
	mfrc522.PCD_Init();	// Inicia o leitor
        //Resetando Led RGB:
        pinMode(ledRed, OUTPUT);
        pinMode(ledGreen, OUTPUT);
        pinMode(ledBlue, OUTPUT);
        digitalWrite(ledRed, LOW);
        digitalWrite(ledGreen, LOW);
        digitalWrite(ledBlue, LOW);
        //Script de atualizacao de horario, disponivel em https://github.com/renanlino/galileoTimeSync
        Serial.println("Atualizando horario...");
        system("python /galileoTimeSync/readAndSetDateTime.py");
        // Inicializacao do modulo Bluetooth
        system("rfkill unblock all");
        system("hciconfig hci0 up");
        system("hciconfig hci0 reset");
        //Inicializacao das interrupcoes
        attachInterrupt(2, startMonitor, RISING);
        Timer1.initialize(1000000);
        Timer1.attachInterrupt( add );
        Serial.println("Inicializacao concluida...");
        
}

void loop() {
  uint8_t dadosCartao[18];
  int erros = 0;
  int acoesMonitoramento = 1;
  
  if (globalCount > maxCount){
      heartbeat();
    }
  
  if ( acoesSetup ) {
    acoesSetup = 0;
    digitalWrite(ledBlue, HIGH);
    digitalWrite(ledGreen, LOW);
    
    sprintf(comando, "python /notebookWatchdog/blue/setLed.py %s %d %d 1", wearBLEAdd, wearLedB, 255);
    system(comando);
    
    sprintf(comando, "python /notebookWatchdog/sendData.py 0");
    system(comando);
    globalStatus = 0;
    
    sprintf(comando, "python /notebookWatchdog/blue/setBuzzer.py %s 0", wearBLEAdd);
    system(comando);
    
    Serial.println("Aguardando interrupcao para iniciar monitoramento...");
    monitorar = 0;
  }
  
  while (monitorar) {
    
    if (globalCount > maxCount){
      heartbeat();
    }
    
    if ( acoesMonitoramento ) {
      acoesMonitoramento = 0;
      digitalWrite(ledBlue, LOW);
      digitalWrite(ledGreen, HIGH);
      Serial.println("Monitoramento iniciado!");
      
      sprintf(comando, "python /notebookWatchdog/blue/setLed.py %s %d %d 1", wearBLEAdd, wearLedG, 255);
      system(comando);
    
      sprintf(comando, "python /notebookWatchdog/sendData.py 1");
      system(comando);
      globalStatus = 1;
    }
    if ( readCard(dadosCartao) ) {
      erros = 0;
      if ( !compareVetores (dadosCartao, cartaoNotebook, 18) ) {
        Serial.println("Cartao apresentado nao corresponde ao notebook! ACIONANDO ALARME!");
        alarme(ACIONA_NOTEBOOK_REMOVIDO);
        break;
      }
    } else erros++;
    if (erros > 5) {
      Serial.println("Limite de erros de leitura excedidos! ACIONANDO ALARME!");
      alarme(ACIONA_NOTEBOOK_REMOVIDO);
      break;
    }
    if (! digitalRead(3) ) {
      Serial.println("Base afastada da mesa! ACIONANDO ALARME!");
      alarme(ACIONA_BASE_REMOVIDA);
      break;
    }
    delay(1000);
  }
}

void startMonitor() {
  //Chamada pela interrupcao do botao de monitoramento. Ativa a flag de monitoramento.
      if (!monitorar) {
        monitorar = 1;
      } 
}

int readCard(uint8_t buffer[]) {
  //Efetua a leitura dos 18 bytes presente em um bloco do cartao, conforme especificado anteriormente.
    uint8_t bufferSize = 18;
    //Geracao da chave: Utiliza a chave padrao dos cartoes Mifare.
    MFRC522::MIFARE_Key key;
    for (int i = 0; i < 6; i++) key.keyByte[i] = 0xFF;
    
    // Procura por um cartao na proximidade
    if ( ! mfrc522.PICC_IsNewCardPresent()) return 0;

    // Seleciona um cartao e le sua UID
    if ( ! mfrc522.PICC_ReadCardSerial()) return 0;

    //Autentica no setor desejado:
    if (mfrc522.PCD_Authenticate(MFRC522::PICC_CMD_MF_AUTH_KEY_A, 4 * setor + 3, &key, &(mfrc522.uid)) != MFRC522::STATUS_OK) return 0;

    
    // Le o bloco do cartao
    mfrc522.MIFARE_Read(4 * setor + bloco, buffer, &bufferSize);
    mfrc522.PCD_StopCrypto1();
    return 1;
}

void alarme(int evento) {
  //Executa as acoes necessaria para disparar o alarme em caso de remocao da base ou do notebook
  uint8_t dadosCartao[18];
  
  Serial.println("ALARME ACIONADO!");
  int pareAlarme = 0;
  
  digitalWrite(ledGreen, LOW);
  digitalWrite(ledRed, HIGH);
  digitalWrite(ledBlue, LOW); 
  
  sprintf(comando, "python /notebookWatchdog/sendData.py 2");
  system(comando);
  globalStatus = 2;
  
  sprintf(comando, "python /notebookWatchdog/blue/setLed.py %s %d %d 1", wearBLEAdd, wearLedR, 255);
  system(comando);
  
  sprintf(comando, "python /notebookWatchdog/blue/setBuzzer.py %s 1", wearBLEAdd);
  system(comando);
  
  while (!pareAlarme) {
    
    if (globalCount > maxCount){
      heartbeat();
    }
     
     if ( readCard(dadosCartao) ) {
       if ( compareVetores(dadosCartao, cartaoDono, 18) ) {
          pareAlarme = 1;
          monitorar = 0;
          acoesSetup = 1;
          digitalWrite(ledRed, LOW);
          digitalWrite(ledBlue, HIGH);
          Serial.println("ALARME 3 PELO USUARIO!");
          
          sprintf(comando, "python /notebookWatchdog/sendData.py 3");
          system(comando);
          
          sprintf(comando, "python /notebookWatchdog/blue/setLed.py %s %d %d 1", wearBLEAdd, wearLedR, 0);
          system(comando);
          
          sprintf(comando, "python /notebookWatchdog/blue/setBuzzer.py %s 0", wearBLEAdd);
          system(comando);
          
          return;
       }
     }
     delay(100);

  } 
}

int compareVetores(uint8_t a[], uint8_t b[], int size) {
  for (int i = 0;  i < size; i++){
    if (a[i] != b[i]) return 0; 
  }
  return 1;
}

void heartbeat() {
  //Funcao periodica que atualiza as informacoes no servidor mesmo que nao haja mudanca de status, para garantir conectividade
  //Reinicia o bluetooth para evitar que o dispositivo seja suspenso durante a execucao do programa
  //BUG CONHECIDO: As chamadas regulares de atualizacao do servidor causam erros nas informacoes gravas (codigos de status invalidos)
  Serial.println("Heartbeat!");
  system("hciconfig hci0 reset");
  //DESABILITADO: sprintf(comando, "python /notebookWatchdog/sendData.py %d", globalStatus);
  //DESABILITADO: system(comando);
  globalCount = 0;
}

void add() {
  globalCount++; 
}
