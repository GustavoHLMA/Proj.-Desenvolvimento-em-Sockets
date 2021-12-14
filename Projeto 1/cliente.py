from socket import socket, AF_INET, SOCK_DGRAM
import time
import sys

from threading import Thread
from threading import Lock


msgServidor_cliente = '' 
msgServidor_thread = '' 
alive = True
jogando = False


lock = Lock()

socketClient = socket(AF_INET, SOCK_DGRAM)


def enviarmensagem(mensagem):
    mensagemcliente = mensagem.encode()
    socketClient.sendto(mensagemcliente, ('localhost', 9500))


def recebermensagem():
    global alive
    global msgServidor_cliente
    global msgServidor_thread

    while alive:
        resposta_servidor = socketClient.recvfrom(1024)
        respostacliente = str(resposta_servidor[0].decode())

        estadocliente = ''
        mensagem = ''

        for x in respostacliente:
            if x == '&':
                estadocliente = mensagem
                mensagem = ''
            else:
                mensagem += x

        if estadocliente == 'Thread':
            msgServidor_thread = mensagem
        else:
            msgServidor_cliente = mensagem


def rodada():  
    
    global msgServidor_cliente
    global jogando

    while msgServidor_cliente == '':
        time.sleep(0.1)

    pergunta = msgServidor_cliente
    print("\nRound número", x + 1)
    print("\nPergunta:", pergunta) 

    if not jogando:
        sys.exit()

    respostacliente = input("Insira sua resposta: ")

    enviarmensagem('Cliente1&' + respostacliente)

    while True:

        if msgServidor_cliente == "errado":
            msgServidor_cliente = ''
            respostacliente = input("Resposta está errada, continue tentando: ")
            enviarmensagem('Cliente1&' + respostacliente)
        else:
            time.sleep(0.1)


print("Participe de uma competição relacionada a perguntas de química!")
print("\nDigite seu nome para começar:")

nome = input("Nome:")

while nome == '':
    nome = input("Nome inválido, tente novamente:")

enviarmensagem('Cliente0&' + nome)

thread = Thread(target=recebermensagem)
thread.start()


while alive:
    while msgServidor_cliente == '':
        time.sleep(0.1)

    if msgServidor_cliente == 'JaIniciou':
        print("Partida está em andamento")
        input("\nDigite qualquer tecla para sair da aplicação")
        exit(0)

    print(msgServidor_cliente)

    while msgServidor_cliente != 'start':
        time.sleep(0.1)

    msgServidor_cliente = ''
    
    print("A partida está prestes a começar!")

    jogando = True

    for x in range(5):  
        threadSec = Thread(target=rodada)  
        threadSec.start()

        while True:
            if msgServidor_cliente == 'correta' and x < 4:
                msgServidor_cliente = ''
                msgServidor_thread = ''
                print("\nVocê acertou!")
                print("\nPróxima pergunta:")
                break

            if msgServidor_cliente == 'correta' and x == 4:
                msgServidor_cliente = ''
                msgServidor_thread = ''
                print("\nVocê acertou!")
                break

            if msgServidor_thread == 'outro':
                msgServidor_thread = ''
                msgServidor_cliente = ''
                print("\nOutro participante acertou a pergunta ):")
                del threadSec
                break

            elif msgServidor_thread == 'tempoAcabou':
                msgServidor_thread = ''
                msgServidor_cliente = ''
                print("\nTempo esgotado")
                del threadSec
                break
            else:
                time.sleep(0.1)

    jogando = False
    print("\nPartida Finalizada! Pontuações finais:")

    while msgServidor_thread=='': 
        time.sleep(0.1)
    print(msgServidor_thread)
    msgServidor_thread = ''

    alive = False

    print("Obrigado por participar!")
