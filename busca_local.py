import random as random
from typing import List, Tuple, Dict
import random  # Necessário para operações aleatórias usadas nas buscas locais

from modelagem import Instance, verify_solution

# ======================================================================
# JOB EXCHANGE OPERATORS
# ======================================================================

def bl_job_exchange(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random single job-exchange local search.
    Randomly swaps two positions; accepts only improving and feasible moves
    until a stagnation limit.
    """
    if verbose:
        print("\nIniciando Job Exchange...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 500
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:
        iterations += 1

        i = random.randint(0, len(best_sol) - 1)
        j = random.randint(0, len(best_sol) - 1)
        if i == j:
            continue

        new_sol = best_sol[:]
        new_sol[i], new_sol[j] = new_sol[j], new_sol[i]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if not new_solution["feasible"]:
            continue

        new_makespan = new_solution["C_max"]
        if new_makespan < best_makespan:
            best_sol = new_sol
            best_solution = new_solution
            best_makespan = new_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Melhoria encontrada: novo makespan {new_makespan} trocando posições {i} e {j}")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1
            if stagnation_counter >= max_stagnation:
                break

    if verbose:
        print("Busca Local (Job Exchange aleatório) finalizada.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved


def double_job_exchange(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random double job-exchange: applies two independent random swaps per move.
    """
    if verbose:
        print("\nIniciando Double Job Exchange...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:
        iterations += 1

        n = len(best_sol)
        i_1 = random.randint(0, n - 1)
        j_1 = random.randint(0, n - 1)
        i_2 = random.randint(0, n - 1)
        j_2 = random.randint(0, n - 1)

        # garante índices distintos
        if len({i_1, j_1, i_2, j_2}) < 4:
            continue

        new_sol = best_sol[:]
        new_sol[i_1], new_sol[j_1] = new_sol[j_1], new_sol[i_1]
        new_sol[i_2], new_sol[j_2] = new_sol[j_2], new_sol[i_2]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if not new_solution["feasible"]:
            continue

        new_makespan = new_solution["C_max"]
        if new_makespan < best_makespan:
            best_sol = new_sol
            best_solution = new_solution
            best_makespan = new_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Melhoria: novo makespan {new_makespan} trocando "
                      f"{i_1}<->{j_1} e {i_2}<->{j_2}")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1
            if stagnation_counter >= max_stagnation:
                break

    if verbose:
        print("Double Job Exchange finalizado. Achou um ótimo local.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved


def deterministic_job_exchange(
    inst: Instance,
    res: Dict,
    first_improvement: bool = False,
    verbose: bool = False
) -> Tuple[List[int], Dict, bool]:
    """
    Deterministic job-exchange local search.
    Se first_improvement=False: best-improvement;
    Se first_improvement=True: first-improvement.
    Repete até atingir ótimo local nessa vizinhança.
    """
    if verbose:
        mode = "First" if first_improvement else "Best"
        print(f"\nIniciando Job Exchange Determinístico ({mode}-Improvement)...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]

    improved_any = False
    iterations = 0

    while True:
        iterations += 1
        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        n = len(best_sol)
        for i in range(n):
            for j in range(i + 1, n):
                new_sol = best_sol[:]
                new_sol[i], new_sol[j] = new_sol[j], new_sol[i]

                new_solution = verify_solution(inst, new_sol, verbose=False)
                if not new_solution["feasible"]:
                    continue

                new_makespan = new_solution["C_max"]
                if new_makespan < candidate_best_makespan:
                    candidate_best_makespan = new_makespan
                    candidate_best_sol = new_sol
                    candidate_best_solution = new_solution
                    if first_improvement:
                        break
            if first_improvement and candidate_best_sol is not None:
                break

        # nenhum vizinho factível melhor
        if candidate_best_sol is None or candidate_best_makespan >= best_makespan:
            break

        # aplica melhor (ou primeiro) movimento
        best_sol = candidate_best_sol
        best_solution = candidate_best_solution
        best_makespan = candidate_best_makespan
        improved_any = True

        if verbose:
            print(f"Melhoria: novo makespan {best_makespan} (iter {iterations})")
            print("Solução:", best_sol)

    if verbose:
        print("Busca Local (Job Exchange Determinístico) finalizada.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved_any

# ======================================================================
# JOB INSERTION OPERATORS
# ======================================================================

def insert_job_random(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random single-job insertion.
    """
    if verbose:
        print("\nIniciando Perturbação Insert Job Random...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]

    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while stagnation_counter < max_stagnation:
        iterations += 1

        # remove uma posição aleatória
        remove_index = random.randint(0, len(best_sol) - 1)
        job = best_sol[remove_index]
        new_sol = best_sol[:remove_index] + best_sol[remove_index + 1:]

        # insere em posição aleatória
        insert_index = random.randint(0, len(new_sol))
        new_sol = new_sol[:insert_index] + [job] + new_sol[insert_index:]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if new_solution["feasible"]:
            new_makespan = new_solution["C_max"]
            if new_makespan < best_makespan:
                best_sol = new_sol
                best_solution = new_solution
                best_makespan = new_makespan
                improved = True
                stagnation_counter = 0
                if verbose:
                    print(f"Perturbação: job {job} movido para posição {insert_index}")
                    print("Solução:", best_sol)
            else:
                stagnation_counter += 1
        else:
            stagnation_counter += 1

    if verbose:
        print("Perturbação Insert Job Random finalizada.")
        print("Número de tentativas:", iterations)

    return best_sol, best_solution, improved


def insert_job_best(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random job removal + best insertion position.
    """
    if verbose:
        print("\nIniciando Perturbação Insert Job Best...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]

    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while stagnation_counter < max_stagnation:
        iterations += 1

        remove_index = random.randint(0, len(best_sol) - 1)
        job = best_sol[remove_index]
        base_sol = best_sol[:remove_index] + best_sol[remove_index + 1:]

        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        for insert_index in range(len(base_sol) + 1):
            trial_sol = base_sol[:insert_index] + [job] + base_sol[insert_index:]
            trial_solution = verify_solution(inst, trial_sol, verbose=False)
            if not trial_solution["feasible"]:
                continue
            trial_makespan = trial_solution["C_max"]
            if trial_makespan < candidate_best_makespan:
                candidate_best_makespan = trial_makespan
                candidate_best_sol = trial_sol
                candidate_best_solution = trial_solution

        if candidate_best_sol is not None and candidate_best_makespan < best_makespan:
            best_sol = candidate_best_sol
            best_solution = candidate_best_solution
            best_makespan = candidate_best_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Perturbação: job {job} movido para melhor posição")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1

    if verbose:
        print("Perturbação Insert Job Best finalizada.")
        print("Número de tentativas:", iterations)

    return best_sol, best_solution, improved


def double_job_insert(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random double-job insertion: removes two jobs and reinserts
    them at random positions.
    """
    if verbose:
        print("\nIniciando Double Job Insert...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:
        iterations += 1

        n = len(best_sol)
        remove_index_1 = random.randint(0, n - 1)
        remove_index_2 = random.randint(0, n - 1)
        if remove_index_1 == remove_index_2:
            continue

        job_1 = best_sol[remove_index_1]
        job_2 = best_sol[remove_index_2]

        base_sol = [j for idx, j in enumerate(best_sol) if idx not in (remove_index_1, remove_index_2)]

        insert_index_1 = random.randint(0, len(base_sol))
        new_sol = base_sol[:insert_index_1] + [job_1] + base_sol[insert_index_1:]

        insert_index_2 = random.randint(0, len(new_sol))
        new_sol = new_sol[:insert_index_2] + [job_2] + new_sol[insert_index_2:]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if not new_solution["feasible"]:
            stagnation_counter += 1
            continue

        new_makespan = new_solution["C_max"]
        if new_makespan < best_makespan:
            best_sol = new_sol
            best_solution = new_solution
            best_makespan = new_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Melhoria: novo makespan {new_makespan} após double insert")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1
            if stagnation_counter >= max_stagnation:
                break

    if verbose:
        print("Double Job Insert finalizado.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved


def _deterministic_job_insertion(
    inst: Instance,
    res: Dict,
    first_improvement: bool = False,
    verbose: bool = False
    ) -> Tuple[List[int], Dict, bool]:
    """
    Núcleo determinístico de inserção de tarefas.
    Se first_improvement=False: best-improvement;
    Se first_improvement=True: first-improvement.
    Repete até atingir ótimo local nessa vizinhança.
    """
    if verbose:
        mode = "First" if first_improvement else "Best"
        print(f"\nIniciando Seleção Determinística de Tarefas ({mode}-Improvement)...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved_any = False
    iterations = 0

    while True:
        iterations += 1
        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        n = len(best_sol)
        for remove_index in range(n):
            job = best_sol[remove_index]
            base_sol = best_sol[:remove_index] + best_sol[remove_index + 1:]
            for insert_index in range(len(base_sol) + 1):
                trial_sol = base_sol[:insert_index] + [job] + base_sol[insert_index:]
                if trial_sol == best_sol:
                    continue
                trial_solution = verify_solution(inst, trial_sol, verbose=False)
                if not trial_solution["feasible"]:
                    continue
                trial_makespan = trial_solution["C_max"]
                if trial_makespan < candidate_best_makespan:
                    candidate_best_makespan = trial_makespan
                    candidate_best_sol = trial_sol
                    candidate_best_solution = trial_solution
                    if first_improvement:
                        break
            if first_improvement and candidate_best_sol is not None:
                break

        if candidate_best_sol is None or candidate_best_makespan >= best_makespan:
            break

        best_sol = candidate_best_sol
        best_solution = candidate_best_solution
        best_makespan = candidate_best_makespan
        improved_any = True

        if verbose:
            print(f"Melhoria: novo makespan {best_makespan} (iter {iterations})")
            print("Solução:", best_sol)

    if verbose:
        print("Seleção Determinística de Tarefas finalizada.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved_any

# ======================================================================
# BLOCK MOVES
# ======================================================================

def insert_block_random(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random block move: remove a random contiguous block and reinserts it
    at a random position.
    """
    if verbose:
        print("\nIniciando Perturbação Block Random...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]

    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while stagnation_counter < max_stagnation:
        iterations += 1

        n = len(best_sol)
        if n < 2:
            break
        max_block_size = max(2, int(0.4 * n))
        block_size = random.randint(2, max_block_size)

        if n < block_size:
            continue

        start_index = random.randint(0, n - block_size)
        block = best_sol[start_index:start_index + block_size]
        base_sol = best_sol[:start_index] + best_sol[start_index + block_size:]

        insert_index = random.randint(0, len(base_sol))
        new_sol = base_sol[:insert_index] + block + base_sol[insert_index:]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if not new_solution["feasible"]:
            stagnation_counter += 1
            continue

        new_makespan = new_solution["C_max"]
        if new_makespan < best_makespan:
            best_sol = new_sol
            best_solution = new_solution
            best_makespan = new_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Perturbação: bloco de tamanho {block_size} movido para posição {insert_index}")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1

    if verbose:
        print("Perturbação Block Random finalizada.")
        print("Número de tentativas:", iterations)

    return best_sol, best_solution, improved


def insert_block_best(inst: Instance, res: Dict, min_block_size: int = 2, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random block selection + best insertion position.
    """
    if verbose:
        print("\nIniciando Perturbação Insert Block Best...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]

    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while stagnation_counter < max_stagnation:
        iterations += 1

        n = len(best_sol)
        if n < min_block_size:
            break
        max_block_size = max(min_block_size, int(0.4 * n))
        block_size = random.randint(min_block_size, max_block_size)

        if n < block_size:
            continue

        start_index = random.randint(0, n - block_size)
        block = best_sol[start_index:start_index + block_size]
        base_sol = best_sol[:start_index] + best_sol[start_index + block_size:]

        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        for insert_index in range(len(base_sol) + 1):
            trial_sol = base_sol[:insert_index] + block + base_sol[insert_index:]
            trial_solution = verify_solution(inst, trial_sol, verbose=False)
            if not trial_solution["feasible"]:
                continue
            trial_makespan = trial_solution["C_max"]
            if trial_makespan < candidate_best_makespan:
                candidate_best_makespan = trial_makespan
                candidate_best_sol = trial_sol
                candidate_best_solution = trial_solution

        if candidate_best_sol is not None and candidate_best_makespan < best_makespan:
            best_sol = candidate_best_sol
            best_solution = candidate_best_solution
            best_makespan = candidate_best_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Perturbação: bloco de tamanho {block_size} movido para melhor posição")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1

    if verbose:
        print("Perturbação Insert Block Best finalizada.")
        print("Número de tentativas:", iterations)

    return best_sol, best_solution, improved


def _deterministic_block_insertion(
    inst: Instance,
    res: Dict,
    first_improvement: bool = False,
    verbose: bool = False
) -> Tuple[List[int], Dict, bool]:
    """
    Núcleo determinístico de movimentação de blocos.
    Se first_improvement=False: best-improvement;
    Se first_improvement=True: first-improvement.
    Repete até atingir ótimo local.
    """
    if verbose:
        mode = "First" if first_improvement else "Best"
        print(f"\nIniciando Seleção Determinística de Blocos ({mode}-Improvement)...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved_any = False
    iterations = 0

    while True:
        iterations += 1
        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        n = len(best_sol)
        if n < 2:
            break
        max_block_size = max(2, int(0.4 * n))

        for block_size in range(2, max_block_size + 1):
            for start_index in range(0, n - block_size + 1):
                block = best_sol[start_index:start_index + block_size]
                base_sol = best_sol[:start_index] + best_sol[start_index + block_size:]
                for insert_index in range(len(base_sol) + 1):
                    trial_sol = base_sol[:insert_index] + block + base_sol[insert_index:]
                    if trial_sol == best_sol:
                        continue
                    trial_solution = verify_solution(inst, trial_sol, verbose=False)
                    if not trial_solution["feasible"]:
                        continue
                    trial_makespan = trial_solution["C_max"]
                    if trial_makespan < candidate_best_makespan:
                        candidate_best_makespan = trial_makespan
                        candidate_best_sol = trial_sol
                        candidate_best_solution = trial_solution
                        if first_improvement:
                            break
                if first_improvement and candidate_best_sol is not None:
                    break
            if first_improvement and candidate_best_sol is not None:
                break

        if candidate_best_sol is None or candidate_best_makespan >= best_makespan:
            break

        best_sol = candidate_best_sol
        best_solution = candidate_best_solution
        best_makespan = candidate_best_makespan
        improved_any = True

        if verbose:
            print(f"Melhoria (bloco): novo makespan {best_makespan} (iter {iterations})")
            print("Solução:", best_sol)

    if verbose:
        print("Seleção Determinística de Blocos finalizada.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved_any

# ======================================================================
# 2-OPT OPERATORS
# ======================================================================

def two_opt_exchange(inst: Instance, res: Dict, verbose: bool = False) -> Tuple[List[int], Dict, bool]:
    """
    Random 2-opt exchange: randomly selects a segment [i,j] and reverses it.
    Accepts only improving and feasible moves until stagnation.
    """
    if verbose:
        print("\nIniciando 2-Opt Exchange Aleatório...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 500
    stagnation_counter = 0
    iterations = 0

    n = len(best_sol)
    if n < 2:
        return best_sol, best_solution, improved

    while stagnation_counter < max_stagnation:
        iterations += 1

        i = random.randint(0, n - 2)
        j = random.randint(i + 1, n - 1)

        new_sol = best_sol[:i] + best_sol[i:j+1][::-1] + best_sol[j+1:]

        new_solution = verify_solution(inst, new_sol, verbose=False)
        if not new_solution["feasible"]:
            stagnation_counter += 1
            continue

        new_makespan = new_solution["C_max"]
        if new_makespan < best_makespan:
            best_sol = new_sol
            best_solution = new_solution
            best_makespan = new_makespan
            improved = True
            stagnation_counter = 0
            if verbose:
                print(f"Melhoria 2-Opt aleatória: novo makespan {best_makespan}")
                print("Solução:", best_sol)
        else:
            stagnation_counter += 1

    if verbose:
        print("2-Opt Aleatório finalizado.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved


def deterministic_2_opt_exchange(
    inst: Instance,
    res: Dict,
    first_improvement: bool = False,
    verbose: bool = False
) -> Tuple[List[int], Dict, bool]:
    """
    Deterministic 2-opt local search.
    Se first_improvement=False: best-improvement;
    Se first_improvement=True: first-improvement.
    Repete até atingir ótimo local.
    """
    if verbose:
        mode = "First" if first_improvement else "Best"
        print(f"\nIniciando 2-Opt Exchange Determinístico ({mode}-Improvement)...")

    best_solution = res
    best_sol = res["sequence_normalized"][:]
    best_makespan = best_solution["C_max"]
    improved_any = False
    iterations = 0

    n = len(best_sol)
    if n < 2:
        return best_sol, best_solution, improved_any

    while True:
        iterations += 1
        candidate_best_makespan = best_makespan
        candidate_best_sol = None
        candidate_best_solution = None

        for i in range(n - 1):
            for j in range(i + 1, n):
                new_sol = best_sol[:i] + best_sol[i:j+1][::-1] + best_sol[j+1:]
                new_solution = verify_solution(inst, new_sol, verbose=False)
                if not new_solution["feasible"]:
                    continue
                new_makespan = new_solution["C_max"]
                if new_makespan < candidate_best_makespan:
                    candidate_best_makespan = new_makespan
                    candidate_best_sol = new_sol
                    candidate_best_solution = new_solution
                    if first_improvement:
                        break
            if first_improvement and candidate_best_sol is not None:
                break

        if candidate_best_sol is None or candidate_best_makespan >= best_makespan:
            break

        best_sol = candidate_best_sol
        best_solution = candidate_best_solution
        best_makespan = candidate_best_makespan
        improved_any = True

        if verbose:
            print(f"Melhoria 2-Opt: novo makespan {best_makespan} (iter {iterations})")
            print("Solução:", best_sol)

    if verbose:
        print("2-Opt Determinístico finalizado.")
        print("Número de iterações:", iterations)

    return best_sol, best_solution, improved_any
