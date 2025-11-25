import random as random
from typing import List, Tuple, Dict
import random  # Necessário para operações aleatórias usadas nas buscas locais

from Modelagem import Instance, verify_solution

# def buscalocal1(inst: Instance, res: List[int]) -> Tuple[List[int], Dict]:
    
#     print("\nIniciando Busca Local...")
#     improved = False
#     best_solution = res
#     best_sol = res["sequence_normalized"]
#     best_makespan = best_solution["C_max"]
    
#     iterations = 0
#     stagnation_counter = 0
#     max_stagnation = 1000  # Define um número máximo de iterações para evitar loops infinitos

#     while stagnation_counter < max_stagnation:
#         for i in range(len(best_sol)):
#             for j in range(len(best_sol)):
#                 if i == j:
#                     continue
#                 # Troca as tarefas nas posições i e j
#                 new_sol = best_sol[:]
#                 new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
                
#                 new_solution = verify_solution(inst, new_sol, verbose=False)
                
#                 if not new_solution["feasible"]:
#                     continue
                
#                 new_makespan = new_solution["C_max"]
                
#                 if new_makespan < best_makespan:
#                     best_sol = new_sol
#                     best_solution = new_solution
#                     improved = True
#                     stagnation_counter = 0
#                     print(f"Melhoria encontrada: novo makespan {new_makespan} trocando posições {i} e {j}")
                
#                 else:
#                     stagnation_counter += 1
                    
#         iterations += 1
                
#     print("Busca Local finalizada.")
#     print("Número de iterações:", iterations)  # Pode ser implementado um contador se desejado
    
#     return  best_sol, best_solution, improved


def bl_job_exchange(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    
    if verbose:
        print("\nIniciando Job Exchange...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    start_sol = best_sol[:]
    
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 500  # Define um número máximo de iterações para evitar loops infinitos
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:

        i = random.randint(0, len(best_sol) - 1)
        j = random.randint(0, len(best_sol) - 1)
        
        new_sol = best_sol[:]
        new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
        
        new_solution = verify_solution(inst, new_sol, verbose=False)
        if new_solution["feasible"]:
            new_makespan = new_solution["C_max"]
            
            if new_makespan < best_makespan:
                best_sol = new_sol
                best_solution = new_solution
                best_makespan = new_makespan
                improved = True
                if verbose:
                    print(f"Melhoria encontrada: novo makespan {new_makespan} trocando posições {i} e {j}, tentativa {stagnation_counter}")
                    print("Solução:", best_sol)
                stagnation_counter = 0

            
            else:
                stagnation_counter += 1
        iterations += 1
                
    
    if verbose:
        print("Busca Local finalizada. Achou um ótimo local.")
        print("Número de iterações:", iterations)
    
    return  best_sol, best_solution, improved


def insert_job_random(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    
    if verbose:
        print("\nIniciando Perturbação Insert Job Random...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    
    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    iterations = 0

    while stagnation_counter < max_stagnation:
        
        # Seleciona uma posição aleatória para remover a tarefa
        remove_index = random.randint(0, len(best_sol) - 1)
        job = best_sol[remove_index]
        
        # Remove a tarefa da sequência
        new_sol = best_sol[:remove_index] + best_sol[remove_index + 1:]
        
        # Seleciona uma nova posição para inserir a tarefa
        insert_index = random.randint(0, len(new_sol))
        
        # Insere a tarefa na nova posição
        new_sol = new_sol[:insert_index] + [job] + new_sol[insert_index:]
        
        new_solution = verify_solution(inst, new_sol, verbose=False)
        
        if new_solution["feasible"] and new_solution["C_max"] < best_solution["C_max"]:
            
            best_sol = new_sol
            best_solution = new_solution
            improved = True
            if verbose:
                print(f"Perturbação realizada: job {job} movido para posição {insert_index}, tentativa {stagnation_counter}")
                print("Solução:", best_sol)
            stagnation_counter = 0
        else:
            stagnation_counter += 1
    
    if verbose:
        print("Perturbação Insert Job Random finalizada.")
        print("Número de tentativas:", iterations)
    
    return best_sol, best_solution, improved
    

def insert_job_best(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    
    if verbose:
        print("\nIniciando Perturbação Insert Job Best...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    
    improved = False
    max_stagnation = 1000
    stagnation_counter = 0

    iterations = 0
    
    best_insertion_sol = None
    best_insertion_makespan = float('inf')

    while stagnation_counter < max_stagnation:

        iterations += 1
        
        # Seleciona uma posição aleatória para remover a tarefa
        remove_index = random.randint(0, len(best_sol) - 1)
        job = best_sol[remove_index]
        
        # Remove a tarefa da sequência
        new_sol = best_sol[:remove_index] + best_sol[remove_index + 1:]
        
        # Tenta inserir a tarefa em todas as posições possíveis
        for insert_index in range(len(new_sol) + 1):
            trial_sol = new_sol[:insert_index] + [job] + new_sol[insert_index:]
            trial_solution = verify_solution(inst, trial_sol, verbose=False)
            
            if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                best_insertion_makespan = trial_solution["C_max"]
                best_insertion_sol = trial_sol
                best_insertion_solution = trial_solution
        
        if best_insertion_sol is not None and best_insertion_makespan < best_solution["C_max"]:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            if verbose:
                print(f"Perturbação realizada: job {job} movido para melhor posição, tentativa {stagnation_counter}")
                print("Solução:", best_sol)
            stagnation_counter = 0
            improved = True
        else:
            stagnation_counter += 1
    if verbose:
        print("Perturbação Insert Job Best finalizada.")
        print("Número de tentativas:", iterations)
    
    return best_sol, best_solution, improved


def insert_block_random(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
        
    if verbose:
        print("\nIniciando Perturbação Block Throw...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    
    improved = False
    max_stagnation = 1000
    stagnation_counter = 0

    iterations = 0

    while stagnation_counter < max_stagnation:
        iterations += 1
        
        # Seleciona o tamanho do bloco (entre 2 e 4 tarefas)
        block_size = random.randint(2, int(0.4*len(best_sol)))
        
        if len(best_sol) < block_size:
            continue
        
        # Seleciona a posição inicial do bloco
        start_index = random.randint(0, len(best_sol) - block_size)
        block = best_sol[start_index:start_index + block_size]
        
        # Remove o bloco da sequência
        new_sol = best_sol[:start_index] + best_sol[start_index + block_size:]
        
        # Seleciona uma nova posição para inserir o bloco
        insert_index = random.randint(0, len(new_sol))
        
        # Insere o bloco na nova posição
        new_sol = new_sol[:insert_index] + block + new_sol[insert_index:]
        
        new_solution = verify_solution(inst, new_sol, verbose=False)
        
        if new_solution["feasible"] and new_solution["C_max"] < best_solution["C_max"]:
            
            best_sol = new_sol
            best_solution = new_solution
            if verbose:
                print(f"Perturbação realizada: bloco de tamanho {block_size} movido para posição {insert_index}, tentativa {stagnation_counter}")
                print("Solução:", best_sol)
            stagnation_counter = 0
            improved = True
        else:
            stagnation_counter += 1
    
    if verbose:
        print("Perturbação Block Throw finalizada.")
        print("Número de tentativas:", iterations)
    
    return best_sol, best_solution, improved


def insert_block_best(inst: Instance, res: List[int], min_block_size: int = 2, verbose=False) -> Tuple[List[int], Dict]:
    
    if verbose:
        print("\nIniciando Perturbação Insert Block Best...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    
    improved = False
    max_stagnation = 1000
    stagnation_counter = 0
    
    best_insertion_sol = None
    best_insertion_makespan = float('inf')

    interation = 0

    while stagnation_counter < max_stagnation:
        interation += 1
        
        # Seleciona o tamanho do bloco
        block_size = random.randint(min_block_size, int(0.4 * len(best_sol)))
        
        if len(best_sol) < block_size:
            continue
        
        # Seleciona a posição inicial do bloco
        start_index = random.randint(0, len(best_sol) - block_size)
        block = best_sol[start_index:start_index + block_size]
        
        # Remove o bloco da sequência
        new_sol = best_sol[:start_index] + best_sol[start_index + block_size:]
        
        # Tenta inserir o bloco em todas as posições possíveis
        for insert_index in range(len(new_sol) + 1):
            trial_sol = new_sol[:insert_index] + block + new_sol[insert_index:]
            trial_solution = verify_solution(inst, trial_sol, verbose=False)
            
            if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                best_insertion_makespan = trial_solution["C_max"]
                best_insertion_sol = trial_sol
                best_insertion_solution = trial_solution
        
        if best_insertion_sol is not None and best_insertion_makespan < best_solution["C_max"]:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            if verbose:
                print(f"Perturbação realizada: bloco de tamanho {block_size} movido para melhor posição, tentativa {stagnation_counter}")
                print("Solução:", best_sol)
            stagnation_counter = 0
            improved = True
        else:
            stagnation_counter += 1
            
    if verbose:
        print("Perturbação Insert Block Best finalizada.")
        print("Número de tentativas:", interation)  
    
    return best_sol, best_solution, improved
    
def double_job_exchange(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    if verbose:
        print("\nIniciando Double Job Exchange...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]    
    
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 1000  # Define um número máximo de iterações para evitar loops infinitos
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:

        i_1 = random.randint(0, len(best_sol) - 1)
        i_2 = random.randint(0, len(best_sol) - 1)
        j_1 = random.randint(0, len(best_sol) - 1)
        j_2 = random.randint(0, len(best_sol) - 1)
        
        if i_1 == j_1 or i_1 == j_2 or i_2 == j_1 or i_2 == j_2:
            continue
        
        new_sol = best_sol[:]
        new_sol[i_1], new_sol[j_1] = new_sol[j_1], new_sol[i_1]
        new_sol[i_2], new_sol[j_2] = new_sol[j_2], new_sol[i_2]
        
        new_solution = verify_solution(inst, new_sol, verbose=False)
        if new_solution["feasible"]:
            new_makespan = new_solution["C_max"]
            
            if new_makespan < best_makespan:
                best_sol = new_sol
                best_solution = new_solution
                best_makespan = new_makespan
                improved = True
                if verbose:
                    print(f"Melhoria encontrada: novo makespan {new_makespan} trocando posições {i_1} e {j_1}, {i_2} e {j_2}, tentativa {stagnation_counter}")
                    print("Solução:", best_sol)
                stagnation_counter = 0

            
            else:
                stagnation_counter += 1
        iterations += 1
                
    
    if verbose:
        print("Busca Local finalizada. Achou um ótimo local.")
        print("Número de iterações:", iterations)
    
    return  best_sol, best_solution, improved

def double_job_insert(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    if verbose:
        print("\nIniciando Double Job Insert...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]    
    
    best_makespan = best_solution["C_max"]
    improved = False

    max_stagnation = 1000  # Define um número máximo de iterações para evitar loops infinitos
    stagnation_counter = 0
    iterations = 0

    while iterations < max_stagnation:

        remove_index_1 = random.randint(0, len(best_sol) - 1)
        remove_index_2 = random.randint(0, len(best_sol) - 1)
        
        if remove_index_1 == remove_index_2:
            continue
        
        job_1 = best_sol[remove_index_1]
        job_2 = best_sol[remove_index_2]
        
        new_sol = [j for idx, j in enumerate(best_sol) if idx not in (remove_index_1, remove_index_2)]
        
        insert_index_1 = random.randint(0, len(new_sol))
        new_sol = new_sol[:insert_index_1] + [job_1] + new_sol[insert_index_1:]
        
        insert_index_2 = random.randint(0, len(new_sol))
        new_sol = new_sol[:insert_index_2] + [job_2] + new_sol[insert_index_2:]
        
        new_solution = verify_solution(inst, new_sol, verbose=False)
        if new_solution["feasible"]:
            new_makespan = new_solution["C_max"]
            
            if new_makespan < best_makespan:
                best_sol = new_sol
                best_solution = new_solution
                best_makespan = new_makespan
                improved = True
                if verbose:
                    print(f"Melhoria encontrada: novo makespan {new_makespan} movendo jobs para posições {insert_index_1} e {insert_index_2}, tentativa {stagnation_counter}")
                    print("Solução:", best_sol)
                stagnation_counter = 0

            
            else:
                stagnation_counter += 1
        iterations += 1
                
    
    if verbose:
        print("Busca Local finalizada. Achou um ótimo local.")
        print("Número de iterações:", iterations)
    
    return  best_sol, best_solution, improved



def deterministic_job_selection(inst: Instance, res: List[int], verbose=False) -> List[int]:
   
    if verbose:
        print("\nIniciando Seleção Determinística de Tarefas...")
    best_solution = res
    best_sol = res["sequence_normalized"]
    best_sol_makespan = res["C_max"]
    
    improved = False
    
    best_insertion_sol = None
    best_insertion_makespan = float('inf')

    interation = 0

    while best_sol_makespan < best_insertion_makespan:
        interation += 1
        
        for job in best_sol:
            # Remove a tarefa da sequência
            new_sol = [j for j in best_sol if j != job]
            
            # Tenta inserir a tarefa em todas as posições possíveis
            for insert_index in range(len(new_sol) + 1):
                trial_sol = new_sol[:insert_index] + [job] + new_sol[insert_index:]
                trial_solution = verify_solution(inst, trial_sol, verbose=False)
                
                if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                    best_insertion_makespan = trial_solution["C_max"]
                    best_insertion_sol = trial_sol
                    best_insertion_solution = trial_solution            
            
        if best_insertion_sol is not None and best_insertion_makespan < best_sol_makespan:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            best_sol_makespan = best_insertion_makespan
            if verbose:
                print(f"Perturbação realizada: job movido para melhor posição, tentativa {interation}")
                print("Solução:", best_sol)
            improved = True
            
    if verbose:
        print("Perturbação Insert Block Best finalizada.")
        print("Número de tentativas:", interation)
    
    return best_sol, best_solution, improved   

def deterministic_block_selection(inst: Instance, res: List[int], verbose=False) -> List[int]:
    
     if verbose:
         print("\nIniciando Seleção Determinística de Blocos...")
     best_solution = res
     best_sol = res["sequence_normalized"]
     best_sol_makespan = res["C_max"]
     
     improved = False
     
     best_insertion_sol = None
     best_insertion_makespan = float('inf')
    
     interation = 0
    
     while best_sol_makespan < best_insertion_makespan:
          interation += 1
          
          for block_size in range(2, int(0.4 * len(best_sol)) + 1):
                for start_index in range(len(best_sol) - block_size + 1):
                 block = best_sol[start_index:start_index + block_size]
                 
                 # Remove o bloco da sequência
                 new_sol = best_sol[:start_index] + best_sol[start_index + block_size:]
                 
                 # Tenta inserir o bloco em todas as posições possíveis
                 for insert_index in range(len(new_sol) + 1):
                      trial_sol = new_sol[:insert_index] + block + new_sol[insert_index:]
                      trial_solution = verify_solution(inst, trial_sol, verbose=False)
                      
                      if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                            best_insertion_makespan = trial_solution["C_max"]
                            best_insertion_sol = trial_sol
                            best_insertion_solution = trial_solution            
                
          if best_insertion_sol is not None and best_insertion_makespan < best_sol_makespan:
                best_sol = best_insertion_sol
                best_solution = best_insertion_solution
                best_sol_makespan = best_insertion_makespan
                if verbose:
                    print(f"Perturbação realizada: bloco movido para melhor posição, tentativa {interation}")
                    print("Solução:", best_sol)
                improved = True
                
     if verbose:
         print("Perturbação Insert Block Best finalizada.")
         print("Número de tentativas:", interation)
     
     return best_sol, best_solution, improved

def deterministic_first_job_selection(inst: Instance, res: List[int], verbose=False) -> List[int]:
   
    if verbose:
        print("\nIniciando Seleção Determinística de Tarefas (First Improvement)...")
    best_solution = res
    best_sol = res["sequence_normalized"]
    best_sol_makespan = res["C_max"]
    
    improved = False
    
    best_insertion_sol = None
    best_insertion_makespan = float('inf')

    iterations = 0

    while best_sol_makespan < best_insertion_makespan:
        iterations += 1
        
        for job in best_sol:
            # Remove a tarefa da sequência
            new_sol = [j for j in best_sol if j != job]
            
            # Tenta inserir a tarefa em todas as posições possíveis
            for insert_index in range(len(new_sol) + 1):
                trial_sol = new_sol[:insert_index] + [job] + new_sol[insert_index:]
                trial_solution = verify_solution(inst, trial_sol, verbose=False)
                
                if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                    best_insertion_makespan = trial_solution["C_max"]
                    best_insertion_sol = trial_sol
                    best_insertion_solution = trial_solution            
                    break  # Sai do loop ao encontrar a primeira melhoria
            
            if best_insertion_sol is not None:
                break  # Sai do loop externo se uma melhoria foi encontrada
        
        if best_insertion_sol is not None and best_insertion_makespan < best_sol_makespan:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            best_sol_makespan = best_insertion_makespan
            if verbose:
                print(f"Perturbação realizada: job movido para melhor posição, tentativa {iterations}")
                print("Solução:", best_sol)
            improved = True
    
    if verbose:
        print("Perturbação Insert Block Best finalizada.")
        print("Número de tentativas:", iterations)
    
    return best_sol, best_solution, improved   

def deterministic_first_block_selection(inst: Instance, res: List[int], verbose=False) -> List[int]:
    
     if verbose:
         print("\nIniciando Seleção Determinística de Blocos (First Improvement)...")
     best_solution = res
     best_sol = res["sequence_normalized"]
     best_sol_makespan = res["C_max"]
     
     improved = False
     
     best_insertion_sol = None
     best_insertion_makespan = float('inf')
    
     iterations = 0
    
     while best_sol_makespan < best_insertion_makespan:
          iterations += 1
          
          for block_size in range(2, int(0.4 * len(best_sol)) + 1):
                for start_index in range(len(best_sol) - block_size + 1):
                 block = best_sol[start_index:start_index + block_size]
                 
                 # Remove o bloco da sequência
                 new_sol = best_sol[:start_index] + best_sol[start_index + block_size:]
                 
                 # Tenta inserir o bloco em todas as posições possíveis
                 for insert_index in range(len(new_sol) + 1):
                      trial_sol = new_sol[:insert_index] + block + new_sol[insert_index:]
                      trial_solution = verify_solution(inst, trial_sol, verbose=False)
                      
                      if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                            best_insertion_makespan = trial_solution["C_max"]
                            best_insertion_sol = trial_sol
                            best_insertion_solution = trial_solution            
                            break  # Sai do loop ao encontrar a primeira melhoria
                
                 if best_insertion_sol is not None:
                     break  # Sai do loop externo se uma melhoria foi encontrada
          
          if best_insertion_sol is not None and best_insertion_makespan < best_sol_makespan:
                best_sol = best_insertion_sol
                best_solution = best_insertion_solution
                best_sol_makespan = best_insertion_makespan
                if verbose:
                    print(f"Perturbação realizada: bloco movido para melhor posição, tentativa {iterations}")
                    print("Solução:", best_sol)
                improved = True
                
     if verbose:
         print("Perturbação Insert Block Best finalizada.")
         print("Número de tentativas:", iterations)
     
     return best_sol, best_solution, improved

def deterministic_2_opt_exchange(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict, bool]:
    if verbose:
        print("\nIniciando 2-Opt Exchange...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]
    best_sol_makespan = best_solution["C_max"]
    improved = False
    iterations = 0

    # Loop até não haver melhoria; se nenhuma vizinhança factível for encontrada, sair para evitar loop infinito.
    while True:
        iterations += 1
        best_insertion_sol = None
        best_insertion_makespan = float('inf')

        for i in range(len(best_sol) - 1):
            for j in range(i + 1, len(best_sol)):
                trial_sol = best_sol[:i] + best_sol[i:j+1][::-1] + best_sol[j+1:]
                trial_solution = verify_solution(inst, trial_sol, verbose=False)

                if trial_solution["feasible"] and trial_solution["C_max"] < best_insertion_makespan:
                    best_insertion_makespan = trial_solution["C_max"]
                    best_insertion_sol = trial_sol
                    best_insertion_solution = trial_solution

        if best_insertion_sol is None:
            if verbose:
                print("Nenhum vizinho 2-Opt factível encontrado; encerrando.")
            break

        if best_insertion_makespan < best_sol_makespan:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            best_sol_makespan = best_insertion_makespan
            improved = True
            if verbose:
                print(f"Melhoria encontrada: novo makespan {best_insertion_makespan} com 2-Opt, tentativa {iterations}")
                print("Solução:", best_sol)
        else:
            # Sem melhoria -> encerra
            break

    if verbose:
        print("Busca Local finalizada.")
        print("Número de iterações:", iterations)
    
    return best_sol, best_solution, improved

def deterministic_job_exchange(inst: Instance, res: List[int], verbose=False) -> Tuple[List[int], Dict]:
    
    if verbose:
        print("\nIniciando Job Exchange...")
    
    best_solution = res
    best_sol = res["sequence_normalized"]    
    best_sol_makespan = best_solution["C_max"]
    
    improved = False
    best_insertion_sol = None
    best_insertion_makespan = float('inf')
    
    iterations = 0

    while best_sol_makespan < best_insertion_makespan:
        for i in range(len(best_sol)):
            for j in range(len(best_sol)):
                if i == j:
                    continue
                # Troca as tarefas nas posições i e j
                new_sol = best_sol[:]
                new_sol[i], new_sol[j] = new_sol[j], new_sol[i]
                
                new_solution = verify_solution(inst, new_sol, verbose=False)
                
                if not new_solution["feasible"]:
                    continue
                
                new_makespan = new_solution["C_max"]
                
                if new_makespan < best_insertion_makespan:
                    best_insertion_makespan = new_makespan
                    best_insertion_sol = new_sol
                    best_insertion_solution = new_solution
                    
        if best_insertion_sol is not None and best_insertion_makespan < best_sol_makespan:
            best_sol = best_insertion_sol
            best_solution = best_insertion_solution
            best_sol_makespan = best_insertion_makespan
            if verbose:
                print(f"Melhoria encontrada: novo makespan {best_insertion_makespan} trocando posições, tentativa {iterations}")
                print("Solução:", best_sol)
            improved = True

        iterations += 1
                
    
        if verbose:
            print("Busca Local finalizada. Achou um ótimo local.")
            print("Número de iterações:", iterations)
    
    return  best_sol, best_solution, improved