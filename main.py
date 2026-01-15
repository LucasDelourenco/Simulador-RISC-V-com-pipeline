from PyQt5 import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QAbstractItemView
import sys
import re

class Instrucao:
    def __init__(self, texto, linha_idx, fowarding):
        self.textoOG = texto.strip()
        self.texto = texto.strip()
        self.estagio_atual = 0  # -1: ainda não entrou -> mudado para 0 para ja começar em IF
        self.concluida = False
        self.executada = False
        self.linha_idx = linha_idx
        self.fowarding = fowarding

    def avancar(self):
        if self.estagio_atual < 4:
            self.estagio_atual += 1
        else:
            self.concluida = True

    def obter_estagio(self):
        estagios = ["IF", "ID", "EX", "MEM", "WB"]
        if 0 <= self.estagio_atual < len(estagios):
            return estagios[self.estagio_atual]
        return ""

    def IF(self):
        self.instrucao, self.texto = self.textoOG.split(' ', 1)
        self.texto.strip()
        return None
    
    def ID(self, registradores, registradores_forward, labels = None):
        return None
    
    def executar(self, registradores=None, registradores_foward=None, labels=None):
        return None  # sobrescrito por instruções como beq
    
    def M(self, memoria, registradores_foward=None):
        return None
    
    def WB(self, registradores = None):
        return None
    
class InstrucaoTipoR(Instrucao):

    def ID(self, registradores, registradores_forward, labels = None):
        self.rd, rs1, rs2 = self.texto.replace(",", " ").split()
        if(not self.fowarding):
            self.v1 = registradores.get(rs1, 0)
            self.v2 = registradores.get(rs2, 0)
        else:
            self.v1 = registradores_forward.get(rs1, 0)
            self.v2 = registradores_forward.get(rs2, 0)
        return None#self.linha_idx + 1
    
    def operacao(self, rs1, rs2):
        if self.instrucao == "add":
            return rs1+rs2
        if self.instrucao == "sub":
            return rs1-rs2
        if self.instrucao == "sll":
            return rs1 * (2**rs2)
        if self.instrucao == "srl":
            return rs1 / (2**rs2)
        if self.instrucao == "mul":
            return rs1*rs2
        if self.instrucao == "div":
            return int(rs1/rs2)
        if self.instrucao == "rem":
            return rs1%rs2
        if self.instrucao == "and":
            return rs1&rs2
        if self.instrucao == "or":
            return rs1|rs2
        if self.instrucao == "xor":
            return rs1^rs2
    
    def executar(self, registradores, registradores_foward, labels):
        self.resultado = self.operacao(self.v1, self.v2)
        self.executada = True
        if self.fowarding:
            registradores_foward[self.rd] = self.resultado

    def WB(self, registradores):
        if self.rd != "zero":
            registradores[self.rd] = self.resultado

class InstrucaoTipoB(Instrucao):
    def ID(self, registradores, registradores_forward, labels = None):
        rs1, rs2, label = self.texto.replace(",", " ").split()
        if(not self.fowarding):
            v1 = registradores.get(rs1, 0)
            v2 = registradores.get(rs2, 0)
        else:
            v1 = registradores_forward.get(rs1, 0)
            v2 = registradores_forward.get(rs2, 0)
        novoPc = labels.get(label, 0)

        self.executada = True

        if self.pular(v1, v2):
            return novoPc
        else:
            return self.linha_idx + 1

    def pular(self, rs1, rs2):
        if self.instrucao == "beq":
            if rs1 == rs2:
                return True
        elif self.instrucao == "bne":
            if rs1 != rs2:
                return True
        elif self.instrucao == "blt":
            if rs1 < rs2:
                return True
        elif self.instrucao == "bge":
            if rs1 >= rs2:
                return True
        elif self.instrucao == "bgt":
            if rs1 > rs2:
                return True
            
        return False

class InstrucaoJalr(Instrucao):
    def ID(self, registradores, registradores_forward, labels = None):
        rd, imm, rs1  = filter(None, re.split(r'[,()]+', self.texto))
        if(not self.fowarding):
            v1 = registradores.get(rs1, 0)
        else:
            v1 = registradores_forward.get(rs1, 0)
        enderecoDePulo = v1 + int(imm)
        enderecoProx = self.linha_idx + 1
        if rd != "zero":
            registradores[rd] = enderecoProx
        return enderecoDePulo

class InstrucaoTipoI(Instrucao):

    def ID(self, registradores, registradores_forward, labels = None):
        if(not self.fowarding):
            if (self.instrucao == "lw"):
                self.rd, self.imm, self.rs1  = filter(None, re.split(r'[,()]+', self.texto))
            elif (self.instrucao == "li"):
                self.rd, self.imm = self.texto.replace(",", " ").split()
            else:
                self.rd, self.rs1, self.imm = self.texto.replace(",", " ").split()
            if (self.instrucao != "li"):
                self.v1 = registradores.get(self.rs1, 0)
            else:
                self.v1 = 0
        else:
            if (self.instrucao == "lw"):
                self.rd, self.imm, self.rs1  = filter(None, re.split(r'[,()]+', self.texto))
            elif (self.instrucao == "li"):
                self.rd, self.imm = self.texto.replace(",", " ").split()
            else:
                self.rd, self.rs1, self.imm = self.texto.replace(",", " ").split()
            if (self.instrucao != "li"):
                self.v1 = registradores_forward.get(self.rs1, 0)
            else:
                self.v1 = 0

        self.imm = int(self.imm)

        return None#self.linha_idx + 1

    def executar(self, registradores, registradores_foward, labels):
        if self.instrucao == "li":
            self.resultado = self.imm
        else:
            self.resultado = self.v1 + self.imm
        self.executada = True
        if self.fowarding and not (self.instrucao in ["lw", "lh", "lb"]):
            registradores_foward[self.rd] = self.resultado

    def M(self, memoria, registradores_foward):
        if self.instrucao in ["lw", "lh", "lb"]:
            self.resultado = int(self.resultado/4)
            self.resultado = memoria[self.resultado]
            if self.fowarding:
                registradores_foward[self.rd] = self.resultado

    def WB(self, registradores):
        if self.rd != "zero":
            registradores[self.rd] = self.resultado

class InstrucaoTipoJ(Instrucao):
    def ID(self, registradores, registradores_forward, labels):
        if(self.instrucao == "j"):
            rd = "zero"
            label = self.texto
        else:
            rd, label = self.texto.replace(",", " ").split()
        enderecoDePulo = labels.get(label, 0)
        enderecoProx = self.linha_idx + 1

        if self.instrucao == "j":
            rd = "zero"

        if rd != "zero":
            registradores[rd] = enderecoProx

        return enderecoDePulo

class InstrucaoMv(Instrucao):
    def __init__(self, texto, linha_idx, forwarding):
        super().__init__(texto, linha_idx, forwarding)
        self.texto = self.texto + ",0"
        self.aux = InstrucaoTipoI(self.texto, linha_idx, forwarding)

    def IF(self):
        self.aux.IF()

    def ID(self, registradores, registradores_forward, labels):
        return self.aux.ID(registradores, registradores_forward, labels)

    def executar(self, registradores, registradores_foward, labels):
        self.aux.executar(registradores, registradores_foward, labels)

    def WB(self, registradores):
        self.aux.WB(registradores)

class InstrucaoSw(Instrucao):
    def ID(self, registradores, registradores_forward, labels):
        rs1, self.imm, rs2 = filter(None, re.split(r'[,()]+', self.texto))
        if(not self.fowarding):
            self.v2 = registradores.get(rs2, 0)
            self.v1 = registradores.get(rs1, 0)
        else:
            self.v2 = registradores_forward.get(rs2, 0)
            self.v1 = registradores_forward.get(rs1, 0)
        self.imm = int(self.imm)
        
        return None#self.linha_idx + 1

    def executar(self, registradores, registradores_foward, labels):
        self.endereco = self.v2/4 + self.imm/4

    def M(self, memoria, registradores_foward):
        memoria[int(self.endereco)] = self.v1

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Simulador RISC-V Pipeline")
        self.resize(1200, 600)

        layout_principal = QVBoxLayout()
        # ---- Controles Superiores ----
        layout_controles = QHBoxLayout()
        self.botao_arquivo = QPushButton("Selecionar Arquivo (.bin ou .asm)")
        self.botao_arquivo.clicked.connect(self.abrir_arquivo)
        self.label_arquivo = QLabel("Nenhum arquivo selecionado")

        self.botao_run = QPushButton("▶ Iniciar")
        menu_iniciar = QMenu(self)

        acao_basica = QAction("Sem Forwarding", self)
        acao_com_forwarding = QAction("Com Forwarding", self)

        acao_basica.triggered.connect(lambda: self.carregar_pipeline(forwarding=False))
        acao_com_forwarding.triggered.connect(lambda: self.carregar_pipeline(forwarding=True))

        menu_iniciar.addAction(acao_basica)
        #menu_iniciar.addSeparator()
        menu_iniciar.addAction(acao_com_forwarding)

        self.botao_run.setMenu(menu_iniciar)
        self.botao_run.clicked.connect(self.carregar_pipeline)

        self.botao_finish = QPushButton("⏭ Finalizar")
        self.botao_finish.clicked.connect(self.finalizar_execucao)
        self.botao_next = QPushButton("▷ Proximo")
        self.botao_next.clicked.connect(self.ir_para_proximo)
        
        layout_controles.addWidget(self.botao_arquivo)
        layout_controles.addWidget(self.label_arquivo, 1)
        layout_controles.addWidget(self.botao_run)
        layout_controles.addWidget(self.botao_finish)
        layout_controles.addWidget(self.botao_next)
        
        # --- Divisor de tela ---
        splitterH = QSplitter(Qt.Horizontal)
        splitterV = QSplitter(Qt.Vertical)
        
        # --- Painel Esquerdo (Pipeline) ---
        container_pipeline = QWidget()
        layout_pipeline = QVBoxLayout(container_pipeline)
        self.tabela = QTableWidget()
        self.tabela.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tabela.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        layout_pipeline.addWidget(QLabel("Diagrama de Pipeline"))
        layout_pipeline.addWidget(self.tabela)
        
        # --- Painel Direito (Registradores e Memória) ---
        container_detalhes = QWidget()
        layout_detalhes = QVBoxLayout(container_detalhes)
        self.tabela_registradores = QTableWidget()
        self.tabela_registradores.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.tabela_memoria = QTableWidget()
        self.tabela_memoria.setEditTriggers(QAbstractItemView.NoEditTriggers)
        splitterV = QSplitter(Qt.Vertical)

        # Painel Registradores
        widget_registradores = QWidget()
        layout_reg = QVBoxLayout(widget_registradores)
        layout_reg.addWidget(QLabel("Registradores"))
        layout_reg.addWidget(self.tabela_registradores)

        # Painel Memória
        widget_memoria = QWidget()
        layout_mem = QVBoxLayout(widget_memoria)
        layout_mem.addWidget(QLabel("Memória"))
        layout_mem.addWidget(self.tabela_memoria)

        # Adiciona os dois painéis ao splitter vertical
        splitterV.addWidget(widget_registradores)
        splitterV.addWidget(widget_memoria)
        splitterV.setSizes([500, 162]) #500, 10

        layout_detalhes.addWidget(splitterV)
        
        splitterH.addWidget(container_pipeline)
        splitterH.addWidget(container_detalhes)
        splitterH.setSizes([800, 190]) 
        
        self.tabs = QTabWidget()
        self.texto_codigo = QTextEdit()
        self.texto_codigo.setReadOnly(True)
        self.tabs.addTab(splitterH, "Simulação")
        self.tabs.addTab(self.texto_codigo, "Código do Arquivo")

        layout_principal.addLayout(layout_controles)
        layout_principal.addWidget(self.tabs)
        self.setLayout(layout_principal)

        layout_principal.addWidget(self.tabs)



        self.text = []
        self.instrucoes = []
        self.registradores = {"zero":0 , "ra":0, "sp":0, "gp":0, "tp":0, "t0":0,
                               "t1":0, "t2":0, "s0":0, "s1":0, "a0":0, "a1":0, "a2":0, "a3":0, 
                               "a4":0, "a5":0, "a6":0, "a7":0, "s2":0, "s3":0, "s4":0, "s5":0, 
                               "s6":0, "s7":0, "s8":0, "s9":0, "s10":0, "s11":0, "t3":0, "t4":0, "t5":0, "t6":0}
        self.registradoresForwarding = {"zero":0 , "ra":0, "sp":0, "gp":0, "tp":0, "t0":0,
                               "t1":0, "t2":0, "s0":0, "s1":0, "a0":0, "a1":0, "a2":0, "a3":0, 
                               "a4":0, "a5":0, "a6":0, "a7":0, "s2":0, "s3":0, "s4":0, "s5":0, 
                               "s6":0, "s7":0, "s8":0, "s9":0, "s10":0, "s11":0, "t3":0, "t4":0, "t5":0, "t6":0}
        self.valsPorCiclo = [] #matriz
        self.memPorCiclo = []
        self.labels = {}
        self.memoria = {}
        self.ciclo_atual = 0
        self.nop_count = 0
        self.forwarding = False #por enquanto
        
    def mostrar_codigo(self,textoCodigo):
        if textoCodigo:
            self.texto_codigo.setPlainText(textoCodigo)
            #self.tabs.setCurrentIndex(1) #chama para essa aba
        else:
            self.texto_codigo.setPlainText("Nenhum arquivo carregado.")

    def abrir_arquivo(self):
        caminho, _ = QFileDialog.getOpenFileName(
            self,
            "Selecionar Arquivo",
            "",
            "Arquivos BIN/ASM (*.bin *.asm);;Todos os arquivos (*)"
        )
        if caminho:
            self.label_arquivo.setText(caminho)
            #self.carregar_pipeline(caminho)
        self.botao_run.setText("▶ Iniciar")
        self.tabela.clear()           # Remove o conteúdo das células e os cabeçalhos
        self.tabela.setRowCount(0)    # Zera o número de linhas
        self.tabela.setColumnCount(0) # Zera o número de colunas

    def criar_instrucao(self, texto, idx):
        tipo_R = ["add", "sub", "xor", "or", "and", "sll", "srl", "sra", "slt", "sltu", "div"]
        tipo_I = ["addi", "xori", "ori", "andi", "slli", "srli", "srai", "slti", "sltiu", "lb", "lh", "lw", "lbu", "lhu", "li"]
        tipo_S = ["sb", "sh", "sw"]
        tipo_B = ["beq", "bne", "blt", "bge", "bltu", "bgeu", "bgt"]
        tipo_J = ["j", "jal"]
        mnem = texto.split(" ")[0]
        if mnem == "jalr":
            return InstrucaoJalr(texto, idx, self.forwarding)
        elif mnem == "mv":
            return InstrucaoMv(texto, idx, self.forwarding)
        elif mnem in tipo_R:
            return InstrucaoTipoR(texto, idx, self.forwarding)
        elif mnem in tipo_B:
            return InstrucaoTipoB(texto, idx, self.forwarding)
        elif mnem in tipo_I:
            return InstrucaoTipoI(texto, idx, self.forwarding)
        elif mnem in tipo_S:
            return InstrucaoSw(texto, idx, self.forwarding)
        elif mnem in tipo_J:
            return InstrucaoTipoJ(texto, idx, self.forwarding)
        else:
            return Instrucao(texto, idx, self.forwarding)

    def extrair_registradores_fonte(self,instrucao):
        partes = instrucao.strip().split(" ")
        if len(partes) < 2:
            return []

        argumentos = partes[1].split(",")

        if partes[0] in ["lw", "lh", "lb","li"]:  # Load
            # Formato: lw rd, offset(rs1)
            if len(argumentos) >= 2:
                arg = argumentos[1]
                rs1 = arg[arg.find("(")+1 : arg.find(")")]
                return [rs1]
        
        elif partes[0] in ["sb", "sh", "sw"]:
            if len(argumentos) >= 2:
                rs1 = argumentos[0]
                return [rs1]

        elif partes[0] in ["beq", "bne", "blt", "bge", "bltu", "bgeu", "bgt"]:
            if len(argumentos) >= 3:
                return [argumentos[0],argumentos[1]]
            else:
                return []

        else:
            # Formato: op rd, rs1, rs2
            if len(argumentos) >= 3:
                return [argumentos[1], argumentos[2]]
            elif len(argumentos) == 2:
                return [argumentos[1]]
            else:
                return []

        

        return []

    def executar_um_ciclo(self,pos):
        prox = -1
        for instr in self.instrucoes:
            if(not(instr.concluida) and instr.texto!="addi zero,zero,0".strip()):
                match instr.obter_estagio():
                    case "IF":
                        instr.IF()
                    case "ID":
                        prox = instr.ID(self.registradores,self.registradoresForwarding,self.labels)
                    case "EX":
                        instr.executar(self.registradores,self.registradoresForwarding,self.labels)
                    case "MEM":
                        instr.M(self.memoria,self.registradoresForwarding)
                    case "WB":
                        instr.WB(self.registradores)
                instr.avancar()

        self.valsPorCiclo.append(self.registradores.copy()) #atualizando val registradores
        self.memPorCiclo.append(self.memoria.copy())
        if(prox != None and prox != -1):
            return prox
        else:
            return pos+1

    def encher_selfInstrucoes(self):
        pos = 0
        ult_rd = " "
        ult_rd2 = " "
        loads_sem_li = ["lw", "lh", "lb"]
        saves = ["sb", "sh", "sw"]
        desvios = ["beq", "bne", "blt", "bge", "bltu", "bgeu", "bgt","j", "jal","jalr"]

        self.nop_count=0
        nop = "addi zero,zero,0"  
        # Na hora de colocar na tabela se ler "addi zero,zero,0" vai escrever "nop" na posicao da tabela 
        # e continuar a escrita dos estagios a seguir(na coluna j + 1)

        #Sem Forwarding:
        self.valsPorCiclo.append(self.registradores.copy()) #estado dos registradores antes de nenhum ciclo
        self.memPorCiclo.append(self.memoria.copy())
        while(pos != len(self.text)):
            #print(pos) #Print para debug
            lin = self.text[pos]
            instr_count = len(self.instrucoes)
            if(instr_count>=2):
                inst_ant2 = self.instrucoes[instr_count-2]
                if(not(inst_ant2.texto.split(" ")[0] in desvios)): #se nao é desvio tem rd
                    if(inst_ant2.texto.split(" ")[0] in saves): #sw rs,0(rd)
                        arg = inst_ant2.texto.split(" ")[1]
                        ult_rd2 = arg[arg.find("(")+1 : arg.find(")")]
                    else:
                        #ult_rd2 = inst_ant2.texto.split(" ")[1].split(",")[0]  #op rd,blabla
                        ult_rd2 = inst_ant2.texto.split(",")[0]
                else:
                    ult_rd2 = " "
            
            if not(":" in lin):
                rs = self.extrair_registradores_fonte(lin)
                if(not(self.forwarding)):
                    if(ult_rd!= " " and ult_rd in rs): #instrucao atual depende do rd da instrucao anterior, 2 nops
                        self.instrucoes.append(self.criar_instrucao(nop, -1))
                        self.instrucoes.append(self.criar_instrucao(nop, -1))
                        self.executar_um_ciclo(pos)
                        self.executar_um_ciclo(pos)
                        self.nop_count+=2
                    elif(ult_rd2!= " " and ult_rd2 in rs): #instrucao atual depende do rd da penultima instrucao, 1 nop
                        self.instrucoes.append(self.criar_instrucao(nop, -1))
                        self.executar_um_ciclo(pos)
                        self.nop_count+=1
                else:
                    if(instr_count>0 and self.instrucoes[instr_count-1] in loads_sem_li and ult_rd!=" " and ult_rd in rs):
                        self.instrucoes.append(self.criar_instrucao(nop, -1))
                        self.executar_um_ciclo(pos)
                        self.nop_count+=1


                    
                
                
                #Atualizando ult_rd
                if(lin.split(" ")[0] in saves): #sw rs,0(rd)
                    arg = lin.split(" ")[1]
                    ult_rd = arg[arg.find("(")+1 : arg.find(")")]
                else:
                    ult_rd = lin.split(" ")[1].split(",")[0]  #op rd,blabla

                self.instrucoes.append(self.criar_instrucao(lin,pos))
                
                #"executando" um ciclo:

                #Caso seja desvio, coloca um nop e zera os rds
                if(lin.split(" ")[0] in desvios):
                    self.executar_um_ciclo(pos)
                    prox = self.executar_um_ciclo(pos)
                    self.instrucoes.append(self.criar_instrucao(nop, -1))
                    ult_rd = " "
                    ult_rd2 = " "
                    self.nop_count+=1
                else:
                    prox = self.executar_um_ciclo(pos)
                #self.valsPorCiclo.append(self.registradores) #estado registradores depois do ciclo atual
                #Movido para dentro do executar_um_ciclo ^

                if(prox != None):
                    pos = prox
                else:
                    pos+=1
                


            else:
                pos+=1

        i=0
        for i in range(5):
            self.executar_um_ciclo(pos)


    def carregar_pipeline(self,forwarding):
        try:
            self.forwarding = forwarding
            #self.botao_run.setText("⟳ Reiniciar")
            scrollbar = self.tabela.verticalScrollBar()
            scrollbar.setValue(0)
            self.tabela.clear()           # Remove o conteúdo das células e os cabeçalhos
            self.tabela.setRowCount(0)    # Zera o número de linhas
            self.tabela.setColumnCount(0) # Zera o número de colunas
            self.text = []
            self.instrucoes = []
            self.memoria = {}
            self.registradores = {"zero":0 , "ra":0, "sp":0, "gp":0, "tp":0, "t0":0,
                                "t1":0, "t2":0, "s0":0, "s1":0, "a0":0, "a1":0, "a2":0, "a3":0, 
                                "a4":0, "a5":0, "a6":0, "a7":0, "s2":0, "s3":0, "s4":0, "s5":0, 
                                "s6":0, "s7":0, "s8":0, "s9":0, "s10":0, "s11":0, "t3":0, "t4":0,
                                "t5":0, "t6":0}
            self.registradoresForwarding = {"zero":0 , "ra":0, "sp":0, "gp":0, "tp":0, "t0":0,
                               "t1":0, "t2":0, "s0":0, "s1":0, "a0":0, "a1":0, "a2":0, "a3":0, 
                               "a4":0, "a5":0, "a6":0, "a7":0, "s2":0, "s3":0, "s4":0, "s5":0, 
                               "s6":0, "s7":0, "s8":0, "s9":0, "s10":0, "s11":0, "t3":0, "t4":0, "t5":0, "t6":0}
            self.valsPorCiclo = [] #matriz
            self.memPorCiclo = []
            self.labels = {}
            self.ciclo_atual = 0
            caminho = self.label_arquivo.text()
            if not caminho or caminho.startswith("Erro") or caminho == "Nenhum arquivo selecionado":
                return
            with open(caminho, 'rb') as f:
                dados = f.read()
                try:
                    texto = dados.decode("utf-8")
                except UnicodeDecodeError:
                    texto = dados.decode("latin-1")

            self.botao_run.setText("⟳ Reiniciar")
            self.mostrar_codigo(texto)
            
            pre_linhas = [linha.strip() for linha in texto.strip().split('\n') if linha.strip()]
            self.text=[]
            valendo = True

            if(pre_linhas[0]==".data"):
                valendo = False
            for linha in pre_linhas:
                if(linha == ".text"):
                    valendo = True
                    continue
                if(not valendo or linha=="ecall" or linha.split(" ")[0] == "la"):
                    continue
                if(valendo):
                    self.text.append(linha)
                    if ":" in linha:
                        label = linha.split(":")[0].strip()
                        self.labels[label] = len(self.text)
                        continue
    
    
            self.encher_selfInstrucoes()

            # for tmp in self.instrucoes:  #Debug
            #     print(tmp.texto)

            i=0
            num_instr=0
            for i in range(len(self.instrucoes)):
                if(self.instrucoes[i].texto != "addi zero,zero,0"):
                    num_instr+=1
            #num_instr = len(self.instrucoes) #substituir self.text em self.instrucoes
            num_ciclos = num_instr + 4 + self.nop_count  #ciclos p/cada instr + enchimento + bolhas
            # Print para debug v
            # print("\n" + "NumInstrucoes:" + str(num_instr) + "\n" + "NumColunas: " + str(num_ciclos))

            self.tabela.setRowCount(num_instr)
            self.tabela.setColumnCount(num_ciclos)

            # Cabeçalhos de coluna: ciclos 0, 1, 2, ...
            self.tabela.setHorizontalHeaderLabels([str(i+1) for i in range(num_ciclos)])
            # Cabeçalhos de linha: instruções
            i=0
            ind_linha = 0
            while i < num_instr:
                texto_linha = self.instrucoes[ind_linha]
                if(texto_linha.texto != "addi zero,zero,0"):
                    item = QTableWidgetItem(texto_linha.textoOG)
                    self.tabela.setVerticalHeaderItem(i, item)
                    i += 1
                ind_linha+=1
            self.tabela.setHorizontalHeaderItem(0, QTableWidgetItem("Atual"))

            estagios = ['IF', 'ID', 'EX', 'MEM', 'WB']

            #alterar para pular uma coluna para NOP -> logica de enumerate nao funciona nesse caso, trocar logica
            # for i, instr in enumerate(self.text):
            #     for j, estagio in enumerate(estagios):
            #         coluna = i + j
            #         item = QTableWidgetItem(estagio)
            #         item.setTextAlignment(Qt.AlignCenter)
            #         self.tabela.setItem(i, coluna, item)
            i=0
            j=0
            coluna_ini_atual=0
            ind_linha=0
            while(i < num_instr):
                while(j < 5):
                    if(self.instrucoes[ind_linha].texto == "addi zero,zero,0"):
                        coluna = coluna_ini_atual
                        item = QTableWidgetItem("(nop)")
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabela.setItem(i, coluna, item)
                        coluna_ini_atual+=1
                        ind_linha+=1
                    else:
                        coluna = coluna_ini_atual + j
                        item = QTableWidgetItem(estagios[j])
                        item.setTextAlignment(Qt.AlignCenter)
                        self.tabela.setItem(i, coluna, item)
                        #print("a" + str(i))
                        j+=1
                i+=1
                ind_linha+=1
                j=0
                coluna_ini_atual+=1



            self.registradores = {"zero":0 , "ra":0, "sp":0, "gp":0, "tp":0, "t0":0,
                                "t1":0, "t2":0, "s0":0, "s1":0, "a0":0, "a1":0, "a2":0, "a3":0, 
                                "a4":0, "a5":0, "a6":0, "a7":0, "s2":0, "s3":0, "s4":0, "s5":0, 
                                "s6":0, "s7":0, "s8":0, "s9":0, "s10":0, "s11":0, "t3":0, "t4":0,
                                "t5":0, "t6":0}
            self.memoria = {}
            self.atualizar_tabela_registradores()
            self.atualizar_tabela_memoria()
            self.destacar_celulas_atual_verde()

        except Exception as e:
            self.label_arquivo.setText(f"Erro ao carregar pipeline: {e}")


    def imprimir_debug_terminal(self):
        caminho = self.label_arquivo.text()
        if not caminho or caminho.startswith("Erro") or caminho == "Nenhum arquivo selecionado":
            return  # não faz nada se não houver arquivo válido

        try:
            with open(caminho, "rb") as f:
                dados_binarios = f.read()
                texto = dados_binarios.decode("utf-8")
                linhas = texto.strip().split('\n')
                comeca = False

                for i, linha in enumerate(linhas):
                    if comeca:
                        print(f"Linha {i + 1}: {linha}")
                    if linha.strip().split(' ')[0] == ".text":
                        comeca = True
        except Exception as e:
            print(f"Erro ao executar: {e}")


    def deslocar_tabela_para_esquerda(self):
        row_count = self.tabela.rowCount()
        col_count = self.tabela.columnCount()

        for row in range(row_count):
            for col in range(1, col_count):
                item = self.tabela.item(row, col)
                if item:
                    novo_item = QTableWidgetItem(item.text())
                    novo_item.setTextAlignment(Qt.AlignCenter)
                    self.tabela.setItem(row, col - 1, novo_item)
                else:
                    self.tabela.setItem(row, col - 1, QTableWidgetItem(""))

            # Limpar a última coluna após o deslocamento
            self.tabela.setItem(row, col_count - 1, QTableWidgetItem(""))

        # Atualizar os rótulos das colunas
        headers = [self.tabela.horizontalHeaderItem(i).text() for i in range(1, col_count)]
        headers.append(str(int(headers[-1]) + 1) if headers else str(col_count))
        self.tabela.setHorizontalHeaderLabels(headers)
        self.tabela.setColumnCount(col_count - 1)
        self.tabela.setHorizontalHeaderItem(0, QTableWidgetItem("Atual"))


    def deslocar_tabela_para_cima(self): #Descartado
        row_count = self.tabela.rowCount()
        col_count = self.tabela.columnCount()

        novos_rotulos = []

        for row in range(1, row_count):
            # Pega o rótulo da linha de baixo e usa para a de cima
            header_item = self.tabela.verticalHeaderItem(row)
            novos_rotulos.append(header_item.text() if header_item else "")
            
            for col in range(col_count):
                item = self.tabela.item(row, col)
                if item:
                    novo_item = QTableWidgetItem(item.text())
                    novo_item.setTextAlignment(Qt.AlignCenter)
                    self.tabela.setItem(row - 1, col, novo_item)
                else:
                    self.tabela.setItem(row - 1, col, QTableWidgetItem(""))

        # Aplica os novos rótulos de linha
        self.tabela.setVerticalHeaderLabels(novos_rotulos)

        # Remove a última linha
        self.tabela.setRowCount(row_count - 1)



    def atualizar_tabela_registradores(self):
        registros = self.registradores
        num_registradores = 32

        valores_anteriores = []
        for i in range(num_registradores):
            item = self.tabela_registradores.item(i, 1)
            valores_anteriores.append(item.text() if item else None)

        self.tabela_registradores.setRowCount(num_registradores)
        self.tabela_registradores.setColumnCount(2)
        self.tabela_registradores.setHorizontalHeaderLabels(["Registrador", "Valor"])

        for i in range(num_registradores):
            nome = list(registros.keys())[i]
            valor = registros[nome]

            item_nome = QTableWidgetItem(nome)
            item_nome.setTextAlignment(Qt.AlignCenter)

            item_valor = QTableWidgetItem(str(valor))
            item_valor.setTextAlignment(Qt.AlignCenter)

            valor_antigo = valores_anteriores[i]
            if valor_antigo is not None and valor_antigo != str(valor):
                item_valor.setBackground(QColor(255, 255, 200))  # amarelo claro

            self.tabela_registradores.setItem(i, 0, item_nome)
            self.tabela_registradores.setItem(i, 1, item_valor)

            # Faz scroll para a célula que mudou de valor
            if valor_antigo is not None and valor_antigo != str(valor):
                index = self.tabela_registradores.model().index(i, 1)
                self.tabela_registradores.scrollTo(index, QAbstractItemView.PositionAtCenter)

        labels = [f"x{i}" for i in range(num_registradores)]
        self.tabela_registradores.setVerticalHeaderLabels(labels)
        self.tabela_registradores.setColumnWidth(0, 80)
        self.tabela_registradores.setColumnWidth(1, 60)



            

    def linha_esta_vazia(self, row):
        col_count = self.tabela.columnCount()
        for col in range(col_count):
            item = self.tabela.item(row, col)
            if item and item.text().strip() != "":
                return False
        return True
    def ajustar_scroll_se_linha_vazia(self):
        row_count = self.tabela.rowCount()
        col_count = self.tabela.columnCount()
        
        linhas_vazias_no_topo = 0
        for row in range(row_count):
            # Verifica se a linha está vazia
            linha_vazia = True
            for col in range(col_count):
                item = self.tabela.item(row, col)
                if item and item.text().strip() != "":
                    linha_vazia = False
                    break
            if linha_vazia:
                linhas_vazias_no_topo += 1
            else:
                break  # para ao encontrar a primeira linha com conteúdo

        # Queremos scroll ser linhas_vazias_no_topo - 1, mas no mínimo zero
        scroll_target = max(linhas_vazias_no_topo - 1, 0)
        
        scrollbar = self.tabela.verticalScrollBar()
        max_scroll = scrollbar.maximum()
        # Ajusta o scroll para o alvo, mas respeitando o máximo
        nova_pos = min(scroll_target, max_scroll)
        scrollbar.setValue(nova_pos)

    def destacar_celulas_atual_verde(self):
        tabela = self.tabela
        col_count = tabela.columnCount()
        row_count = tabela.rowCount()

        # Encontrar o índice da coluna "Atual" (se não for sempre 0)
        col_atual = 0
        for col in range(col_count):
            header_item = tabela.horizontalHeaderItem(col)
            if header_item and header_item.text() == "Atual":
                col_atual = col
                break

        cor_verde_suave = QColor(200, 255, 200)  # verde clarinho

        for row in range(row_count):
            item = tabela.item(row, col_atual)
            if item and item.text().strip() != "":
                item.setBackground(cor_verde_suave)
            else:
                # limpar fundo se estiver vazio
                if item:
                    item.setBackground(QColor("white"))

    def atualizar_tabela_memoria(self):

        # Ordena os endereços para tabela ficar organizada
        enderecos = sorted(self.memoria.keys())

        self.tabela_memoria.setRowCount(len(enderecos))
        self.tabela_memoria.setColumnCount(2)
        self.tabela_memoria.setHorizontalHeaderLabels(["Endereço", "Valor"])
        #self.tabela_memoria.verticalHeader().setVisible(False)

        for row, endereco in enumerate(enderecos):
            valor = self.memoria[endereco]

            item_endereco = QTableWidgetItem(hex(endereco*4))
            item_valor = QTableWidgetItem(str(valor))

            # Centraliza os valores nas células
            item_endereco.setTextAlignment(Qt.AlignCenter)
            item_valor.setTextAlignment(Qt.AlignCenter)

            self.tabela_memoria.setItem(row, 0, item_endereco)
            self.tabela_memoria.setItem(row, 1, item_valor)

        self.tabela_memoria.resizeColumnsToContents()


    def ir_para_proximo(self):
        # for instr in self.instrucoes:
        #     instr.avancar()

        self.deslocar_tabela_para_esquerda()
        if(self.ciclo_atual < len(self.valsPorCiclo)-1):
            self.ciclo_atual += 1
            self.registradores = self.valsPorCiclo[self.ciclo_atual]
            self.memoria = self.memPorCiclo[self.ciclo_atual]
        #print(self.valsPorCiclo)
        self.atualizar_tabela_registradores()
        self.ajustar_scroll_se_linha_vazia()
        self.destacar_celulas_atual_verde()
        self.atualizar_tabela_memoria()
        
        
        #if(self.instrucoes[0].obter_estagio()=="WB"): #Deslocando para cima
        #    self.deslocar_tabela_para_cima()

    def finalizar_execucao(self):
        for i in range(len(self.valsPorCiclo) - self.ciclo_atual):
            self.ir_para_proximo()

if __name__ == "__main__":

    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    app.exec_()
