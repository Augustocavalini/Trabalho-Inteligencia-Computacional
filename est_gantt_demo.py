import os
import matplotlib.pyplot as plt

# ============================================================
# Exemplo simples de instância
# (substitua por Instance real se quiser depois)
# ============================================================

class SimpleInstance:
    def __init__(self, p, S):
        self.p = p          # tempos de processamento
        self.n = len(p)     # número de jobs
        self.S = S          # matriz de setup s_ij


# Exemplo com 4 jobs
p = [3, 2, 4, 3]  # J0, J1, J2, J3
S = [
    [0, 1, 3, 2],
    [2, 0, 2, 4],
    [3, 1, 0, 2],
    [2, 3, 2, 0],
]

inst = SimpleInstance(p, S)

# Pasta de saída das figuras
OUT_DIR = "const_EST_view"
os.makedirs(OUT_DIR, exist_ok=True)


# ============================================================
# Construtivo EST COM LOG por passo (simplificado)
# (sem precedências, só C_último + s_ij)
# ============================================================

def greedy_est_with_log(inst):
    """
    Constrói solução via EST simplificado e registra, em cada passo:
      - sequência parcial
      - tempos b, c dos jobs já escalonados
      - EST dos jobs ainda não escalonados
    """
    n = inst.n
    unscheduled = set(range(n))
    scheduled = []
    b = {}   # start times
    c = {}   # completion times

    last_job = None
    last_C = 0

    log = []
    step = 0

    while unscheduled:
        step += 1

        # 1) Calcula EST para cada job não escalonado
        est = {}
        for j in unscheduled:
            if last_job is None:
                est_j = 0.0
            else:
                est_j = last_C + inst.S[last_job][j]
            est[j] = est_j

        # 2) Escolhe job com menor EST
        chosen = min(est, key=est.get)
        chosen_est = est[chosen]

        # 3) Define b_j, c_j
        b_j = chosen_est
        c_j = b_j + inst.p[chosen]

        b[chosen] = b_j
        c[chosen] = c_j

        scheduled.append(chosen)
        unscheduled.remove(chosen)

        last_job = chosen
        last_C = c_j

        # EST dos que ainda faltam
        est_remaining = {j: est[j] for j in unscheduled}

        # monta um "res" parcial no formato esperado pelo gantt
        res_step = build_partial_res(inst, scheduled, b, c)

        log.append({
            "step": step,
            "chosen_job": chosen,
            "res": res_step,
            "est": est_remaining
        })

    return log


def build_partial_res(inst, scheduled, b, c):
    """
    Constrói um dicionário de solução parcial no formato:
      - sequence_normalized
      - b, c como listas indexadas por job
      - C_max
      - feasible = True
    """
    n = inst.n
    b_list = [0.0] * n
    c_list = [0.0] * n

    for j in scheduled:
        b_list[j] = b[j]
        c_list[j] = c[j]

    C_max = max(c_list[j] for j in scheduled) if scheduled else 0.0

    res = {
        "sequence_normalized": scheduled.copy(),
        "b": b_list,
        "c": c_list,
        "C_max": C_max,
        "feasible": True
    }
    return res


# ============================================================
# Gantt no MESMO ESTILO do seu plot_gantt + tabela de EST
# com opção de salvar em arquivo
# ============================================================

def plot_gantt_with_est(inst, res, est_dict, title=None, filename=None):
    """
    Versão 'estendida' do plot_gantt:
      - em cima: gantt (um job por linha, setas, [b,c])
      - embaixo: tabela com EST dos jobs ainda não escalonados

    Se filename for fornecido, salva a figura em vez de dar plt.show().
    """
    if not res.get("feasible", False):
        print("Solução não é factível.")
        return

    seq = res["sequence_normalized"]
    b = res["b"]
    c = res["c"]

    # figura com 2 linhas: (gantt, tabela)
    fig, (ax_gantt, ax_table) = plt.subplots(
        nrows=2, ncols=1,
        figsize=(12, max(5, len(seq) * 0.6 + 2)),
        gridspec_kw={"height_ratios": [3, 1]}
    )

    # Título geral da figura (suptitle) – evita brigar com tight_layout
    if title is None:
        title = f"Gantt da solução — C_max = {res['C_max']:.1f}"
    fig.suptitle(title, fontsize=14, y=0.97)

    # ---------------------------
    # Gantt (igual ao seu estilo)
    # ---------------------------
    yticks = []
    ylabels = []

    for idx, j in enumerate(seq):
        y = idx
        yticks.append(y)
        ylabels.append(f"Job {j+1}")  # 1-based na label

        start = b[j]
        duration = inst.p[j]

        # barra horizontal do job
        ax_gantt.barh(y, duration, left=start, height=0.4)

        # marcadores de início/fim
        ax_gantt.vlines(start, y - 0.2, y + 0.2, linewidth=1)
        ax_gantt.vlines(c[j], y - 0.2, y + 0.2, linewidth=1)

        # rótulo [start, end]
        ax_gantt.text(
            (start + c[j]) / 2, y,
            f"[{start:.1f}, {c[j]:.1f}]",
            ha="center", va="center"
        )

    # setas conectando jobs consecutivos
    for r in range(1, len(seq)):
        i = seq[r - 1]
        j = seq[r]
        gap = b[j] - c[i]

        ax_gantt.annotate(
            "",
            xy=(b[j], r),         # ponta da seta
            xytext=(c[i], r - 1), # base da seta
            arrowprops=dict(arrowstyle="->", lw=1)
        )

        mid_x = (c[i] + b[j]) / 2
        mid_y = r - 0.5
        ax_gantt.text(
            mid_x, mid_y, f"{gap:.1f}",
            ha="center", va="center",
            bbox=dict(facecolor='white', edgecolor='none', alpha=0.7)
        )

    ax_gantt.set_yticks(yticks)
    ax_gantt.set_yticklabels(ylabels)
    ax_gantt.set_xlabel("Tempo")
    ax_gantt.grid(True, alpha=0.3)

    # deixa um pouco de espaço à direita
    if seq:
        max_time = max(c[j] for j in seq) + 2
    else:
        max_time = 10
    ax_gantt.set_xlim(0, max_time)

    # ---------------------------
    # Tabela com EST
    # ---------------------------
    ax_table.axis("off")

    if est_dict:
        table_data = []
        for j, val in sorted(est_dict.items()):
            table_data.append([f"Job {j+1}", f"{val:.1f}"])

        col_labels = ["Job", "EST"]

        table = ax_table.table(
            cellText=table_data,
            colLabels=col_labels,
            loc="center",
            cellLoc="center",   # centraliza conteúdo das células
            colLoc="center"     # centraliza cabeçalhos
        )
        table.scale(1, 1.4)

        # Título da tabela, com padding extra pra não encostar no Gantt
        ax_table.set_title(
            "EST dos jobs ainda não escalonados",
            pad=20, fontsize=11
        )
    else:
        ax_table.text(
            0.5, 0.5,
            "Todos os jobs já foram escalonados.",
            ha="center", va="center", fontsize=12
        )

    # Espaçamento entre subplots + espaço pro suptitle
    fig.subplots_adjust(hspace=0.5)
    plt.tight_layout(rect=[0, 0, 1, 0.93])

    # Salva ou mostra
    if filename is not None:
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"Figura salva em: {filename}")
    else:
        plt.show()

# ============================================================
# Execução: gera uma figura .png por passo na pasta const_EST_view
# ============================================================

if __name__ == "__main__":
    log = greedy_est_with_log(inst)

    for info in log:
        step = info["step"]
        res_step = info["res"]
        est_step = info["est"]

        filename = os.path.join(OUT_DIR, f"est_step_{step}.png")

        print(f"Gerando passo {step}: seq parcial = {res_step['sequence_normalized']}, EST = {est_step}")
        plot_gantt_with_est(
            inst,
            res_step,
            est_step,
            title=f"Construtivo EST – Passo {step} (C_max parcial = {res_step['C_max']:.1f})",
            filename=filename
        )
