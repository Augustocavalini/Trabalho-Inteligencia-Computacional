import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx

# ---------------------------
# 1) Problema de Representação
# ---------------------------
@dataclass
class Instance:
    """
    Instância 1 | s_ij, prec(d_ij) | C_max
    - n: número de jobs reais (1..n). Também usamos 0 (início) e n+1 (fim) como dummies.
    - p: tempos de processamento, indexados 0..n+1 (p[0]=p[n+1]=0).
    - s: matriz (n+2)x(n+2) de setups s[i][j], incluindo 0 e n+1 (convenção: s[i][i]=0).
    - d: matriz de atrasos de precedência (nxn), -1 se não houver precedência.
    """
    n: int
    p: List[float]
    s: List[List[float]]
    d: List[List[float]]  # Matriz de atrasos de precedência (nxn)

    def check_basic_shapes(self) -> None:
        # assert len(self.p) == self.n, "p deve ter índices 0..n+1 (com p[0]=p[n+1]=0)."
        # assert len(self.s) == self.n + 2 and all(len(row) == self.n + 2 for row in self.s), \
        #     "s deve ser (n+2) x (n+2), incluindo 0 e n+1."
        # assert len(self.d) == self.n + 2 and all(len(row) == self.n + 2 for row in self.d), \
        #     "d deve ser (n+2) x (n+2), incluindo 0 e n+1."
        # assert self.p[0] == 0 and self.p[self.n+1] == 0, "Use p[0]=p[n+1]=0 para os dummies."
        # for i in range(self.n + 2):
        #     assert self.s[i][i] == 0, "Convencione s[i][i]=0."
        #     assert all(self.d[i][j] == -1 or self.d[i][j] >= 0 for j in range(self.n + 2)), \
        #         "Valores de atraso devem ser >=0 ou -1."
        assert len(self.p) == self.n, "p deve ter índices 0..n-1."
        assert len(self.s) == self.n and all(len(row) == self.n for row in self.s), \
            "s deve ser n x n."
        assert len(self.d) == self.n and all(len(row) == self.n for row in self.d), \
            "d deve ser n x n."
        for i in range(self.n + 2):
            assert self.s[i][i] == 0, "Convencione s[i][i]=0."
            assert all(self.d[i][j] == -1 or self.d[i][j] >= 0 for j in range(self.n)), \
                "Valores de atraso devem ser >=0 ou -1."

# ---------------------------
# 2) Carregar instância do arquivo .txt
# ---------------------------
def load_instance_from_txt(file_path: str) -> Instance:
    """
    Carrega uma instância do problema a partir de um arquivo .txt.
    O arquivo deve estar no formato fornecido (R, Pj, A, Sij).
    """
    with open(file_path, 'r') as f:
        # Lendo o número de jobs (R) e removendo o prefixo "R="
        R_line = f.readline().strip()
        R = int(R_line.split('=')[1])
        
        # Lendo o vetor de tempos de processamento Pj (Pi=...)
        Pj_line = f.readline().strip()
        Pj = list(map(int, Pj_line.split('=')[1].strip('()').split(',')))
        
        # Lendo a matriz de precedências atrasadas A
        dij = [[-1 for _ in range(R)] for _ in range(R)]  # Matriz de atrasos (inicializa com -1)
        
        line = f.readline().strip()
        if line != 'A=':
            raise ValueError("Formato inválido: Esperado 'A=' após Pj.")
        while True:
            line = f.readline().strip()
            
            if line == 'Sij=':  # Fim da seção de A
                break
            i, j, d_ij = map(int, line.split(','))
            dij[i - 1][j - 1] = d_ij  # Preenche a matriz com o atraso de precedência
        
        # Lendo a matriz de setups Sij
        Sij = []
        for i in range(R):
            line = list(map(int, f.readline().strip().split(',')))
            Sij.append(line)
    
    # Criando a instância no formato correto
    inst = Instance(
        n=R,      # número de jobs reais
        p=Pj,     # p[0] e p[n+1] são 0
        s=Sij,    # s[i][j] com setup entre todos os jobs
        d=dij   # Atrasos com -1 onde não há precedência
    )
    
    return inst

# ---------------------------
# 3) Verificar e calcular a solução
# ---------------------------
def verify_solution(inst: Instance, seq: List[int]) -> Dict:
    """
    Verifica se 'seq' é uma solução válida e calcula:
      - factível? (boolean)
      - violações (lista textual)
      - C_max (makespan)
      - cronograma: b[i], c[i] (inícios e términos)
    """
    # print("\n=== Iniciando verificação da solução ===")
    # print(f"Sequência original: {seq}")
    
    n = inst.n
    # print(f"Número de jobs (n): {n}")

    # Ajusta seq se for no formato 1..n
    if all(1 <= job <= n for job in seq):
        seq_norm = [job - 1 for job in seq]  # Ajusta para 0-based
        # print(f"Sequência normalizada (0-based): {seq_norm}")
    else:
        seq_norm = seq[:]
        # print("Sequência já estava normalizada")

    # Verifica precedências (ordem)
    pos = {job: idx for idx, job in enumerate(seq_norm)}
    # print("\n=== Verificando precedências (ordem) ===")
    # print(f"Posições dos jobs: {pos}")

    order_viol = []
    for i in range(n):
        for j in range(n):
            if inst.d[i][j] != -1:  # Se há precedência
                # print(f"Checando precedência {i}->{j} (atraso={inst.d[i][j]})")
                # print(f"  Posição de {i}: {pos[i]}")
                # print(f"  Posição de {j}: {pos[j]}")
                if pos[i] > pos[j]:
                    # print(f"  VIOLAÇÃO: {i} deveria vir antes de {j}")
                    order_viol.append((i, j))

    if len(order_viol) > 0:
        # print(f"\nViolações de ordem encontradas: {order_viol}")
        return {
            "feasible": False, 
            "violations": [f"Ordem de precedência violada: {order_viol}."],
            "C_max": None, 
            "b": None, 
            "c": None,
            "sequence_normalized": seq_norm
        }

    # Calcula cronograma e verifica delays
    # print("\n=== Calculando cronograma e verificando delays ===")
    b = [0.0] * n  # Inícios
    c = [0.0] * n  # Términos
    delay_viol = []  # Violações de delay de precedência

    # print(f"\nProcessando job {seq_norm[0]} na primeira posição")
    # print(f"  Início (b[{seq_norm[0]}]) = 0.0")
    # print(f"  Término (c[{seq_norm[0]}]) = {inst.p[seq_norm[0]]}")
    c[seq_norm[0]] = inst.p[seq_norm[0]]

    # Para cada job j na sequência
    for r in range(1, len(seq_norm)):
        j = seq_norm[r]    # job atual
        # print(f"\nProcessando job {j}")
        
        # Encontra o início mais tardio considerando todas as precedências
        latest_start = 0.0
        for i in range(n):
            if inst.d[i][j] != -1:  # Se i precede j
                required_start = c[i] + inst.d[i][j]
                if required_start > latest_start:
                    latest_start = required_start
                # print(f"  Checando delay {i}->{j}:")
                # print(f"    Término de {i}: {c[i]}")
                # print(f"    Delay requerido: {inst.d[i][j]}")
                # print(f"    Início mínimo: {required_start}")

        # Considera também o setup do job imediatamente anterior
        i = seq_norm[r-1]  # job anterior na sequência
        setup_start = c[i] + inst.s[i][j]
        # print(f"  Setup após job {i}: {c[i]} + {inst.s[i][j]} = {setup_start}")
        
        # O início real deve respeitar tanto precedências quanto setup
        b[j] = max(latest_start, setup_start)
        c[j] = b[j] + inst.p[j]
        # print(f"  Início final (b[{j}]) = {b[j]}")
        # print(f"  Término final (c[{j}]) = {c[j]}")
        
        # Verifica se alguma precedência foi violada
        for i in range(n):
            if inst.d[i][j] != -1:  # Se i precede j
                required_start = c[i] + inst.d[i][j]
                if b[j] < required_start:
                    violation = (i, j, required_start - b[j])
                    # print(f"  VIOLAÇÃO: Delay {i}->{j} insuficiente por {violation[2]:.1f} unidades")
                    delay_viol.append(violation)

    if len(delay_viol) > 0:
        # print(f"\nViolações de delay encontradas: {delay_viol}")
        return {
            "feasible": False,
            "violations": [f"Delays de precedência violados: {delay_viol}"],
            "C_max": None,
            "b": b,
            "c": c,
            "sequence_normalized": seq_norm
        }

    C_max = c[seq_norm[-1]]
    # print(f"\nMakespan (C_max) = {C_max}")

    return {
        "feasible": True,
        "violations": [],
        "C_max": C_max,
        "b": b,
        "c": c,
        "sequence_normalized": seq_norm
    }
