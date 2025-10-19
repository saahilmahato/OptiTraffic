import argparse
from pathlib import Path
import json
import pandas as pd
import numpy as np
from scipy import stats
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')

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


def calculate_descriptive_stats(data: np.ndarray, label: str) -> dict:
    """Calculate descriptive statistics for a dataset."""
    stats_dict = {
        'label': label,
        'n': len(data),
        'mean': np.mean(data),
        'std': np.std(data, ddof=1),
        'variance': np.var(data, ddof=1),
        'min': np.min(data),
        'max': np.max(data),
        'median': np.median(data),
        'q1': np.percentile(data, 25),
        'q3': np.percentile(data, 75)
    }
    return stats_dict


def print_descriptive_stats(stats_dict: dict):
    """Print descriptive statistics in a formatted manner."""
    print(f"\n{'='*60}")
    print(f"Descriptive Statistics: {stats_dict['label']}")
    print(f"{'='*60}")
    print(f"Sample Size (n):        {stats_dict['n']}")
    print(f"Mean:                   {stats_dict['mean']:.6e}")
    print(f"Standard Deviation:     {stats_dict['std']:.6e}")
    print(f"Variance:               {stats_dict['variance']:.6e}")
    print(f"Minimum:                {stats_dict['min']:.6e}")
    print(f"Maximum:                {stats_dict['max']:.6e}")
    print(f"Median:                 {stats_dict['median']:.6e}")
    print(f"Q1 (25th percentile):   {stats_dict['q1']:.6e}")
    print(f"Q3 (75th percentile):   {stats_dict['q3']:.6e}")


def test_normality(data: np.ndarray, label: str) -> bool:
    """Test for normality using Shapiro-Wilk test."""
    print(f"\n--- Normality Test: {label} ---")
    statistic, p_value = stats.shapiro(data)
    print(f"Shapiro-Wilk statistic: {statistic:.6e}")
    print(f"P-value:                {p_value:.6e}")
    
    is_normal = p_value > 0.05
    if is_normal:
        print(f"Result: Data appears normally distributed (p > 0.05)")
    else:
        print(f"Result: Data may not be normally distributed (p ≤ 0.05)")
    
    return is_normal


def test_equal_variance(data1: np.ndarray, data2: np.ndarray, label1: str, label2: str) -> bool:
    """Test for equal variances using Levene's test."""
    print(f"\n--- Equal Variance Test: {label1} vs {label2} ---")
    statistic, p_value = stats.levene(data1, data2)
    print(f"Levene's statistic:     {statistic:.6e}")
    print(f"P-value:                {p_value:.6e}")
    
    equal_var = p_value > 0.05
    if equal_var:
        print(f"Result: Variances are equal (p > 0.05)")
    else:
        print(f"Result: Variances are not equal (p ≤ 0.05)")
    
    return equal_var


def perform_t_test(data1: np.ndarray, data2: np.ndarray, 
                   label1: str, label2: str, 
                   alternative: str, equal_var: bool) -> dict:
    """
    Perform independent samples t-test.
    
    Args:
        data1: First dataset (e.g., Fixed-time)
        data2: Second dataset (e.g., MARL)
        label1: Label for first dataset
        label2: Label for second dataset
        alternative: 'less' or 'greater' for one-tailed test
        equal_var: Whether to assume equal variances
    """
    print(f"\n{'='*60}")
    print(f"Hypothesis Test: {label1} vs {label2}")
    print(f"{'='*60}")
    
    # Perform t-test
    if equal_var:
        print("Using: Standard independent samples t-test (equal variances)")
        t_stat, p_value = stats.ttest_ind(data1, data2, alternative=alternative, equal_var=True)
    else:
        print("Using: Welch's t-test (unequal variances)")
        t_stat, p_value = stats.ttest_ind(data1, data2, alternative=alternative, equal_var=False)
    
    # Calculate degrees of freedom
    n1, n2 = len(data1), len(data2)
    if equal_var:
        df = n1 + n2 - 2
    else:
        # Welch-Satterthwaite equation
        s1, s2 = np.var(data1, ddof=1), np.var(data2, ddof=1)
        df = ((s1/n1 + s2/n2)**2) / ((s1/n1)**2/(n1-1) + (s2/n2)**2/(n2-1))
    
    # Calculate effect size (Cohen's d)
    pooled_std = np.sqrt(((n1-1)*np.var(data1, ddof=1) + (n2-1)*np.var(data2, ddof=1)) / (n1+n2-2))
    cohens_d = (np.mean(data1) - np.mean(data2)) / pooled_std
    
    print(f"\nTest Statistics:")
    print(f"t-statistic:            {t_stat:.6e}")
    print(f"Degrees of freedom:     {df:.2f}")
    print(f"P-value (one-tailed):   {p_value:.6e}")
    print(f"Cohen's d (effect size): {cohens_d:.6e}")
    
    # Interpret effect size
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        effect = "negligible"
    elif abs_d < 0.5:
        effect = "small"
    elif abs_d < 0.8:
        effect = "medium"
    else:
        effect = "large"
    print(f"Effect size interpretation: {effect}")
    
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'df': df,
        'cohens_d': cohens_d,
        'effect_size': effect
    }


def print_hypothesis_and_conclusion(metric: str, fixed_mean: float, marl_mean: float, 
                                   test_result: dict, alpha: float = 0.05):
    """Print hypothesis statements and conclusion."""
    print(f"\n{'='*60}")
    print(f"HYPOTHESIS TEST CONCLUSION: {metric}")
    print(f"{'='*60}")
    
    # State hypotheses
    if metric == "Vehicles Passed":
        print(f"H₀: μ_MARL = μ_Fixed (no difference in vehicles passed)")
        print(f"H₁: μ_MARL > μ_Fixed (MARL passes more vehicles)")
        direction = "greater"
    else:  # Wait Time
        print(f"H₀: μ_MARL = μ_Fixed (no difference in wait time)")
        print(f"H₁: μ_MARL < μ_Fixed (MARL has lower wait time)")
        direction = "less"
    
    print(f"\nSignificance level (α): {alpha}")
    print(f"\nObserved means:")
    print(f"  Fixed-time: {fixed_mean:.6e}")
    print(f"  MARL:       {marl_mean:.6e}")
    print(f"  Difference: {abs(marl_mean - fixed_mean):.6e}")
    
    # Decision
    print(f"\nDecision:")
    is_significant = test_result['p_value'] < alpha
    
    if is_significant:
        print(f"✓ REJECT H₀ (p = {test_result['p_value']:.6e} < {alpha})")
        print(f"\nConclusion:")
        if metric == "Vehicles Passed":
            print(f"  The MARL controller passes significantly MORE vehicles")
            print(f"  than the fixed-time controller (p < {alpha}).")
        else:
            print(f"  The MARL controller has significantly LOWER wait time")
            print(f"  than the fixed-time controller (p < {alpha}).")
        print(f"  The effect size is {test_result['effect_size']} (Cohen's d = {test_result['cohens_d']:.6e}).")
        print(f"  This difference is statistically significant and practically meaningful.")
    else:
        print(f"✗ FAIL TO REJECT H₀ (p = {test_result['p_value']:.6e} ≥ {alpha})")
        print(f"\nConclusion:")
        print(f"  There is insufficient evidence to conclude that MARL")
        print(f"  performs differently than the fixed-time controller")
        print(f"  for {metric.lower()} (p ≥ {alpha}).")


# Main driver
def main():
    parser = argparse.ArgumentParser(description="Statistical Hypothesis Testing for Traffic Controllers")
    parser.add_argument('--fixed', type=Path, default=Path('results/fixed.json'))
    parser.add_argument('--marl', type=Path, default=Path('results/marl.json'))
    parser.add_argument('--alpha', type=float, default=0.05, help='Significance level')
    args = parser.parse_args()

    # Load data
    df_fixed = load_data(args.fixed)
    df_marl = load_data(args.marl)
    
    if df_fixed.empty or df_marl.empty:
        logging.error("Failed to load data. Exiting.")
        return
    
    print("\n" + "="*60)
    print("STATISTICAL HYPOTHESIS TESTING")
    print("Traffic Controller Comparison: Fixed-Time vs MARL")
    print("="*60)
    
    # Extract data
    vehicles_fixed = df_fixed['vehicles_passed'].values
    vehicles_marl = df_marl['vehicles_passed'].values
    wait_fixed = df_fixed['wait_time'].values
    wait_marl = df_marl['wait_time'].values
    
    # ========== VEHICLES PASSED ANALYSIS ==========
    print("\n\n" + "#"*60)
    print("# ANALYSIS 1: VEHICLES PASSED")
    print("#"*60)
    
    # Descriptive statistics
    stats_veh_fixed = calculate_descriptive_stats(vehicles_fixed, "Fixed-Time Controller - Vehicles Passed")
    stats_veh_marl = calculate_descriptive_stats(vehicles_marl, "MARL Controller - Vehicles Passed")
    print_descriptive_stats(stats_veh_fixed)
    print_descriptive_stats(stats_veh_marl)
    
    # Check assumptions
    print("\n" + "-"*60)
    print("CHECKING ASSUMPTIONS")
    print("-"*60)
    normal_veh_fixed = test_normality(vehicles_fixed, "Fixed-Time Vehicles")
    normal_veh_marl = test_normality(vehicles_marl, "MARL Vehicles")
    equal_var_veh = test_equal_variance(vehicles_fixed, vehicles_marl, 
                                        "Fixed-Time Vehicles", "MARL Vehicles")
    
    # Hypothesis test (one-tailed: MARL > Fixed)
    test_veh = perform_t_test(vehicles_marl, vehicles_fixed, 
                              "MARL", "Fixed-Time",
                              alternative='greater', 
                              equal_var=equal_var_veh)
    
    print_hypothesis_and_conclusion("Vehicles Passed", 
                                   stats_veh_fixed['mean'], 
                                   stats_veh_marl['mean'],
                                   test_veh, 
                                   args.alpha)
    
    # ========== WAIT TIME ANALYSIS ==========
    print("\n\n" + "#"*60)
    print("# ANALYSIS 2: WAIT TIME")
    print("#"*60)
    
    # Descriptive statistics
    stats_wait_fixed = calculate_descriptive_stats(wait_fixed, "Fixed-Time Controller - Wait Time")
    stats_wait_marl = calculate_descriptive_stats(wait_marl, "MARL Controller - Wait Time")
    print_descriptive_stats(stats_wait_fixed)
    print_descriptive_stats(stats_wait_marl)
    
    # Check assumptions
    print("\n" + "-"*60)
    print("CHECKING ASSUMPTIONS")
    print("-"*60)
    normal_wait_fixed = test_normality(wait_fixed, "Fixed-Time Wait Time")
    normal_wait_marl = test_normality(wait_marl, "MARL Wait Time")
    equal_var_wait = test_equal_variance(wait_fixed, wait_marl,
                                        "Fixed-Time Wait Time", "MARL Wait Time")
    
    # Hypothesis test (one-tailed: MARL < Fixed)
    test_wait = perform_t_test(wait_marl, wait_fixed,
                              "MARL", "Fixed-Time", 
                              alternative='less',
                              equal_var=equal_var_wait)
    
    print_hypothesis_and_conclusion("Wait Time",
                                   stats_wait_fixed['mean'],
                                   stats_wait_marl['mean'],
                                   test_wait,
                                   args.alpha)
    
    # ========== OVERALL SUMMARY ==========
    print("\n\n" + "="*60)
    print("OVERALL SUMMARY")
    print("="*60)
    
    veh_significant = test_veh['p_value'] < args.alpha
    wait_significant = test_wait['p_value'] < args.alpha
    
    print(f"\nVehicles Passed: {'SIGNIFICANT' if veh_significant else 'NOT SIGNIFICANT'}")
    print(f"  - MARL mean: {stats_veh_marl['mean']:.2f}")
    print(f"  - Fixed mean: {stats_veh_fixed['mean']:.2f}")
    print(f"  - Improvement: {((stats_veh_marl['mean'] - stats_veh_fixed['mean']) / stats_veh_fixed['mean'] * 100):.2f}%")
    print(f"  - p-value: {test_veh['p_value']:.6e}")
    
    print(f"\nWait Time: {'SIGNIFICANT' if wait_significant else 'NOT SIGNIFICANT'}")
    print(f"  - MARL mean: {stats_wait_marl['mean']:.2f}s")
    print(f"  - Fixed mean: {stats_wait_fixed['mean']:.2f}s")
    print(f"  - Reduction: {((stats_wait_fixed['mean'] - stats_wait_marl['mean']) / stats_wait_fixed['mean'] * 100):.2f}%")
    print(f"  - p-value: {test_wait['p_value']:.6e}")
    
    print(f"\n{'='*60}")
    print("FINAL CONCLUSION")
    print("="*60)
    
    if veh_significant and wait_significant:
        print("✓ The MARL controller demonstrates STATISTICALLY SIGNIFICANT")
        print("  improvements over the fixed-time controller in BOTH metrics:")
        print("  - Higher vehicle throughput")
        print("  - Lower wait times")
        print("\n  The results strongly support the adoption of MARL for")
        print("  traffic signal control.")
    elif veh_significant or wait_significant:
        print("⚠ The MARL controller shows mixed results:")
        if veh_significant:
            print("  - SIGNIFICANT improvement in vehicle throughput")
            print("  - No significant difference in wait times")
        else:
            print("  - No significant difference in vehicle throughput")
            print("  - SIGNIFICANT improvement in wait times")
        print("\n  Further investigation may be needed.")
    else:
        print("✗ The MARL controller does NOT show statistically significant")
        print("  improvements over the fixed-time controller in either metric")
        print("  at the α = {} significance level.".format(args.alpha))
    
    print("="*60 + "\n")


if __name__ == '__main__':
    main()