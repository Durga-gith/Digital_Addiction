import matplotlib.pyplot as plt

def generate_full_risk_chart(dates, risks, future_labels, future_risks, path):
    plt.figure(figsize=(6, 4))

    plt.plot(dates, risks, marker="o", label="Historical Risk")

    all_labels = dates + future_labels
    future_x = list(range(len(dates) - 1, len(all_labels)))
    plt.plot(
        future_x,
        [risks[-1]] + future_risks,
        linestyle="dashed",
        marker="o",
        label="Predicted Risk"
    )

    plt.xticks(range(len(all_labels)), all_labels, rotation=30)
    plt.ylim(0, 1)
    plt.ylabel("Risk Score")
    plt.title("Digital Addiction Risk Trend")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()