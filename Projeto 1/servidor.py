from socket import socket, AF_INET, SOCK_DGRAM
import time
import random
from threading import Thread

socketServer = socket(AF_INET, SOCK_DGRAM)
socketServer.bind(('localhost', 9500))

acerto = None
comecou = False

respostaLogin = ''
respostaSemLogin = ''

addressLogin = None
addressSemLogin = None


def barrainvertida(linha):
    holder = ""
    for caractere in linha:
        if caractere != "\n":
            holder += caractere
    return holder


def par(n):
    if n % 2 == 0:
        return "par"
    else:
        return "impar"


def readtxt(arquivo):
    cont = 0
    lista = []
    holderTupla = ()
    for linha in arquivo:
        cont += 1
        caractere = barrainvertida(linha)
        tuplaAux = (caractere,)
        holderTupla += tuplaAux
        if par(cont) == "par":
            lista.append(holderTupla)
            holderTupla = ()
    return lista


def listenerClient():
    global respostaLogin
    global respostaSemLogin
    global addressLogin
    global addressSemLogin
    global comecou

    while(True):
        clienteStatus = ''
        mensagem = ''
        clientTxt = socketServer.recvfrom(2048)
        received = str(clientTxt[0].decode())     
        corteLinha = clientTxt[1]  

      

        for j in received:
            if (j != '&'):
                mensagem += j
            else:
                clienteStatus = mensagem
                mensagem = ''
               
        print("Recebeu",mensagem,"de",corteLinha[0])

        if(clienteStatus=="Cliente1"):
            respostaLogin = mensagem
            addressLogin =  corteLinha
        elif(clienteStatus=="Cliente0" and comecou):
            answerClient = str.encode('Cliente0&'+'JaIniciou')
            socketServer.sendto(answerClient, corteLinha)
            print("\nAlguem nao cadastrado tentou se conectar\n")

        else:
            respostaSemLogin = mensagem
            addressSemLogin =  corteLinha


def sendPlayers(mensagem, status): 
    global players    

    for cliente in players:  
        answerClient = str.encode(status+mensagem)
        socketServer.sendto(answerClient, cliente)


def sendPlayerFalse(pular):
    global players

    for cliente in players:
        if cliente != pular:
            answerClient = str.encode('Thread&'+'outro')
            socketServer.sendto(answerClient, cliente)
        else:
            resposta_acerto = str.encode('Cliente1&'+'correta')  
            socketServer.sendto(resposta_acerto, pular)


def game():
    global acerto
    global respostaLogin
    global addressLogin
    global comecou

    acerto = False

    sendPlayers(listaPerguntas[contador][0],'Cliente1&') 

    while True:
        if not comecou:
            break

        while respostaLogin=='':
            time.sleep(0.1)

        if not comecou:
            break

        if respostaLogin != listaPerguntas[contador][1]:

            answerClient = str.encode('Cliente1&'+'errado')   
            socketServer.sendto(answerClient, addressLogin)

            posicao = players.index(addressLogin)
            pontuacao[posicao] -= 5

            respostaLogin = ''
            acerto = False
                
        elif respostaLogin == listaPerguntas[contador][1] and acerto==False:

            print(addressLogin[0],"acertou")
            sendPlayerFalse(addressLogin) 

            posicao = players.index(addressLogin)
            pontuacao[posicao] += 25

            respostaLogin = ''
            acerto = True

            break


thread = Thread(target=listenerClient, daemon=True)  
thread.start()

print("Servidor escutando requisicoes...")

players = []
listaNomes = []
pontuacao = []

quant_jogadores = 5

continua = True

while continua:
    while len(players) < quant_jogadores:  

        while respostaSemLogin=='':
            time.sleep(0.1)

        listaNomes.append(respostaSemLogin)
        players.append(addressSemLogin)
        pontuacao.append(0)

        answerClient = str.encode(('Cliente1&\nAguardando outros participantes...\n'))
        socketServer.sendto(answerClient, addressSemLogin)

        respostaSemLogin=''

    time.sleep(5)
    arquivo = open("perguntas.txt", "r")
    todasPerguntas = readtxt(arquivo)   
    arquivo.close()

    listaPerguntas = random.sample(todasPerguntas, 5) 

    sendPlayers('start','Cliente1&')

    print("\nStarting")

    time.sleep(1)

    comecou = True

    for contador in range(5):  

        time.sleep(3)

        print("\nJogo nº:",contador+1)

        thread2 = Thread(target=game,daemon=True)  
        thread2.start()

        timer = 0
        while True:
            if acerto:
                acerto = False
                break
            
            if timer == 10:
                print("Tempo esgotado")
                sendPlayers('tempoAcabou','Thread&') 
                for contPontuacao in range(len(pontuacao)):
                    pontuacao[contPontuacao]-=1
                break
            else:
                time.sleep(1)
                timer += 1
        respostaLogin = ''
        addressLogin = ''

    totalP = ''

    for contListaNomes in range(len(listaNomes)):
        totalP += (listaNomes[contListaNomes]+" = " + str(pontuacao[contListaNomes]) + "\n")

    print("\nFim de Jogo! Pontuacoes da game:")
    print(totalP)

    time.sleep(1)

    sendPlayers(totalP,'Thread&')

    comecou = False
    players = []
    listaNomes = []
    pontuacao = []
    respostaLogin = ''
    respostaSemLogin = ''

    print("\nServidor escutando requisições...")


print("Após 20 segundos ninguém se conectou...\nServidor finalizado!")
