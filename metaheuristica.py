import random
from typing import List, Dict, Callable, Optional

from modelagem import Instance, verify_solution
import busca_local as bl

# -------------------------------
# Wrappers de vizinhança (retornam dicionário de solução)
# Cada função das buscas locais retorna: (seq, sol_dict, improved).
# Mantemos apenas as vizinhanças completamente implementadas.
# -------------------------------
def _wrap_deterministic_2_opt_exchange(inst: Instance, sol_dict: Dict) -> Dict:
    return bl.deterministic_2_opt_exchange(inst, sol_dict)[1]

def _wrap_deterministic_job_exchange(inst: Instance, sol_dict: Dict) -> Dict:
    return bl.deterministic_job_exchange(inst, sol_dict)[1]

def _wrap_deterministic_job_insertion(inst: Instance, sol_dict: Dict) -> Dict:
    return bl._deterministic_job_insertion(inst, sol_dict)[1]

def _wrap_deterministic_block_insertion(inst: Instance, sol_dict: Dict) -> Dict:
    return bl._deterministic_block_insertion(inst, sol_dict)[1]


# def _wrap_double_job_insert(inst: Instance, sol_dict: Dict) -> Dict:
#     return bl.double_job_insert(inst, sol_dict)[1]

# Lista default de vizinhanças (ordem de exploração)
DEFAULT_NEIGHBORHOODS: List[Callable[[Instance, Dict], Dict]] = [
    _wrap_deterministic_2_opt_exchange,
    _wrap_deterministic_job_exchange,
    _wrap_deterministic_job_insertion,
    _wrap_deterministic_block_insertion,
]


def _shake_sequence(seq: List[int], strength: int = 1) -> List[int]:
    """Aplica perturbação simples na sequência (shaking).
    strength controla quantas operações aleatórias são aplicadas."""
    new_seq = seq[:]
    for _ in range(strength):
        op = random.randint(0, 2)
        n = len(new_seq)
        if n < 2:
            return new_seq
        if op == 0:  # swap
            i, j = random.sample(range(n), 2)
            new_seq[i], new_seq[j] = new_seq[j], new_seq[i]
        elif op == 1:  # move job
            i = random.randint(0, n - 1)
            job = new_seq.pop(i)
            j = random.randint(0, n - 1)
            new_seq.insert(j, job)
        else:  # move bloco pequeno
            if n >= 3:
                start = random.randint(0, n - 2)
                end = min(n, start + random.randint(2, min(4, n)))
                block = new_seq[start:end]
                rest = new_seq[:start] + new_seq[end:]
                pos = random.randint(0, len(rest))
                new_seq = rest[:pos] + block + rest[pos:]
    return new_seq


def VNS(inst: Instance, initial_sequence: List[int], max_iter: int = 500, max_stagnation: int = 100,
        neighborhoods: Optional[List[Callable[[Instance, Dict], Dict]]] = None,
        verbose: bool = False) -> Dict:
    """Variable Neighborhood Search (VNS) para o problema 1 | s_ij, prec(d_ij) | Cmax.

    Parâmetros:
      inst: instância do problema.
      initial_sequence: sequência inicial de jobs (0-based) factível.
      max_iter: limite total de iterações externas.
      max_stagnation: máximo de ciclos sem melhoria antes de parar.
      neighborhoods: lista de funções de vizinhança (wrapper) a aplicar.
      verbose: imprime detalhes se True.

    Retorna:
      Dicionário de solução no formato de verify_solution (inclui C_max, sequência normalizada etc.).
    """
    if neighborhoods is None:
        neighborhoods = DEFAULT_NEIGHBORHOODS

    current_sol = initial_sequence

    best_sol = current_sol
    best_C = best_sol["C_max"]

    no_improve = 0
    iteration = 0

    if verbose:
        print(f"[VNS] Início: C_max={best_C}")

    while iteration < max_iter and no_improve < max_stagnation:
        iteration += 1
        improved_cycle = False


        # Explora cada vizinhança na ordem

        # neighborhoods = random.shuffle(neighborhoods)
        neighborhoods = random.sample(neighborhoods, k=len(neighborhoods))
        for neigh_index, neigh_func in enumerate(neighborhoods):
            print(f"[VNS] Iter {iteration} Tentando vizinhança {neigh_index}...")
            # Shaking: intensidade pode crescer com o índice da vizinhança
            shaken_seq = _shake_sequence(best_sol["sequence_normalized"], strength = 3)
            # shaken_seq = _shake_sequence(best_sol["sequence_normalized"], strength=neigh_index + 1)
            
            while True:
                shaken_eval = verify_solution(inst, shaken_seq, verbose=False)
                if not shaken_eval["feasible"]:
                    shaken_seq = _shake_sequence(best_sol["sequence_normalized"], strength = 3)
                else:
                    break

            # Local search na vizinhança
            new_sol = neigh_func(inst, shaken_eval)
            new_C = new_sol["C_max"]

            if verbose:
                print(f"[VNS] Iter {iteration} Viz {neigh_index} => C_max={new_C}")

            if new_C < best_C:
                best_sol = new_sol
                best_C = new_C
                improved_cycle = True
                no_improve = 0
                if verbose:
                    print(f"[VNS] Melhoria: novo C_max={best_C} (viz {neigh_index})")
                break  # Reinicia ciclo de vizinhanças após melhoria

        if not improved_cycle:
            no_improve += 1
            if verbose:
                print(f"[VNS] Nenhuma melhoria no ciclo {iteration}. Sem melhoria consecutiva={no_improve}")

    if verbose:
        print(f"[VNS] Fim após {iteration} iterações. Melhor C_max={best_C}")

    return best_sol
