import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx
import random

import Modelagem as md
from Modelagem import Instance

import view as vw

# ******************************** MÉTODOS DE ATUALIZAÇÃO E ORDENAÇÃO ********************************

# dado que um job já foi colocado na solução, atualiza uma tabela de earliest start times, com o tempo em que cada próximo job pode começar 
def update_earliest_start_times(inst: Instance, sol_partial: List[int], est_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Atualiza a tabela de earliest start times representada como lista de tuplas
    (job_idx, est_value). Retorna a lista ordenada por est_value (asc).
    """
    print("\n=== Atualizando earliest start times (tuplas) ===")
    print(f"Solução parcial: {sol_partial}")
    print(f"EST (tuplas) atual: {est_tuples}")

    n = inst.n
    # converte para dicionário para facilitar atualizações
    est_map = {job: val for job, val in est_tuples}
    last_job = sol_partial[-1]
    print(f"Último job colocado: {last_job}, EST[{last_job}] = {est_map.get(last_job)}")

    for j in range(n):
        if j in sol_partial:
            print(f"\nJob {j}: já está na solução, pulando...")
            continue

        print(f"\nProcessando job {j}:")
        old = est_map.get(j, 0.0)

        # setup após último job colocado
        setup_start = est_map[last_job] + inst.p[last_job] + inst.s[last_job][j]
        print(f"  Setup após job {last_job}: EST[{last_job}]({est_map[last_job]}) + p[{last_job}]({inst.p[last_job]}) + s[{last_job}][{j}]({inst.s[last_job][j]}) = {setup_start}")
        est_map[j] = max(est_map.get(j, 0.0), setup_start)
        print(f"  EST após setup (temporário) = {est_map[j]}")

        # atrasos de precedência de todos os jobs já na solução
        for i in sol_partial:
            if inst.d[i][j] != -1:
                prec_start = est_map[i] + inst.p[i] + inst.d[i][j]
                print(f"  Precedência {i}->{j}: EST[{i}]({est_map[i]}) + p[{i}]({inst.p[i]}) + d[{i}][{j}]({inst.d[i][j]}) = {prec_start}")
                est_map[j] = max(est_map[j], prec_start)
                print(f"  EST após precedência = {est_map[j]}")

        if est_map[j] != old:
            print(f"  EST final de {j} atualizado: {old} -> {est_map[j]}")
        else:
            print(f"  EST final de {j} mantido: {est_map[j]}")

    # constroi lista ordenada por valor (ascendente)
    # est_updated = sorted([(job, est_map[job]) for job in range(n)], key=lambda x: x[1])
    est_updated = [(job, est_map[job]) for job in range(n)]
    print(f"\nEST final atualizado (tuplas ordenadas): {est_updated}")
    return est_updated

# dado que um job já foi colocado na solução, atualiza uma tabela de earliest finish times, com o tempo em que cada próximo job vai terminar
def update_earliest_finish_times(inst: Instance, sol_partial: List[int], eft_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
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
                print(f"  Precedência {i}->{j}: EFT[{i}]({eft_map[i]}) + p[{j}]({inst.p[j]}) + d[{i}][{j}]({inst.d[i][j]}) + p[{j}]({inst.p[j]}) = {prec_finish}")
                eft_map[j] = max(eft_map[j], prec_finish)
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

# ??
def update_latest_finish_times(inst: Instance, sol_partial: List[int], lft_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Atualiza a tabela de latest finish times representada como lista de tuplas
    (job_idx, lft_value). Retorna a lista ordenada por lft_value (asc).
    """
    print("\n=== Atualizando latest finish times (tuplas) ===")
    print(f"Solução parcial: {sol_partial}")
    print(f"LFT (tuplas) atual: {lft_tuples}")

    n = inst.n
    lft_map = {job: val for job, val in lft_tuples}
    last_job = sol_partial[-1]
    print(f"Último job colocado: {last_job}, LFT[{last_job}] = {lft_map.get(last_job)}")

    for j in range(n):
        if j in sol_partial:
            print(f"\nJob {j}: já está na solução, pulando...")
            continue

        print(f"\nProcessando job {j}:")
        old = lft_map.get(j, 0.0)

        # consideração de setup (termino possível antes do last_job)
        setup_finish = lft_map[last_job] + inst.p[j] + inst.s[last_job][j]
        print(f"  Setup antes de job {last_job}: LFT[{last_job}]({lft_map[last_job]}) + p[{j}]({inst.p[j]}) + s[{last_job}][{j}]({inst.s[last_job][j]}) = {setup_finish}")
        lft_map[j] = max(lft_map.get(j, 0.0), setup_finish)
        print(f"  LFT após setup (temporário) = {lft_map[j]}")

        # atrasos de precedência (restrições que impõem um limite superior)
        for i in sol_partial:
            if inst.d[i][j] != -1:
                prec_finish = lft_map[i] + inst.p[j] + inst.d[i][j]
                print(f"  Precedência {i}->{j}: LFT[{i}]({lft_map[i]}) + p[{j}]({inst.p[j]}) + d[{i}][{j}]({inst.d[i][j]}) = {prec_finish}")
                lft_map[j] = max(lft_map[j], prec_finish)
                print(f"  LFT após precedência = {lft_map[j]}")

        if lft_map[j] != old:
            print(f"  LFT final de {j} atualizado: {old} -> {lft_map[j]}")
        else:
            print(f"  LFT final de {j} mantido: {lft_map[j]}")

    # constroi lista ordenada por valor (ascendente)
    # lft_updated = sorted([(job, lft_map[job]) for job in range(n)], key=lambda x: x[1])
    lft_updated = [(job, lft_map[job]) for job in range(n)]
    print(f"\nLFT final atualizado (tuplas ordenadas): {lft_updated}")
    return lft_updated


def get_candidates_ordered(inst: Instance, sol_partial: List[int], list_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Obtém a lista de candidatos a serem agendados (jobs não na solução parcial)
    ordenados pelo valor associado na lista de tuplas (job_idx, value).
    """
    print("\n=== Obtendo candidatos ordenados ===")
    print(f"Solução parcial: {sol_partial}")
    print(f"Lista (tuplas) recebida: {list_tuples}")

    lft_map = {job: val for job, val in list_tuples}
    candidates = [(job, lft_map[job]) for job in range(inst.n) if job not in sol_partial]
    candidates.sort(key=lambda x: x[1])  # ordena por LFT

    print(f"Candidatos ordenados: {candidates}")
    return candidates

# ******************************** MÉTODOS CONSTRUTIVOS GERAIS ********************************

def greedy_constructive_build(
        inst: Instance, 
        get_candidates_ordered: callable, 
        update_scores: callable, 
        initial_scores: list[tuple[int, float]], 
        initial_seq: Optional[List[int]] = None, 
        plot_title: str | None = "Gantt — Construtivo Guloso"
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
        res0 = md.verify_solution(inst, sol, verbose=True)
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
        candidates = get_candidates_ordered(inst, sol, scores)
        if not candidates:
            print("[constructive_build] Sem candidatos disponíveis. Interrompendo.")
            break

        chosen = None
        for j, _val in candidates:
            if j in sol:
                continue
            trial = sol + [j]
            res_try = md.verify_solution(inst, trial, verbose=True)
            if res_try.get("feasible", False):
                chosen = j
                break

        if chosen is None:
            print("[constructive_build] Nenhum candidato mantém viabilidade neste passo. Interrompendo.")
            break

        sol.append(chosen)
        # atualiza scores com o prefixo corrente
        scores = update_scores(inst, sol, scores)

    # verificação final
    res = md.verify_solution(inst, sol, verbose=True)

    # plot opcional
    if plot_title is not None:
        try:
            vw.plot_gantt(inst, res, title=plot_title)
        except Exception as e:
            print(f"[constructive_build] Falha ao plotar Gantt: {e}")
    return sol, res


def randomized_greedy_constructive_build(
    inst: Instance,
    get_candidates_ordered: callable,
    update_scores: callable,
    initial_scores: List[Tuple[int, float]],
    initial_seq: Optional[List[int]] = None,
    plot_title: str | None = "Gantt — Construtivo Randômico",
    alpha: float = 0.0,
    rcl_size: Optional[int] = None,
    seed: Optional[int] = None
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
        res0 = md.verify_solution(inst, sol, verbose=True)
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
            res_try = md.verify_solution(inst, trial, verbose=True)
            if res_try.get("feasible", False):
                chosen = j
                break

        # se nenhum na RCL manteve viabilidade, tenta buscar pelo restante da lista ordenada
        if chosen is None:
            for j, _v in candidates:
                if j in sol:
                    continue
                trial = sol + [j]
                res_try = md.verify_solution(inst, trial, verbose=True)
                if res_try.get("feasible", False):
                    chosen = j
                    break

        if chosen is None:
            print("[rand_greedy] Nenhum candidato mantém viabilidade neste passo. Interrompendo.")
            break

        sol.append(chosen)
        scores = update_scores(inst, sol, scores)

    res = md.verify_solution(inst, sol, verbose=True)

    # plot opcional
    if plot_title is not None:
        try:
            vw.plot_gantt(inst, res, title=plot_title)
        except Exception as e:
            print(f"[constructive_build] Falha ao plotar Gantt: {e}")
    return sol, res

