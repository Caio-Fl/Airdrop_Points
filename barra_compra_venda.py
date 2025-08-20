def barra_compra_venda(valor, valor_medido,limite=100):
    import matplotlib.pyplot as plt
    valor = max(-limite, min(limite, valor))  # limitar o valor

    fig, ax = plt.subplots(figsize=(4.5, 0.12))

    # Fundo transparente
    #fig.patch.set_alpha(0.0)  # fundo da figura
    #ax.patch.set_alpha(0.0)   # fundo dos eixos
    fig.patch.set_facecolor('#111827'),
    # Barra compra (esquerda, valores negativos)
    if valor < 0:
        ax.barh(0, valor, color='green', height=0.2)
    # Barra venda (direita, valores positivos)
    elif valor > 0:
        ax.barh(0, valor, color='red', height=0.2)
    else:
        ax.barh(0, 0.01, color='gray', height=0.2)  # visual neutro

    # Linha central (neutro)
    ax.axvline(0, color="black", linewidth=1)

    # Texto indicativo
    ax.text(-limite * 0.9, 0.25, "← Buy", color='green', fontsize=8, family='Space Grotesk, sans-serif')
    ax.text(limite * 0.9, 0.25, "Sell →", color='red', fontsize=8, ha='right', family='Space Grotesk, sans-serif')
    if (valor_medido < (-50)):
        ax.text(0, 0.6, "⚠️ ALERT: Implied APY very Low, Verify if there is no Problem with Protocol", ha='center', fontsize=5, weight='bold', color='orange', family='Space Grotesk, sans-serif')
    elif ((-50) <= valor_medido < (-5)):
        ax.text(0, 0.6, "⚠️ ALERT: EXTREME BUY", ha='center', fontsize=6, weight='bold', color='green', family='Space Grotesk, sans-serif')
    elif (valor_medido > 105):
        ax.text(0, 0.6, "⚠️ ALERT: EXTREME SELL", ha='center', fontsize=6, weight='bold', color='red', family='Space Grotesk, sans-serif')
    else:
        ax.text(0, 0.6, f"Trade Force: {abs(round(valor,1))}", ha='center', fontsize=8, weight='bold', color='white', family='Space Grotesk, sans-serif')

    # Limites e ocultar eixos
    ax.set_xlim(-limite, limite)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.axis('off')
    plt.tight_layout()
    force = (round(valor,1))

    return fig, force
