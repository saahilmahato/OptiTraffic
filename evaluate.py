import argparse
from pathlib import Path
import json
import logging
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from scipy.stats import shapiro, levene, ttest_ind, mannwhitneyu, bootstrap
from statsmodels.stats.power import TTestIndPower

# Configure logging
def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s"
    )

# Load JSON data
def load_data(file_path: Path) -> pd.DataFrame:
    """Load JSON results into a pandas DataFrame."""
    if not file_path.exists():
        logging.error(f"File not found: {file_path}")
        return pd.DataFrame()
    try:
        with file_path.open("r") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        logging.info(f"Loaded {len(df)} records from {file_path.name}")
        return df
    except json.JSONDecodeError:
        logging.error(f"Invalid JSON in file: {file_path}")
        return pd.DataFrame()

# Cohen's d effect size
def cohens_d(a: np.ndarray, b: np.ndarray) -> float:
    pooled_var = (np.var(a, ddof=1) + np.var(b, ddof=1)) / 2
    return (np.mean(b) - np.mean(a)) / np.sqrt(pooled_var)

# Format p-values in scientific notation
def fmt_p(p: float) -> str:
    return f"{p:.2e}" if p is not None else "nan"

# Perform statistical tests and return summary
def run_tests(df_fixed: pd.DataFrame, df_marl: pd.DataFrame, alpha: float = 0.05) -> dict:
    summary = {}
    power_tool = TTestIndPower()
    for metric in ["vehicles_passed", "wait_time"]:
        a = df_fixed[metric].values
        b = df_marl[metric].values
        logging.info(f"=== Testing metric: {metric} ===")

        # Descriptive stats
        summary[metric] = {'fixed_mean': np.mean(a), 'marl_mean': np.mean(b)}
        logging.info(f"Mean Fixed {metric}: {summary[metric]['fixed_mean']:.2f}")
        logging.info(f"Mean MARL  {metric}: {summary[metric]['marl_mean']:.2f}")

        # Normality
        for label, data in [("Fixed", a), ("MARL", b)]:
            _, p = shapiro(data)
            logging.info(f"{label} {metric} normality p-value: {fmt_p(p)}")

        # Variance homogeneity and t-test
        _, p_l = levene(a, b)
        equal_var = p_l > alpha
        t_stat, p_t = ttest_ind(a, b, equal_var=equal_var)
        summary[metric].update({'t_stat': t_stat, 'p_value': p_t})
        logging.info(f"Levene p={fmt_p(p_l)} equal_var={equal_var}")
        logging.info(f"t-test p-value: {fmt_p(p_t)}; t-statistic: {t_stat:.4f}")

        # Effect size
        d = cohens_d(a, b)
        summary[metric]['cohens_d'] = d
        logging.info(f"Cohen's d: {d:.4f}")

        # Mann-Whitney
        alt = 'two-sided' if metric == 'vehicles_passed' else 'greater'
        u_stat, p_u = mannwhitneyu(a, b, alternative=alt)
        summary[metric].update({'u_stat': u_stat, 'u_p': p_u})
        logging.info(f"Mann-Whitney U p-value: {fmt_p(p_u)}; U-statistic: {u_stat:.4f}")

        # Bootstrap CI
        def mean_diff(x, y): return np.mean(y) - np.mean(x)
        bs = bootstrap((a, b), mean_diff, n_resamples=5000, random_state=42)
        ci = bs.confidence_interval
        summary[metric].update({'ci_low': ci.low, 'ci_high': ci.high})
        logging.info(f"Bootstrap 95% CI: [{ci.low:.2f}, {ci.high:.2f}]")

        # Power analysis with robust fallback
        effect_size = abs(d)
        power = power_tool.power(effect_size=effect_size, nobs1=len(a), ratio=len(b)/len(a), alpha=alpha)
        # If power is NaN or unusually >0.9999, set to 1.0 (i.e., effectively 100% power)
        if np.isnan(power) or power > 0.9999:
            logging.info(f"Effect size {effect_size:.4f} leads to power ~1.0; setting power=1.0")
            power = 1.0
        summary[metric]['power'] = power
        logging.info(f"Statistical power: {fmt_p(power)}")

    # Decide winner
    vp, wt = summary['vehicles_passed'], summary['wait_time']
    if vp['p_value'] < alpha and wt['p_value'] < alpha and vp['marl_mean'] > vp['fixed_mean'] and wt['marl_mean'] < wt['fixed_mean']:
        winner = 'MARL'
    elif vp['p_value'] < alpha and vp['marl_mean'] > vp['fixed_mean']:
        winner = 'Vehicles Passed wins'
    elif wt['p_value'] < alpha and wt['marl_mean'] < wt['fixed_mean']:
        winner = 'Wait Time wins'
    else:
        winner = 'No clear winner'
    summary['overall_winner'] = winner
    logging.info(f"Overall winner: {winner}")
    return summary

# Plotting functions
def plot_boxplots(df_fixed: pd.DataFrame, df_marl: pd.DataFrame, out_dir: Path):
    df_fixed['method'] = 'Fixed'
    df_marl['method'] = 'MARL'
    df = pd.concat([df_fixed, df_marl], ignore_index=True)

    fig, axes = plt.subplots(2, 1, figsize=(8, 10))  # 2 rows, 1 column
    for ax, metric in zip(axes, ['vehicles_passed', 'wait_time']):
        sns.boxplot(x='method', y=metric, data=df, ax=ax)
        ax.set_title(f"{metric.replace('_', ' ').title()} by Method")

    fig.tight_layout()
    fig.savefig(out_dir / 'boxplots.png')
    plt.close(fig)



def plot_histograms(df_fixed: pd.DataFrame, df_marl: pd.DataFrame, out_dir: Path):
    fig, axes = plt.subplots(4, 1, figsize=(8, 16))  # 4 rows, 1 column

    sns.histplot(df_fixed['vehicles_passed'], kde=True, ax=axes[0])
    axes[0].set_title('Fixed - Vehicles Passed')

    sns.histplot(df_marl['vehicles_passed'], kde=True, ax=axes[1])
    axes[1].set_title('MARL - Vehicles Passed')

    sns.histplot(df_fixed['wait_time'], kde=True, ax=axes[2])
    axes[2].set_title('Fixed - Wait Time')

    sns.histplot(df_marl['wait_time'], kde=True, ax=axes[3])
    axes[3].set_title('MARL - Wait Time')

    fig.tight_layout()
    fig.savefig(out_dir / 'histograms.png')
    plt.close(fig)


# Generate PDF report
def generate_pdf_report(summary: dict, out_dir: Path):
    pdf_path = out_dir / 'detailed_report.pdf'
    with PdfPages(pdf_path) as pdf:
        # Text summary page
        fig = plt.figure(figsize=(8, 10))
        fig.clf()
        txt = []
        txt.append('Detailed Statistical Report')
        txt.append('==========================')
        for metric in ['vehicles_passed', 'wait_time']:
            data = summary[metric]
            txt.append(f"\nMetric: {metric}")
            txt.append(f" Fixed mean: {data['fixed_mean']:.2f}")
            txt.append(f" MARL mean: {data['marl_mean']:.2f}")
            txt.append(f" p-value: {fmt_p(data['p_value'])}")
            txt.append(f" Cohen's d: {data['cohens_d']:.2f}")
            txt.append(f" 95% CI: [{data['ci_low']:.2f}, {data['ci_high']:.2f}]")
            txt.append(f" Power: {fmt_p(data['power'])}\n")
        txt.append(f"Overall Winner: {summary['overall_winner']}")
        fig.text(0.01, 0.99, '\n'.join(txt), va='top', family='monospace')
        pdf.savefig(fig)
        plt.close(fig)

        # Add existing figures
        for fname in ['boxplots.png', 'histograms.png']:
            fig = plt.figure()
            img = plt.imread(out_dir / fname)
            plt.imshow(img)
            plt.axis('off')
            pdf.savefig(fig)
            plt.close(fig)
    logging.info(f"PDF report generated at {pdf_path}")

# Main driver
def main():
    configure_logging()
    parser = argparse.ArgumentParser(description="Enhanced Stats Pipeline")
    parser.add_argument('--fixed', type=Path, default=Path('results/fixed.json'))
    parser.add_argument('--marl', type=Path, default=Path('results/marl.json'))
    parser.add_argument('--out', type=Path, default=Path('results'))
    args = parser.parse_args()

    args.out.mkdir(exist_ok=True)

    df_fixed = load_data(args.fixed)
    df_marl = load_data(args.marl)
    if df_fixed.empty or df_marl.empty:
        logging.error("DataFrames empty. Exiting.")
        return

    summary = run_tests(df_fixed, df_marl)
    plot_boxplots(df_fixed, df_marl, args.out)
    plot_histograms(df_fixed, df_marl, args.out)
    generate_pdf_report(summary, args.out)

    logging.info("Analysis complete! Results, graphs, and PDF report are in %s", args.out)

if __name__ == '__main__':
    main()