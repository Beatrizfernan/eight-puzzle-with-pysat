import random
from pysat.solvers import Glucose3
from pysat.formula import CNF
from typing import List, Dict, Tuple, Optional

class SolucionadorSATEightPuzzle:
    def __init__(self):
        self.estado_meta = [[0, 1, 2], [3, 4, 5], [6, 7, 8]] 
        self.contador_variaveis = 1
        self.mapa_variaveis = {}  
        self.mapa_variaveis_reverso = {}  
        
    def criar_variavel(self, nome_variavel: str) -> int:
        """Cria uma variável proposicional e mapeia para um inteiro"""
        if nome_variavel not in self.mapa_variaveis:
            self.mapa_variaveis[nome_variavel] = self.contador_variaveis
            self.mapa_variaveis_reverso[self.contador_variaveis] = nome_variavel
            self.contador_variaveis += 1
        return self.mapa_variaveis[nome_variavel]
    
    def gerar_estado_inicial_aleatorio(self, num_movimentos: int = 20) -> List[List[int]]:
        """Gera um estado inicial válido a partir do estado meta com movimentos aleatórios"""
        estado = [linha[:] for linha in self.estado_meta] 
        
        
        pos_vazio = self.encontrar_pos_vazio(estado)
        
        for _ in range(num_movimentos):
            movimentos_validos = self.movimentos_validos(pos_vazio)
            if movimentos_validos:
                movimento = random.choice(movimentos_validos)
                pos_vazio = self.aplicar_movimento(estado, pos_vazio, movimento)
        
        return estado
    
    def encontrar_pos_vazio(self, estado: List[List[int]]) -> Tuple[int, int]:
        """Encontra a posição do espaço vazio (0)"""
        for i in range(3):
            for j in range(3):
                if estado[i][j] == 0:
                    return (i, j)
        return (0, 0)
    
    def movimentos_validos(self, pos_vazio: Tuple[int, int]) -> List[str]:
        """Retorna lista de movimentos válidos para o espaço vazio"""
        i, j = pos_vazio
        movimentos = []
        if i > 0: movimentos.append('C')  
        if i < 2: movimentos.append('B') 
        if j > 0: movimentos.append('E')  
        if j < 2: movimentos.append('D') 
        return movimentos
    
    def aplicar_movimento(self, estado: List[List[int]], pos_vazio: Tuple[int, int], mov: str) -> Tuple[int, int]:
        """Aplica um movimento e retorna a nova posição do espaço vazio"""
        i, j = pos_vazio
        
        if mov == 'C' and i > 0:
            estado[i][j], estado[i-1][j] = estado[i-1][j], estado[i][j]
            return (i-1, j)
        elif mov == 'B' and i < 2:
            estado[i][j], estado[i+1][j] = estado[i+1][j], estado[i][j]
            return (i+1, j)
        elif mov == 'E' and j > 0:
            estado[i][j], estado[i][j-1] = estado[i][j-1], estado[i][j]
            return (i, j-1)
        elif mov == 'D' and j < 2:
            estado[i][j], estado[i][j+1] = estado[i][j+1], estado[i][j]
            return (i, j+1)
        
        return pos_vazio
    
    def criar_variaveis_posicao(self, max_passos: int) -> None:
        """Cria variáveis para posições: passo_P_linha_col_numero"""
        for passo in range(max_passos + 1):
            for linha in range(1, 4):
                for coluna in range(1, 4):
                    for numero in range(9):
                        nome_var = f"{passo}_P_{linha}_{coluna}_{numero}"
                        self.criar_variavel(nome_var)
    
    def criar_variaveis_acao(self, max_passos: int) -> None:
        """Cria variáveis para ações: passo_A_direcao"""
        acoes = ['C', 'B', 'E', 'D', 'N'] 
        for passo in range(max_passos):
            for acao in acoes:
                nome_var = f"{passo}_A_{acao}"
                self.criar_variavel(nome_var)
    
    def adicionar_restricoes_posicao(self, cnf: CNF, max_passos: int) -> None:
        """Adiciona restrições para posições"""
        for passo in range(max_passos + 1):
            for linha in range(1, 4):
                for coluna in range(1, 4):
                    
                    clausula = []
                    for numero in range(9):
                        var = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_{numero}")
                        clausula.append(var)
                    cnf.append(clausula)
                    
                    
                    for i in range(9):
                        for j in range(i+1, 9):
                            var1 = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_{i}")
                            var2 = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_{j}")
                            cnf.append([-var1, -var2])
            
            
            for numero in range(9):
                clausula = []
                for linha in range(1, 4):
                    for coluna in range(1, 4):
                        var = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_{numero}")
                        clausula.append(var)
                cnf.append(clausula)
                
                
                posicoes = [(l, c) for l in range(1, 4) for c in range(1, 4)]
                for i in range(len(posicoes)):
                    for j in range(i+1, len(posicoes)):
                        l1, c1 = posicoes[i]
                        l2, c2 = posicoes[j]
                        var1 = self.criar_variavel(f"{passo}_P_{l1}_{c1}_{numero}")
                        var2 = self.criar_variavel(f"{passo}_P_{l2}_{c2}_{numero}")
                        cnf.append([-var1, -var2])
    
    def adicionar_restricoes_acao(self, cnf: CNF, max_passos: int) -> None:
        """Adiciona restrições de ação (exatamente uma ação por passo)"""
        acoes = ['C', 'B', 'E', 'D', 'N']
        for passo in range(max_passos):
          
            clausula = []
            for acao in acoes:
                var = self.criar_variavel(f"{passo}_A_{acao}")
                clausula.append(var)
            cnf.append(clausula)
            
           
            for i in range(len(acoes)):
                for j in range(i+1, len(acoes)):
                    var1 = self.criar_variavel(f"{passo}_A_{acoes[i]}")
                    var2 = self.criar_variavel(f"{passo}_A_{acoes[j]}")
                    cnf.append([-var1, -var2])
    
    def adicionar_restricoes_transicao(self, cnf: CNF, max_passos: int) -> None:
        """Adiciona restrições de transição de estado"""
        for passo in range(max_passos):
            self.adicionar_transicoes_movimento(cnf, passo, 'C', -1, 0)  
            self.adicionar_transicoes_movimento(cnf, passo, 'B', 1, 0)   
            self.adicionar_transicoes_movimento(cnf, passo, 'E', 0, -1)  
            self.adicionar_transicoes_movimento(cnf, passo, 'D', 0, 1)  
            self.adicionar_transicao_sem_acao(cnf, passo)              
    
    def adicionar_transicoes_movimento(self, cnf: CNF, passo: int, acao: str, dr: int, dc: int) -> None:
        """Adiciona transições para um movimento específico"""
        for linha in range(1, 4):
            for coluna in range(1, 4):
                nova_linha, nova_coluna = linha + dr, coluna + dc
                
               
                if 1 <= nova_linha <= 3 and 1 <= nova_coluna <= 3:
                    vazio_var = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_0")
                    acao_var = self.criar_variavel(f"{passo}_A_{acao}")
                    novo_vazio_var = self.criar_variavel(f"{passo+1}_P_{nova_linha}_{nova_coluna}_0")
                    
                    
                    
                    cnf.append([-vazio_var, -acao_var, novo_vazio_var])
                    
                  
                    for numero in range(1, 9):
                        antigo_num_var = self.criar_variavel(f"{passo}_P_{nova_linha}_{nova_coluna}_{numero}")
                        novo_num_var = self.criar_variavel(f"{passo+1}_P_{linha}_{coluna}_{numero}")
                        cnf.append([-vazio_var, -acao_var, -antigo_num_var, novo_num_var])
                
               
                for outra_linha in range(1, 4):
                    for outra_coluna in range(1, 4):
                        if (outra_linha, outra_coluna) != (linha, coluna) and (outra_linha, outra_coluna) != (nova_linha, nova_coluna):
                            for numero in range(9):
                                var_antigo = self.criar_variavel(f"{passo}_P_{outra_linha}_{outra_coluna}_{numero}")
                                var_novo = self.criar_variavel(f"{passo+1}_P_{outra_linha}_{outra_coluna}_{numero}")
                                acao_var = self.criar_variavel(f"{passo}_A_{acao}")
                                vazio_var = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_0")
                                cnf.append([-acao_var, -vazio_var, -var_antigo, var_novo])
    
    def adicionar_transicao_sem_acao(self, cnf: CNF, passo: int) -> None:
        """Adiciona transição para quando não há ação (estado permanece igual)"""
        acao_var = self.criar_variavel(f"{passo}_A_N")
        for linha in range(1, 4):
            for coluna in range(1, 4):
                for numero in range(9):
                    var_antigo = self.criar_variavel(f"{passo}_P_{linha}_{coluna}_{numero}")
                    var_novo = self.criar_variavel(f"{passo+1}_P_{linha}_{coluna}_{numero}")
                    cnf.append([-acao_var, -var_antigo, var_novo])
                    cnf.append([-acao_var, var_antigo, -var_novo])
    
    def adicionar_estado_inicial(self, cnf: CNF, estado_inicial: List[List[int]]) -> None:
        """Adiciona restrições do estado inicial"""
        for linha in range(3):
            for coluna in range(3):
                numero = estado_inicial[linha][coluna]
                var = self.criar_variavel(f"0_P_{linha+1}_{coluna+1}_{numero}")
                cnf.append([var])
    
    def adicionar_estado_meta(self, cnf: CNF, passo: int) -> None:
        """Adiciona restrições do estado meta no passo especificado"""
        for linha in range(3):
            for coluna in range(3):
                numero = self.estado_meta[linha][coluna]
                var = self.criar_variavel(f"{passo}_P_{linha+1}_{coluna+1}_{numero}")
                cnf.append([var])
    
    def resolver_puzzle(self, estado_inicial: List[List[int]], max_passos: int = 20) -> Optional[List[str]]:
        """Resolve o puzzle tentando diferentes números de passos"""
        print(f"Estado inicial:")
        self.imprimir_estado(estado_inicial)
        print(f"Estado meta:")
        self.imprimir_estado(self.estado_meta)
        print()
        
        for passos in range(1, max_passos + 1):
            print(f"Tentando resolver com {passos} passos...")
            
            
            self.contador_variaveis = 1
            self.mapa_variaveis = {}
            self.mapa_variaveis_reverso = {}
            
            cnf = CNF()
            
            
            self.criar_variaveis_posicao(passos)
            self.criar_variaveis_acao(passos)
            
           
            self.adicionar_restricoes_posicao(cnf, passos)
            self.adicionar_restricoes_acao(cnf, passos)
            self.adicionar_restricoes_transicao(cnf, passos)
            self.adicionar_estado_inicial(cnf, estado_inicial)
            self.adicionar_estado_meta(cnf, passos)
            
            
            solver = Glucose3()
            solver.append_formula(cnf)
            
            if solver.solve():
                print(f"Solução encontrada com {passos} passos!")
                modelo = solver.get_model()
                solver.delete()
                return self.extrair_solucao(modelo, passos)
            
            solver.delete()
        
        print("Nenhuma solução encontrada dentro do limite de passos.")
        return None
    
    def extrair_solucao(self, modelo: List[int], passos: int) -> List[str]:
        """Extrai a sequência de ações da solução"""
        acoes = []
        nomes_acoes = ['C', 'B', 'E', 'D', 'N']
        
        for passo in range(passos):
            for acao in nomes_acoes:
                nome_var = f"{passo}_A_{acao}"
                if nome_var in self.mapa_variaveis:
                    var_id = self.mapa_variaveis[nome_var]
                    if var_id in modelo:
                        if acao != 'N': 
                            acoes.append(acao)
                        break
        
        return acoes
    
    def imprimir_estado(self, estado: List[List[int]]) -> None:
        """Imprime o estado do puzzle"""
        for linha in estado:
            print(" ".join(str(x) for x in linha))
        print()
    
    def verificar_solucao(self, estado_inicial: List[List[int]], acoes: List[str]) -> bool:
        """Verifica se a sequência de ações resolve o puzzle"""
        estado = [linha[:] for linha in estado_inicial]
        pos_vazio = self.encontrar_pos_vazio(estado)
        
        print("Verificando solução:")
        print("Estado inicial:")
        self.imprimir_estado(estado)
        
        for i, acao in enumerate(acoes):
            if acao in self.movimentos_validos(pos_vazio):
                pos_vazio = self.aplicar_movimento(estado, pos_vazio, acao)
                print(f"Passo {i+1}: Movimento {acao}")
                self.imprimir_estado(estado)
            else:
                print(f"Movimento inválido: {acao}")
                return False
        
        return estado == self.estado_meta

if __name__ == "__main__":
    solucionador = SolucionadorSATEightPuzzle()
    
    
    estado_inicial = solucionador.gerar_estado_inicial_aleatorio(10)
    
    
    solucao = solucionador.resolver_puzzle(estado_inicial, max_passos=15)
    
    if solucao:
        print("Sequência de movimentos:")
        print(" -> ".join(solucao))
        print(f"Número total de movimentos: {len(solucao)}")
        
        
        if solucionador.verificar_solucao(estado_inicial, solucao):
            print("✓ Solução verificada com sucesso!")
        else:
            print("✗ Erro na solução!")
    else:
        print("Nenhuma solução encontrada.")
