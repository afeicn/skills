import argparse
import json

def get_comprehensive_tax(taxable_income):
    if taxable_income <= 0:
        return 0, 0, 0
    brackets = [
        (36000, 0.03, 0),
        (144000, 0.10, 2520),
        (300000, 0.20, 16920),
        (420000, 0.25, 31920),
        (660000, 0.30, 52920),
        (960000, 0.35, 85920),
        (float('inf'), 0.45, 181920)
    ]
    for limit, rate, deduction in brackets:
        if taxable_income <= limit:
            return taxable_income * rate - deduction, rate, deduction

def get_bonus_tax(bonus):
    if bonus <= 0:
        return 0, 0, 0
    monthly_bonus = bonus / 12.0
    brackets = [
        (3000, 0.03, 0),
        (12000, 0.10, 210),
        (25000, 0.20, 1410),
        (35000, 0.25, 2660),
        (55000, 0.30, 4410),
        (80000, 0.35, 7160),
        (float('inf'), 0.45, 15160)
    ]
    for limit, rate, deduction in brackets:
        if monthly_bonus <= limit:
            return bonus * rate - deduction, rate, deduction

def main():
    parser = argparse.ArgumentParser(description="Calculate tax settlement options")
    parser.add_argument("--income", type=float, required=True, help="综合所得收入额")
    parser.add_argument("--bonus", type=float, required=True, help="全年一次性奖金")
    parser.add_argument("--tax_free", type=float, default=60000, help="减除费用 (默认 60000)")
    parser.add_argument("--deductions", type=float, required=True, help="专项扣除+专项附加扣除+其他扣除等各项扣除合计")
    parser.add_argument("--paid_tax", type=float, default=0, help="已预缴税额")
    args = parser.parse_args()

    # Scenario 1: Separate
    comp_taxable_1 = max(0, args.income - args.tax_free - args.deductions)
    comp_tax_1, comp_rate_1, _ = get_comprehensive_tax(comp_taxable_1)
    bonus_tax_1, bonus_rate_1, _ = get_bonus_tax(args.bonus)
    total_tax_1 = comp_tax_1 + bonus_tax_1

    # Scenario 2: Merged
    comp_taxable_2 = max(0, args.income + args.bonus - args.tax_free - args.deductions)
    comp_tax_2, comp_rate_2, _ = get_comprehensive_tax(comp_taxable_2)
    total_tax_2 = comp_tax_2

    best_scenario = 1 if total_tax_1 <= total_tax_2 else 2
    min_tax = min(total_tax_1, total_tax_2)
    diff = abs(total_tax_1 - total_tax_2)
    
    final_payment = min_tax - args.paid_tax

    result = {
        "Scenario1_Separate": {
            "Comprehensive_Taxable": comp_taxable_1,
            "Comprehensive_Tax": comp_tax_1,
            "Comprehensive_Rate": comp_rate_1,
            "Bonus_Tax": bonus_tax_1,
            "Bonus_Rate": bonus_rate_1,
            "Total_Tax": total_tax_1
        },
        "Scenario2_Merged": {
            "Comprehensive_Taxable": comp_taxable_2,
            "Comprehensive_Tax": comp_tax_2,
            "Comprehensive_Rate": comp_rate_2,
            "Total_Tax": total_tax_2
        },
        "Best_Scenario": "单独计税" if best_scenario == 1 else "全部并入综合所得",
        "Tax_Difference": diff,
        "Final_Calculated_Tax": min_tax,
        "Paid_Tax": args.paid_tax,
        "Settlement_Amount": final_payment, # Negative means refund (退税), Positive means pay (补税)
        "Action": "应退税" if final_payment < 0 else "应补税"
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
