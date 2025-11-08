import Modelagem as md
import view as vw
import construtivo as ct

# inst = load_instance_from_txt("Instancias\\N10_P(10-20)_S(5-10)_A(20-40)_W5_Wo2_P2.txt")
inst = md.load_instance_from_txt("teste.txt") 


# sol = [1, 2, 3, 4, 5]  # Exemplo de solução (sequência de jobs reais)
# res = md.verify_solution(inst, sol)
# vw.plot_gantt(inst, res, title="Gantt da solução — Exemplo didático")

# sol = [1, 2, 5, 3, 4]  # Exemplo de solução (sequência de jobs reais)
# res = md.verify_solution(inst, sol)
# vw.plot_gantt(inst, res, title="Gantt da solução — Exemplo didático")

# # ordenando pelo earliest_start_times
# sol_partial = [0]
# est = [(idx, 0.0) for idx, _ in enumerate(range(inst.n))]

# est = ct.update_earliest_start_times(inst, sol_partial, est)

# sol_partial = [0, 1]
# est = ct.update_earliest_start_times(inst, sol_partial, est)

# # sol_partial = [1, 2, 4]
# # sol_partial = [x-1 for x in sol_partial]  # ajusta índices
# sol_partial = [0, 1, 3]

# est = ct.update_earliest_start_times(inst, sol_partial, est)

# candidates = ct.get_est_candidates_ordered(inst, sol_partial, est)

# ***********************************************************

# ordenando pelo earliest_finish_times
sol_partial = []
eft = [(idx, inst.p[idx]) for idx, _ in enumerate(range(inst.n))]
for _ in range(inst.n):
    candidates = ct.get_eft_candidates_ordered(inst, sol_partial, eft)
    sol_partial.append(candidates[0][0])  # adiciona o job com menor EFT
    eft = ct.update_earliest_finish_times(inst, sol_partial, eft)

    print(f"\nSolução construtiva por EFT: {sol_partial}")

res = md.verify_solution(inst, sol_partial)
vw.plot_gantt(inst, res, title="Gantt da solução — Construtivo por EFT")
    

