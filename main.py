import Modelagem as md
import view as vw
import construtivo as ct
import busca_local as bl

inst = md.load_instance_from_txt("Instancias\\N10_P(10-20)_S(5-10)_A(20-40)_W5_Wo2_P2.txt")
inst = md.load_instance_from_txt("Instancias\\N20_P(10-20)_S(5-10)_A(20-40)_W10_Wo5_P1.txt")
# inst = md.load_instance_from_txt("teste.txt") 

# lista inicial EST (ex.: baseada só em 0)
initial_est = [(j, 0) for j in range(inst.n)]

sol, res = ct.greedy_constructive_build(
    inst=inst,
    get_candidates_ordered=ct.get_candidates_ordered,
    update_scores=ct.update_earliest_start_times,
    initial_scores=initial_est,
    initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
    plot_title="Gantt — Construtivo por EST"
)


# lista inicial EFT (ex.: baseada só em p[j])
initial_eft = [(j, inst.p[j]) for j in range(inst.n)]

sol, res = ct.greedy_constructive_build(
    inst=inst,
    get_candidates_ordered=ct.get_candidates_ordered,
    update_scores=ct.update_earliest_finish_times,
    initial_scores=initial_eft,
    initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
    plot_title="Gantt — Construtivo por EFT"
)

# *********************************************************************************************************************
# BUSCA LOCAL 1

# max_stagnation = 10
# stagnation_counter = 0
# buscalocal_res = res

# while stagnation_counter < max_stagnation:
#     buscalocal_sol, buscalocal_res, improved = bl.buscalocal1(
#         inst=inst, res=buscalocal_res
#     )
#     if improved:
#         vw.plot_gantt(inst, buscalocal_res, title=f"Gantt — Após Encontrar OL BL1 {stagnation_counter}")
#         stagnation_counter = 0
#     else:
#         print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
#         stagnation_counter += 1

# vw.plot_gantt(inst, buscalocal_res, title="Gantt — Após Busca Local 1")

# *********************************************************************************************************************
# JOB EXCHANGE

max_stagnation = 10
stagnation_counter = 0
job_exchange_res = res

while stagnation_counter < max_stagnation:
    job_exchange_sol, job_exchange_res, improved = bl.bl_job_exchange(
        inst=inst, res= res
    )

    if improved:
        vw.plot_gantt(inst, job_exchange_res, title=f"Gantt — Após Encontrar OL JE {stagnation_counter}")
        stagnation_counter = 0
    else:
        print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
        stagnation_counter += 1

vw.plot_gantt(inst, job_exchange_res, title="Gantt — Após Job Exchange")


# ********************************************************************************************************************
# BLOCK THROW

max_stagnation = 10
stagnation_counter = 0
block_throw_res = res

while stagnation_counter < max_stagnation:
    block_throw_sol, block_throw_res, improved = bl.insert_block_random(
        Inst=inst, res= res
    )

    if improved:
        vw.plot_gantt(inst, block_throw_res, title=f"Gantt — Após Encontrar OL BT {stagnation_counter}")
        stagnation_counter = 0
    else:
        print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
        stagnation_counter += 1
        
vw.plot_gantt(inst, block_throw_res, title="Gantt — Após Block Throw")


#*********************************************************************************************************************
# INSERT_JOB_RANDOM
max_stagnation = 10
stagnation_counter = 0
insert_job_random_res = res

while stagnation_counter < max_stagnation:
    insert_job_random_sol, insert_job_random_res, improved = bl.insert_job_random(
        inst=inst, res= res
    )

    if improved:
        vw.plot_gantt(inst, insert_job_random_res, title=f"Gantt — Após Encontrar OL IJR {stagnation_counter}")
        stagnation_counter = 0
    else:
        print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
        stagnation_counter += 1

vw.plot_gantt(inst, insert_job_random_res, title="Gantt — Após Insert Job Random")


#*********************************************************************************************************************
#INSERT_JOB_BEST
max_stagnation = 10
stagnation_counter = 0
insert_job_best_res = res

while stagnation_counter < max_stagnation:
    insert_job_best_sol, insert_job_best_res, improved = bl.insert_job_best(
        inst=inst, res= res
    )

    if improved:
        vw.plot_gantt(inst, insert_job_best_res, title=f"Gantt — Após Encontrar OL IJB {stagnation_counter}")
        stagnation_counter = 0
        
    else:
        stagnation_counter += 1
        print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
        
vw.plot_gantt(inst, insert_job_best_res, title="Gantt — Após Insert Job Best")

# *********************************************************************************************************************
# #INSERT_BLOCK_BEST
max_stagnation = 10
stagnation_counter = 0 
insert_block_best_res = res

while stagnation_counter < max_stagnation:
    insert_block_best_sol, insert_block_best_res, improved = bl.insert_block_best(
        inst=inst, res= res
    )

    if improved:
        vw.plot_gantt(inst, insert_block_best_res, title=f"Gantt — Após Encontrar OL IBB {stagnation_counter}")
        stagnation_counter = 0
        
    else:
        stagnation_counter += 1
        print(f"Nenhuma melhoria encontrada. Contador de estagnação: {stagnation_counter}")
        
vw.plot_gantt(inst, insert_block_best_res, title="Gantt — Após Insert Block Best")

# # inicializa scores (EFT/EST/LFT iniciais). aqui usamos zeros como exemplo.
# initial_scores = [(j, 0.0) for j in range(inst.n)]

# # chamada do construtivo guloso randomizado
# sol, res = ct.randomized_greedy_constructive_build(
#     inst=inst,
#     get_candidates_ordered=ct.get_candidates_ordered,
#     update_scores=ct.update_earliest_finish_times,
#     initial_scores=initial_scores,
#     initial_seq=None,    # ou um prefixo viável [0,1,...]
#     plot_title="Gantt — Construtivo Randômico",
#     alpha=0.3,           # largura da RCL (0 = puro guloso)
#     rcl_size=None,       # ou um int para top-k
#     seed=42              # para reprodutibilidade
# )



# Parâmetros do GRASP
# n_constructions = 10  # número de soluções a construir
# best_sol = None
# best_res = None
# best_makespan = float('inf')

# print(f"\nConstruindo {n_constructions} soluções...")

# for i in range(n_constructions):
#     print(f"\n=== Construção {i+1}/{n_constructions} ===")
    
#     # inicializa scores (EFT/EST/LFT iniciais)
#     initial_scores = [(j, 0.0) for j in range(inst.n)]
    
#     # constrói uma solução
#     sol, res = ct.randomized_greedy_constructive_build(
#         inst=inst,
#         get_candidates_ordered=ct.get_candidates_ordered,
#         update_scores=ct.update_earliest_finish_times,
#         initial_scores=initial_scores,
#         initial_seq=None,
#         plot_title=None,  # não plota Gantt intermediário
#         alpha=0.3,
#         rcl_size=None,
#         seed=42+i  # seed diferente para cada construção
#     )
    
#     # atualiza melhor solução
#     if res["feasible"] and res["C_max"] < best_makespan:
#         best_makespan = res["C_max"]
#         best_sol = sol
#         best_res = res
#         print(f"Nova melhor solução! Makespan: {best_makespan}")

# print(f"\n=== Melhor solução encontrada ===")
# print(f"Sequência: {best_sol}")
# print(f"Makespan: {best_makespan}")

# # Plota apenas a melhor solução
# if best_sol is not None:
#     vw.plot_gantt(inst, best_res, title=f"Gantt — Melhor solução GRASP (C_max={best_makespan:.1f})")