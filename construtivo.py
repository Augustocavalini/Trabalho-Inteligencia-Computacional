import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
import networkx as nx

from Modelagem import Instance

# dado que um job já foi colocado na solução, atualiza uma tabela de earliest start times, 
# considerando os atrasos de precedência e os tempos de setup 
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

# pode também considerar o tempo final, escolhendo aquele job que vai ser finalizado mais cedo
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


def get_est_candidates_ordered(inst: Instance, sol_partial: List[int], est_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Obtém a lista de candidatos a serem agendados (jobs não na solução parcial)
    ordenados pelo seu earliest start time (EST).
    """
    print("\n=== Obtendo candidatos a EST (ordenados) ===")
    print(f"Solução parcial: {sol_partial}")
    print(f"EST (tuplas) recebido: {est_tuples}")

    est_map = {job: val for job, val in est_tuples}
    candidates = [(job, est_map[job]) for job in range(inst.n) if job not in sol_partial]
    candidates.sort(key=lambda x: x[1])  # ordena por EST

    print(f"Candidatos a EST (ordenados): {candidates}")
    return candidates

def get_eft_candidates_ordered(inst: Instance, sol_partial: List[int], eft_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Obtém a lista de candidatos a serem agendados (jobs não na solução parcial)
    ordenados pelo seu earliest finish time (EFT).
    """
    # print("\n=== Obtendo candidatos a EFT (ordenados) ===")
    # print(f"Solução parcial: {sol_partial}")
    # print(f"EFT (tuplas) recebido: {eft_tuples}")

    eft_map = {job: val for job, val in eft_tuples}
    candidates = [(job, eft_map[job]) for job in range(inst.n) if job not in sol_partial]
    candidates.sort(key=lambda x: x[1])  # ordena por EFT

    # print(f"Candidatos a EFT (ordenados): {candidates}")
    return candidates

def get_lft_candidates_ordered(inst: Instance, sol_partial: List[int], lft_tuples: List[Tuple[int, float]]) -> List[Tuple[int, float]]:
    """
    Obtém a lista de candidatos a serem agendados (jobs não na solução parcial)
    ordenados pelo seu latest finish time (LFT).
    """
    print("\n=== Obtendo candidatos a LFT (ordenados) ===")
    print(f"Solução parcial: {sol_partial}")
    print(f"LFT (tuplas) recebido: {lft_tuples}")

    lft_map = {job: val for job, val in lft_tuples}
    candidates = [(job, lft_map[job]) for job in range(inst.n) if job not in sol_partial]
    candidates.sort(key=lambda x: x[1])  # ordena por LFT

    print(f"Candidatos a LFT (ordenados): {candidates}")
    return candidates