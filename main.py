import modelagem as md
import view as vw
import construtivo as ct
import busca_local as bl
import metaheuristica as mh
import pandas as pd  # <- novo import
import time


def run_simulations_for_instance(file_path: str, max_stagnation: int = 10) -> None:
    """
    Executa o pipeline de simulações para uma instância:
      1) Carrega instância
      2) Constrói soluções por EST e EFT
      3) Escolhe a melhor para iniciar busca local
      4) Roda operadores de busca local com critério de estagnação
    """
    print(f"\n==============================")
    print(f"Rodando instância: {file_path}")
    print(f"==============================")

    # 1) Carregar instância
    inst = md.load_instance_from_txt("Instancias\\"+file_path)

    # 2) Construtivo por EST
    initial_est = [(j, 0) for j in range(inst.n)]
    sol_est, res_est = ct.greedy_constructive_build(
        inst=inst,
        get_candidates_ordered=ct.get_candidates_ordered,
        update_scores=ct.update_earliest_start_times,
        initial_scores=initial_est,
        initial_seq=None,
        # plot_title="Gantt — Construtivo por EST"
    )

    # 2) Construtivo por EFT
    initial_eft = [(j, inst.p[j]) for j in range(inst.n)]
    sol_eft, res_eft = ct.greedy_constructive_build(
        inst=inst,
        get_candidates_ordered=ct.get_candidates_ordered,
        update_scores=ct.update_earliest_finish_times,
        initial_scores=initial_eft,
        initial_seq=None,
        # plot_title="Gantt — Construtivo por EFT"
    )
    
    # 3) Construtivo por Precedence Sublist e greedy insertion
    precedence_sol, res_precedence,  missing_jobs = ct.create_precedence_sublist(inst=inst)
    sol_precedence, res_precedence = ct.greedy_constructive_insert(
        inst=inst, sequence=precedence_sol, missing_jobs=missing_jobs
        # plot_title="Gantt — Construtivo por Precedence Sublist"
    )
    
    print(f"Solução por Precedence Sublist: C_max = {res_precedence['C_max']:.3f}")

    print(f"\nComparação das soluções construtivas:")
    print(f" - EST: C_max = {res_est['C_max']:.3f} | sequencia: {sol_est}")
    print(f" - EFT: C_max = {res_eft['C_max']:.3f} | sequencia: {sol_eft}")
    print(f" - Precedence Sublist: C_max = {res_precedence['C_max']:.3f} | sequencia: {sol_precedence}")

    # 3) Escolher melhor ponto de partida
    def is_better(a, b):
        """Melhor = factível e com menor C_max."""
        if not a.get("feasible", False):
            return False
        if not b.get("feasible", False):
            return True
            
        return a["C_max"] <= b["C_max"]

    start_sol, start_res = (sol_eft, res_eft) if is_better(res_eft, res_est) else (sol_est, res_est)
    start_sol, start_res = (start_sol, start_res) if is_better(start_res, res_precedence) else (sol_precedence, res_precedence)

    if not start_res.get("feasible", False):
        print("[ERRO] Nenhuma solução construtiva viável encontrada. Encerrando esta instância.")
        return

    print(f"Solução inicial escolhida: C_max = {start_res['C_max']:.3f}")

    # ---------- Helpers para loops de estagnação ----------
    def run_stagnation_loop(label: str, fn, res_in, params: dict = {}):
        """Roda operador local até estagnar por 'max_stagnation'."""
        stagnation_counter = 0
        current_res = res_in

        while stagnation_counter < max_stagnation:
            sol_out, res_out, improved = fn(inst=inst, res=current_res, **params) # ** desempacota o dicionário 'params' em argumentos nomeados
            if improved:
                # vw.plot_gantt(inst, res_out, title=f"Gantt — Após Encontrar OL {label} {stagnation_counter}")
                print(f"[{label}] Melhoria encontrada! C_max = {res_out['C_max']:.3f}")
                current_res = res_out
                stagnation_counter = 0
            else:
                stagnation_counter += 1
                print(f"[{label}] Nenhuma melhoria. Estagnação: {stagnation_counter}/{max_stagnation}")

        # vw.plot_gantt(inst, current_res, title=f"Gantt — Após {label}")
        return current_res

    # 4) Fases de busca local (cada fase começa do melhor resultado até então)
    # best_res_bl = start_res
    best_res_vns = start_res

    # JOB EXCHANGE
    # best_res_bl = run_stagnation_loop("JE", bl.bl_job_exchange, best_res_bl)

    # # BLOCK THROW
    # best_res = run_stagnation_loop("BT", bl.insert_block_random, best_res)

    # # INSERT JOB RANDOM
    # best_res = run_stagnation_loop("IJR", bl.insert_job_random, best_res)

    # # INSERT JOB BEST
    # best_res = run_stagnation_loop("IJB", bl.insert_job_best, best_res)

    # # INSERT BLOCK BEST
    # print(f"\nParâmetros para IBB: min_block_size=2, max_block_size={int(inst.n*0.4)}")
    # best_res = run_stagnation_loop("IBB", bl.insert_block_best, best_res, params={"min_block_size": 2, "max_block_size": int(inst.n*0.4)})

    # 5) VNS a partir da melhor sequência atual (se disponível)
    if "sequence_normalized" in best_res_vns:
        # try:
        vns_res = mh.VNS(inst, best_res_vns, max_iter=100, max_stagnation=10, verbose=False)
        if vns_res["C_max"] < best_res_vns["C_max"]:
            print(f"[VNS] Melhoria: {best_res_vns['C_max']:.3f} -> {vns_res['C_max']:.3f}")
            best_res_vns = vns_res
        else:
            print(f"[VNS] Sem melhoria (C_max = {vns_res['C_max']:.3f})")
        # except Exception as e:
            # print(f"[VNS] Erro ao executar: {e}")
    else:
        print("[VNS] sequence_normalized ausente; VNS não executado.")

    print(f"\nFinal da instância {file_path} — Melhor C_max = {best_res_vns['C_max']:.3f}")

    return best_res_vns["C_max"]


if __name__ == "__main__":
    
    excel_path = "Resultados.xlsx"
    df = pd.read_excel(excel_path, header=0)

    # quantidade_inst_para_testar = 5 # vai testar as primeiras 5 instâncias listadas na coluna A do Excel
    quantidade_inst_para_testar = len(df)  # vai testar todas as instâncias listadas na coluna A do Excel

    # Defina abaixo quais índices (linhas) deseja processar.
    # Exemplo para só a linha 52: rows_to_run = [52]
    # Para todas: rows_to_run = None
    rows_to_run = None # Ajuste conforme necessidade

    if rows_to_run is None:
        indices = list(range(quantidade_inst_para_testar))
    else:
        indices = rows_to_run

    for row in indices:
        file_name = str(df.iloc[row, 0]).strip()
        if not file_name:
            continue

        num_it = 10
        best_result = None
        best_result_lit = df.iloc[row, 5]  # Coluna F (6) melhor da literatura
        print(f"\nIniciando simulações para instância: {file_name} (linha {row})")
        print("best_result_lit =", best_result_lit)
        print("------------------------------")

        sum_results = 0.0
        sum_time = 0.0

        for it in range(num_it):
            start_time = time.time()
            best_res_vns = run_simulations_for_instance(file_name)
            end_time = time.time()
            elapsed_time = end_time - start_time

            sum_results += best_res_vns
            sum_time += elapsed_time

            if best_result is None or best_res_vns < best_result:
                best_result = best_res_vns

        mean_result = sum_results / num_it
        mean_time = sum_time / num_it
        diff_best = ((best_result - best_result_lit) / best_result_lit) * 100

        # colocar para que as simulações rodem para todas as instâncias listadas na coluna A do Excel
        # e escrevam os resultados necessários nas outras colunas:
        # G: melhor resultado (coluna 7)
        # H: média (10x) (coluna 8)
        # I: tempo (s) (coluna 9)
        # J: dif best (que está na coluna F:6) (%) (coluna 10)

        df.iloc[row, 6] = best_result      # Coluna G
        df.iloc[row, 7] = mean_result      # Coluna H
        df.iloc[row, 8] = mean_time        # Coluna I
        df.iloc[row, 9] = diff_best        # Coluna J

        # Salva imediatamente após processar a linha
        df.to_excel("Resultados_atualizado.xlsx", index=False)
        print(f"[SALVO] Atualizada linha {row} em Resultados_atualizado.xlsx")