#!/usr/bin/env python3
# verify_results.py - Validate Demi Agent's sales records

import json
from datetime import datetime
from collections import defaultdict


def verify_trace_log(trace_file="agent_trace.log"):
    """Parse trace log and verify all transactions are correct"""
    
    sales = []
    errors = []
    
    try:
        with open(trace_file, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as e:
                    errors.append(f"Line {line_num}: Invalid JSON - {e}")
                    continue
                
                # Extract tool_result events
                if record.get("event") == "tool_result" and record.get("action") == "log_sale":
                    result = record.get("result", {})
                    
                    # Validate: quantity * price = total
                    quantity = result.get("quantity", 0)
                    price = result.get("price", 0)
                    total = result.get("total", 0)
                    expected_total = quantity * price
                    
                    sale_record = {
                        "menu": result.get("menu"),
                        "quantity": quantity,
                        "price": price,
                        "total": total,
                        "timestamp": result.get("timestamp"),
                        "is_correct": total == expected_total,
                    }
                    
                    if total != expected_total:
                        errors.append(
                            f"Calculation error: {sale_record['menu']} - "
                            f"{quantity} x {price} = {total} (expected {expected_total})"
                        )
                    
                    sales.append(sale_record)
    
    except FileNotFoundError:
        print(f"❌ Trace file not found: {trace_file}")
        return
    
    # Summary Report
    print("\n" + "="*60)
    print("📊 DEMI AGENT - SALES VERIFICATION REPORT")
    print("="*60)
    
    if not sales:
        print("⚠️  No sales records found in trace log")
        return
    
    # Group by menu
    by_menu = defaultdict(lambda: {"qty": 0, "total": 0, "count": 0})
    for sale in sales:
        menu = sale["menu"]
        by_menu[menu]["qty"] += sale["quantity"]
        by_menu[menu]["total"] += sale["total"]
        by_menu[menu]["count"] += 1
    
    print(f"\n📝 Total Transactions: {len(sales)}")
    print(f"💰 Grand Total: {sum(s['total'] for s in sales)} บาท\n")
    
    print("Menu Breakdown:")
    print("-" * 60)
    print(f"{'Menu':<20} {'Count':<8} {'Qty':<8} {'Total ฿':<12}")
    print("-" * 60)
    for menu in sorted(by_menu.keys()):
        stats = by_menu[menu]
        print(
            f"{menu:<20} {stats['count']:<8} "
            f"{stats['qty']:<8} {stats['total']:<12.0f}"
        )
    print("-" * 60)
    
    print("\n✅ Detailed Transaction List:")
    print("-" * 60)
    for i, sale in enumerate(sales, 1):
        status = "✓" if sale["is_correct"] else "✗"
        print(
            f"{i}. {status} {sale['menu']:<15} x{sale['quantity']} "
            f"@ {sale['price']} บาท = {sale['total']} บาท"
        )
    print("-" * 60)
    
    if errors:
        print(f"\n⚠️  {len(errors)} Error(s) Found:")
        for error in errors:
            print(f"   • {error}")
    else:
        print("\n✅ All transactions are mathematically correct!")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    verify_trace_log()
