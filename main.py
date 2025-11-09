import Modelagem as md
import view as vw
import construtivo as ct

inst = md.load_instance_from_txt("Instancias\\N10_P(10-20)_S(5-10)_A(20-40)_W5_Wo2_P2.txt")
# inst = md.load_instance_from_txt("teste.txt") 

# # lista inicial EST (ex.: baseada só em 0)
# initial_est = [(j, 0) for j in range(inst.n)]

# sol, res = ct.greedy_constructive_build(
#     inst=inst,
#     get_candidates_ordered=ct.get_candidates_ordered,
#     update_scores=ct.update_earliest_start_times,
#     initial_scores=initial_est,
#     initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
#     plot_title="Gantt — Construtivo por EST"
# )


# # lista inicial EFT (ex.: baseada só em p[j])
# initial_eft = [(j, inst.p[j]) for j in range(inst.n)]

# sol, res = ct.greedy_constructive_build(
#     inst=inst,
#     get_candidates_ordered=ct.get_candidates_ordered,
#     update_scores=ct.update_earliest_finish_times,
#     initial_scores=initial_eft,
#     initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
#     plot_title="Gantt — Construtivo por EFT"
# )


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
n_constructions = 10  # número de soluções a construir
best_sol = None
best_res = None
best_makespan = float('inf')

print(f"\nConstruindo {n_constructions} soluções...")

for i in range(n_constructions):
    print(f"\n=== Construção {i+1}/{n_constructions} ===")
    
    # inicializa scores (EFT/EST/LFT iniciais)
    initial_scores = [(j, 0.0) for j in range(inst.n)]
    
    # constrói uma solução
    sol, res = ct.randomized_greedy_constructive_build(
        inst=inst,
        get_candidates_ordered=ct.get_candidates_ordered,
        update_scores=ct.update_earliest_finish_times,
        initial_scores=initial_scores,
        initial_seq=None,
        plot_title=None,  # não plota Gantt intermediário
        alpha=0.3,
        rcl_size=None,
        seed=42+i  # seed diferente para cada construção
    )
    
    # atualiza melhor solução
    if res["feasible"] and res["C_max"] < best_makespan:
        best_makespan = res["C_max"]
        best_sol = sol
        best_res = res
        print(f"Nova melhor solução! Makespan: {best_makespan}")

print(f"\n=== Melhor solução encontrada ===")
print(f"Sequência: {best_sol}")
print(f"Makespan: {best_makespan}")

# Plota apenas a melhor solução
if best_sol is not None:
    vw.plot_gantt(inst, best_res, title=f"Gantt — Melhor solução GRASP (C_max={best_makespan:.1f})")