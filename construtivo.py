import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx
import random

import modelagem as md
from modelagem import Instance

import view as vw

# ******************************** MÉTODOS DE ATUALIZAÇÃO E ORDENAÇÃO ********************************

# dado que um job já foi colocado na solução, atualiza uma tabela de earliest start times, com o tempo em que cada próximo job pode começar 
def update_earliest_start_times(inst: Instance, sol_partial: List[int], est_tuples: List[Tuple[int, float]], verbose: bool = False) -> List[Tuple[int, float]]:
    """
    Atualiza a tabela de earliest start times representada como lista de tuplas
    (job_idx, est_value). Retorna a lista ordenada por est_value (asc).
    """
    if verbose:
        print("\n=== Atualizando earliest start times (tuplas) ===")
        print(f"Solução parcial: {sol_partial}")
        print(f"EST (tuplas) atual: {est_tuples}")

    n = inst.n
    # converte para dicionário para facilitar atualizações
    est_map = {job: val for job, val in est_tuples}
    last_job = sol_partial[-1]
    if verbose:
        print(f"Último job colocado: {last_job}, EST[{last_job}] = {est_map.get(last_job)}")

    for j in range(n):
        if j in sol_partial:
            if verbose:
                print(f"\nJob {j}: já está na solução, pulando...")
            continue

        if verbose:
            print(f"\nProcessando job {j}:")
        old = est_map.get(j, 0.0)

        # setup após último job colocado
        setup_start = est_map[last_job] + inst.p[last_job] + inst.s[last_job][j]
        if verbose:
            print(f"  Setup após job {last_job}: EST[{last_job}]({est_map[last_job]}) + p[{last_job}]({inst.p[last_job]}) + s[{last_job}][{j}]({inst.s[last_job][j]}) = {setup_start}")
        est_map[j] = max(est_map.get(j, 0.0), setup_start)
        if verbose:
            print(f"  EST após setup (temporário) = {est_map[j]}")

        # atrasos de precedência de todos os jobs já na solução
        for i in sol_partial:
            if inst.d[i][j] != -1:
                prec_start = est_map[i] + inst.p[i] + inst.d[i][j]
                if verbose:
                    print(f"  Precedência {i}->{j}: EST[{i}]({est_map[i]}) + p[{i}]({inst.p[i]}) + d[{i}][{j}]({inst.d[i][j]}) = {prec_start}")
                est_map[j] = max(est_map[j], prec_start)
                if verbose:
                    print(f"  EST após precedência = {est_map[j]}")

        if est_map[j] != old:
            if verbose:
                print(f"  EST final de {j} atualizado: {old} -> {est_map[j]}")
        else:
            if verbose:
                print(f"  EST final de {j} mantido: {est_map[j]}")

    # constroi lista ordenada por valor (ascendente)
    # est_updated = sorted([(job, est_map[job]) for job in range(n)], key=lambda x: x[1])
    est_updated = [(job, est_map[job]) for job in range(n)]
    if verbose:
        print(f"\nEST final atualizado (tuplas ordenadas): {est_updated}")
    return est_updated

# dado que um job já foi colocado na solução, atualiza uma tabela de earliest finish times, com o tempo em que cada próximo job vai terminar
def update_earliest_finish_times(inst: Instance, sol_partial: List[int], eft_tuples: List[Tuple[int, float]], verbose: bool = False) -> List[Tuple[int, float]]:
    """
    Atualiza a tabela de earliest finish times representada como lista de tuplas
    (job_idx, eft_value). Retorna a lista ordenada por eft_value (asc).
    """
    # print("\n=== Atualizando earliest finish times (tuplas) ===")
    # print(f"Solução parcial: {sol_partial}")
    # print(f"EFT (tuplas) atual: {eft_tuples}")

    n = inst.n
    # converte para dicionário para facilitar atualizações
    eft_map = {job: val for job, val in eft_tuples}
    last_job = sol_partial[-1]
    # print(f"Último job colocado: {last_job}, EFT[{last_job}] = {eft_map.get(last_job)}")

    for j in range(n):
        if j in sol_partial:
            # print(f"\nJob {j}: já está na solução, pulando...")
            continue

        # print(f"\nProcessando job {j}:")
        old = eft_map.get(j, 0.0)

        # finished time após último job colocado
        job_finished = eft_map[last_job] + inst.s[last_job][j] + inst.p[j]
        # print(f"  Finished time após job {last_job}: EFT[{last_job}]({eft_map[last_job]}) + p[{last_job}]({inst.p[last_job]}) + s[{last_job}][{j}]({inst.s[last_job][j]}) + p[{j}]({inst.p[j]}) = {job_finished}")
        eft_map[j] = max(eft_map.get(j, 0.0), job_finished)
        # print(f"  EFT após setup (temporário) = {eft_map[j]}")

        # atrasos de precedência de todos os jobs já na solução
        for i in sol_partial:
            if inst.d[i][j] != -1:
                prec_finish = eft_map[i] + inst.d[i][j] + inst.p[j]
                if verbose:
                    print(f"  Precedência {i}->{j}: EFT[{i}]({eft_map[i]}) + p[{j}]({inst.p[j]}) + d[{i}][{j}]({inst.d[i][j]}) + p[{j}]({inst.p[j]}) = {prec_finish}")
                eft_map[j] = max(eft_map[j], prec_finish)
                if verbose:
                    print(f"  EFT após precedência = {eft_map[j]}")

        # if eft_map[j] != old:
        #     print(f"  EFT final de {j} atualizado: {old} -> {eft_map[j]}")
        # else:
        #     print(f"  EFT final de {j} mantido: {eft_map[j]}")

    # constroi lista ordenada por valor (ascendente)
    # est_updated = sorted([(job, eft_map[job]) for job in range(n)], key=lambda x: x[1])
    eft_updated = [(job, eft_map[job]) for job in range(n)]
    # print(f"\nEFT final atualizado (tuplas ordenadas): {eft_updated}")
    return eft_updated


def get_candidates_ordered(inst: Instance, sol_partial: List[int], list_tuples: List[Tuple[int, float]], verbose=False) -> List[Tuple[int, float]]:
    """
    Obtém a lista de candidatos a serem agendados (jobs não na solução parcial)
    ordenados pelo valor associado na lista de tuplas (job_idx, value).
    """
    if verbose:
        print("\n=== Obtendo candidatos ordenados ===")
        print(f"Solução parcial: {sol_partial}")
        print(f"Lista (tuplas) recebida: {list_tuples}")

    lft_map = {job: val for job, val in list_tuples}
    candidates = [(job, lft_map[job]) for job in range(inst.n) if job not in sol_partial]
    candidates.sort(key=lambda x: x[1])  # ordena por LFT
    
    if verbose:
        print(f"Candidatos ordenados: {candidates}")
    return candidates

# ******************************** MÉTODOS CONSTRUTIVOS GERAIS ********************************

def greedy_constructive_build(
        inst: Instance, 
        get_candidates_ordered: callable, 
        update_scores: callable, 
        initial_scores: list[tuple[int, float]], 
        initial_seq: Optional[List[int]] = None, 
        plot_title: str | None = None,
        verbose: bool = False
):
    """
    Constrói uma solução viável completa com uma estratégia genérica de ordenação (EFT, EST, etc)
    Critério de ordenação da lista pelo valor associado à essa estratégia.
    Escolha do candidato é gulosa: primeiro que mantém a viabilidade.

    Parâmetros
    ----------
    inst : objeto de instância
        Deve expor:
          - n: int (número total de jobs 0-based)
          - p: list[float]
          - s: list[list[float]]
          - dij: list[list[float]] com -1 para ausência de precedência
    get_candidates_ordered : callable
        Assinatura: get_candidates_ordered(inst, sol_partial, scores) -> list[(job, score_val)]
        Retorna candidatos ordenados (menor score primeiro).
    update_scores : callable
        Assinatura: update_scores(inst, sol_partial, scores) -> list[(job, score_val)]
        Atualiza os scores dado o prefixo atual.
    initial_scores : list[(job, score_val)]
        Lista inicial de (job, valor), ex.: EFT/EST/LFT iniciais para todos os jobs.
    initial_seq : list[int] | None
        Prefixo opcional já construído (deve ser viável). Se None, começa vazio.
    plot_title : str or None
        Título do gráfico, se vw for fornecido.

    Retorna
    -------
    sol : list[int]
        Sequência construída (idealmente completa).
    res : dict
        Resultado de md.verify_solution(inst, sol).
    """
    # inicia prefixo
    sol = initial_seq if initial_seq else []

    # valida prefixo inicial (se houver)
    if sol:
        res0 = md.verify_solution(inst, sol)
        if not res0.get("feasible", False):
            return sol, {
                "feasible": False,
                "violations": ["Prefixo inicial inviável."],
                "C_max": None, "b": None, "c": None, "sequence_normalized": sol
            }

    # copia scores (para não mutar o argumento)
    scores = initial_scores.copy()

    # loop de construção até tentar alocar todos os jobs
    while len(sol) < inst.n:
        candidates = get_candidates_ordered(inst, sol, scores, verbose=verbose)
        if not candidates:
            if verbose:
                print("[constructive_build] Sem candidatos disponíveis. Interrompendo.")
            break

        chosen = None
        for j, _val in candidates:
            if j in sol:
                continue
            trial = sol + [j]
            res_try = md.verify_solution(inst, trial)
            if res_try.get("feasible", False):
                chosen = j
                break

        if chosen is None:
            if verbose:
                print("[constructive_build] Nenhum candidato mantém viabilidade neste passo. Interrompendo.")
            break

        sol.append(chosen)
        # atualiza scores com o prefixo corrente
        scores = update_scores(inst, sol, scores)

    # verificação final
    res = md.verify_solution(inst, sol)

    # plot opcional
    if plot_title is not None:
        try:
            vw.plot_gantt(inst, res, title=plot_title)
        except Exception as e:
            if verbose:
                print(f"[constructive_build] Falha ao plotar Gantt: {e}")
    return sol, res


def randomized_greedy_constructive_build(
    inst: Instance,
    get_candidates_ordered: callable,
    update_scores: callable,
    initial_scores: List[Tuple[int, float]],
    initial_seq: Optional[List[int]] = None,
    plot_title: str | None = None,
    alpha: float = 0.0,
    rcl_size: Optional[int] = None,
    seed: Optional[int] = None,
    verbose: bool = False
):
    """
    Versão gulosa randomizada do construtivo.
    Estratégias de RCL:
      - se rcl_size fornecido: escolhe aleatoriamente entre os top-k candidatos;
      - senão, usa threshold com alpha: RCL = {c | val <= min_val + alpha*(max_val-min_val)}.
    Parâmetros adicionais:
      - alpha: em [0,1], controla largura da RCL (0 = puro guloso).
      - rcl_size: se int, tamanho fixo do RCL (tem preferência sobre alpha).
      - seed: semente para reprodutibilidade.
    Retorna (sol, res) como greedy_constructive_build.
    """
    if seed is not None:
        random.seed(seed)

    sol = initial_seq.copy() if initial_seq else []

    # valida prefixo inicial (se houver)
    if sol:
        res0 = md.verify_solution(inst, sol)
        if not res0.get("feasible", False):
            return sol, {
                "feasible": False,
                "violations": ["Prefixo inicial inviável."],
                "C_max": None, "b": None, "c": None, "sequence_normalized": sol
            }

    scores = initial_scores.copy()

    while len(sol) < inst.n:
        candidates = get_candidates_ordered(inst, sol, scores)
        # filtra candidatos não-agendados mantendo a ordem
        candidates = [(j, v) for j, v in candidates if j not in sol]
        if not candidates:
            if verbose:
                print("[rand_greedy] Sem candidatos disponíveis. Interrompendo.")
            break

        # Construir RCL
        if rcl_size is not None and rcl_size > 0:
            rcl = candidates[:rcl_size]
        else:
            vals = [v for _, v in candidates]
            min_v, max_v = min(vals), max(vals)
            if max_v - min_v <= 1e-12:
                rcl = candidates[:]  # todos equivalentes
            else:
                threshold = min_v + alpha * (max_v - min_v)
                rcl = [c for c in candidates if c[1] <= threshold]
                if not rcl:
                    rcl = candidates[:1]  # garante pelo menos um candidato

        # tenta escolher aleatoriamente um candidato da RCL que mantenha a viabilidade
        rcl_shuffled = rcl.copy()
        random.shuffle(rcl_shuffled)
        chosen = None
        for j, _v in rcl_shuffled:
            trial = sol + [j]
            res_try = md.verify_solution(inst, trial)
            if res_try.get("feasible", False):
                chosen = j
                break

        # se nenhum na RCL manteve viabilidade, tenta buscar pelo restante da lista ordenada
        if chosen is None:
            for j, _v in candidates:
                if j in sol:
                    continue
                trial = sol + [j]
                res_try = md.verify_solution(inst, trial)
                if res_try.get("feasible", False):
                    chosen = j
                    break

        if chosen is None:
            if verbose:
                print("[rand_greedy] Nenhum candidato mantém viabilidade neste passo. Interrompendo.")
            break

        sol.append(chosen)
        scores = update_scores(inst, sol, scores)

    res = md.verify_solution(inst, sol)

    # plot opcional
    if plot_title is not None:
        try:
            vw.plot_gantt(inst, res, title=plot_title)
        except Exception as e:
            if verbose:
                print(f"[constructive_build] Falha ao plotar Gantt: {e}")
    return sol, res

# ******************************** MÉTODO INSERT GULOSO ********************************

def create_precedence_sublist(
    inst: Instance,
    score: Optional[List[Tuple[int, float]]] = None,
    verbose: bool = False
) -> List[int]:
    """
    Retorna uma solução parcial contendo todos os jobs que participam de
    alguma relação de precedência com os jobs já em sol_partial, organizada
    pelo critério de earliest start time (EST) ou earliest finish time (EFT).

    Parâmetros
    ----------
    inst : Instance
    use_eft : se True usa EFT, senão usa EST
    """
    if verbose:
        print("\n=== Atualizando sublista de precedências ===")

    # identifica todos os jobs que participam de alguma precedência
    involved = set()
    n = inst.n
    for i in range(n):
        for j in range(n):
            if inst.d[i][j] != -1:
                involved.add(i)
                involved.add(j)
                    
    missing_jobs = [j for j in range(n) if j not in involved]

    scores = [(j, 0) for j in range(inst.n)]

    # inicia prefixo
    sol = []

    # loop de construção até tentar alocar todos os jobs
    while len(sol) < len(involved):
        candidates = get_candidates_ordered(inst, sol, scores, verbose=verbose)
        if not candidates:
            if verbose:
                print("[constructive_build] Sem candidatos disponíveis. Interrompendo.")
            break

        chosen = None
        for j, _val in candidates:
            if j in sol or j not in involved:
                continue

            trial = sol + [j]
            res_try = md.verify_solution(inst, trial)
            if res_try.get("feasible", False):
                chosen = j
                break

        if chosen is None:
            if verbose:
                print("[constructive_build] Nenhum candidato mantém viabilidade neste passo. Interrompendo.")
            break

        sol.append(chosen)
        # atualiza scores com o prefixo corrente
        scores = update_earliest_start_times(inst, sol, scores)

    # verificação final
    res = md.verify_solution(inst, sol)

    return sol, res, missing_jobs


def greedy_constructive_insert(
    inst: Instance,
    sequence: List[int],
    missing_jobs: List[int],
    verbose: bool = False,
    plot_title: str | None = None
) -> List[int]:
    """
    Insere, de forma gulosa, todos os jobs em missing_jobs na sequência parcial 'sequence'.
    Em cada iteração:
      - testa inserir cada job ainda faltante em todas as posições possíveis da sequência;
      - avalia o makespan (C_max) de cada sequência candidata com md.verify_solution;
      - escolhe o par (job, posição) que gera o menor C_max viável;
      - fixa essa inserção na sequência.
    Repete até que todos os jobs sejam inseridos ou não seja possível manter viabilidade.
    """
    sol = sequence.copy()
    remaining = missing_jobs.copy()

    while remaining:
        best_job = None
        best_pos = None
        best_cmax = float("inf")

        for j in remaining:
            # tenta inserir o job j em todas as posições possíveis
            for pos in range(len(sol) + 1):
                cand = sol[:pos] + [j] + sol[pos:]
                res = md.verify_solution(inst, cand)
                if not res.get("feasible", False):
                    continue

                cmax = res.get("C_max", float("inf"))
                if cmax < best_cmax:
                    best_cmax = cmax
                    best_job = j
                    best_pos = pos

        # se não encontrou nenhuma inserção viável para nenhum job restante, encerra
        if best_job is None:
            if verbose:
                print("[greedy_constructive_insert] Nenhuma inserção viável encontrada para os jobs restantes.")
            break

        # fixa melhor inserção encontrada
        sol = sol[:best_pos] + [best_job] + sol[best_pos:]
        remaining.remove(best_job)

        if verbose:
            print(f"Inserido job {best_job} na posição {best_pos}, C_max = {best_cmax}")
            print(f"Solução atual: {sol}")
            print(f"Jobs restantes: {remaining}")
            
    res = md.verify_solution(inst, sol)
    
    if plot_title is not None:
        try:
            vw.plot_gantt(inst, res, title=plot_title)
        except Exception as e:
            if verbose:
                print(f"[constructive_build] Falha ao plotar Gantt: {e}")
    return sol, res