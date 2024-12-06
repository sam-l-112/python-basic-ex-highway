def calculate_repayment(c_name, a_name, b_name, c_total_money, debt_a, debt_b):
    # 總欠款
    total_debt = debt_a + debt_b
    print(f"\n{c_name}欠{a_name} {debt_a}元，欠{b_name} {debt_b}元，共計: {total_debt}元")

    # 如果C的錢不足以還清
    if c_total_money < total_debt:
        print(f"{c_name}只有 {c_total_money} 元，無法完全清還。")

        # 根據欠款比例分配還款
        total_ratio = debt_a + debt_b
        repayment_a = c_total_money * (debt_a / total_ratio)
        repayment_b = c_total_money * (debt_b / total_ratio)

        # 計算剩餘欠款
        remaining_a = debt_a - repayment_a
        remaining_b = debt_b - repayment_b

        print(f"{c_name}分別還給{a_name}: {repayment_a:.2f}元，還給{b_name}: {repayment_b:.2f}元")
        print(f"{a_name}還差: {remaining_a:.2f}元，{b_name}還差: {remaining_b:.2f}元")
    else:
        # C的錢足夠還清所有欠款
        repayment_a = debt_a
        repayment_b = debt_b
        extra = c_total_money - total_debt

        print(f"{c_name}分別還清：{a_name}: {repayment_a:.2f}元，{b_name}: {repayment_b:.2f}元")
        print(f"{c_name}還完後剩餘: {extra:.2f}元")

# 主程式
print("請輸入以下資料：")
a_name = input("請輸入A的名字: ")
b_name = input("請輸入B的名字: ")
c_name = input("請輸入C的名字: ")
c_total_money = float(input(f"請輸入{c_name}目前的總金額: "))
debt_a = float(input(f"請輸入{c_name}欠{a_name}的金額: "))
debt_b = float(input(f"請輸入{c_name}欠{b_name}的金額: "))

# 計算
calculate_repayment(c_name, a_name, b_name, c_total_money, debt_a, debt_b)
