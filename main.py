import Modelagem as md
import view as vw
import construtivo as ct

# inst = load_instance_from_txt("Instancias\\N10_P(10-20)_S(5-10)_A(20-40)_W5_Wo2_P2.txt")
inst = md.load_instance_from_txt("teste.txt") 


# sol = [2, 5]  # Exemplo de solução (sequência de jobs reais)
# sol = [x-1 for x in sol]  # ajusta índices
# res = md.verify_solution(inst, sol)

# if res["feasible"]:
#     print("\nSolução viável!")
#     vw.plot_gantt(inst, res, title="Gantt da solução — Exemplo didático")
# else:
#     print("\nSolução inviável!")
#     print(f"Detalhes da inviabilidade: {res.get('violations', 'N/A')}")

# ***********************************************************

# # ---------------------------
# # Construtivo por EFT (viável a cada passo)
# # ---------------------------
# sol_partial = []

# # EFT inicial: (job, eft_inicial) — aqui uso p[j] como chute/base
# eft = [(j, inst.p[j]) for j in range(inst.n)]

# for _ in range(inst.n):
#     # candidatos ordenados por EFT (função já implementada por você)
#     candidates = ct.get_eft_candidates_ordered(inst, sol_partial, eft)
#     if not candidates:
#         print("\nSem candidatos disponíveis. Interrompendo construção.")
#         break

#     # escolhe o primeiro candidato que mantém a parcial viável
#     chosen = None
#     for j, _eft_val in candidates:
#         if j in sol_partial:
#             continue  # evita duplicar
#         trial = sol_partial + [j]
#         if md.verify_solution(inst, trial)["feasible"]:
#             chosen = j
#             break

#     if chosen is None:
#         print("\nNenhum candidato mantém a viabilidade neste passo. Interrompendo.")
#         break

#     # insere o escolhido
#     sol_partial.append(chosen)
#     print(f"\nSolução parcial viável: {sol_partial}")

#     # atualiza EFTs com a parcial atual (função sua)
#     eft = ct.update_earliest_finish_times(inst, sol_partial, eft)
#     print(f"Solução construtiva por EFT (parcial): {sol_partial}")

# # verificação final e Gantt
# res = md.verify_solution(inst, sol_partial)
# vw.plot_gantt(inst, res, title="Gantt da solução — Construtivo por EFT")

# sua lista inicial EFT (ex.: baseada só em p[j] ou como você já constrói)
initial_eft = [(j, inst.p[j]) for j in range(inst.n)]

# passe as funções da sua estratégia (já implementadas no seu módulo ct)
sol, res = ct.constructive_build(
    inst=inst,
    md=md,
    get_candidates_ordered=ct.get_eft_candidates_ordered,
    update_scores=ct.update_earliest_finish_times,
    initial_scores=initial_eft,
    initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
    vw=vw,
    plot_title="Gantt — Construtivo por EFT"
)

initial_est = [(j, 0) for j in range(inst.n)]

# passe as funções da sua estratégia (já implementadas no seu módulo ct)
sol, res = ct.constructive_build(
    inst=inst,
    md=md,
    get_candidates_ordered=ct.get_est_candidates_ordered,
    update_scores=ct.update_earliest_start_times,
    initial_scores=initial_est,
    initial_seq=None,  # ou um prefixo viável se quiser começar de um parcial
    vw=vw,
    plot_title="Gantt — Construtivo por EST"
)