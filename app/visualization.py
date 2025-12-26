import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch


def plot_index_map(index, index_name, cmap, legend):
    """
    Wyświetla mapę indeksu z legendą interpretacyjną
    """
    fig, ax = plt.subplots(figsize=(7, 7))

    im = ax.imshow(index, cmap=cmap, vmin=-1, vmax=1)
    ax.set_title(index_name)
    ax.axis("off")

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.set_label(index_name)

    # Legenda opisowa
    legend_patches = []
    for lo, hi, desc in legend:
        color = plt.cm.get_cmap(cmap)((lo + 1) / 2)
        legend_patches.append(
            Patch(color=color, label=f"{lo} – {hi}: {desc}")
        )

    ax.legend(
        handles=legend_patches,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        fontsize=8,
        ncol=1,
        frameon=True,
    )


    return fig


def plot_histogram(index, index_name):
    """
    Histogram wartości indeksu
    """
    fig, ax = plt.subplots(figsize=(6, 4))

    valid = index[~np.isnan(index)]
    ax.hist(valid, bins=50)

    ax.set_title(f"Histogram – {index_name}")
    ax.set_xlabel(index_name)
    ax.set_ylabel("Liczba pikseli")

    return fig
