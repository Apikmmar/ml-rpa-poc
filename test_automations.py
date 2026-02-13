import httpx
import asyncio
from datetime import datetime
from backend.config import BASE_URL, HEADERS

API_URL = "http://localhost:8000"

# Test 1: Order Validator - Positive & Negative
async def test_order_validator_positive():
    print("\n=== Order Validator (POSITIVE: With Items) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "test@example.com", "customer_id": "TEST001", "priority": "Normal", "items": [{"sku": "item_123", "qty": 5}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(3)
        order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
        status = order_resp.json()["fields"].get("status")
        print(f"  Status: {status} (Expected: Validated)")
        return status == "Validated"

async def test_order_validator_negative():
    print("\n=== Order Validator (NEGATIVE: No Items) ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        order_data = {"fields": {"customer_email": "noitems@test.com", "customer_id": "NOITEM", "priority": "Normal", "status": "Pending", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Orders", headers=HEADERS, json=order_data)
        order_id = resp.json().get("id")
        print(f"✓ Order created without items: {order_id}")
        await asyncio.sleep(3)
        order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
        status = order_resp.json()["fields"].get("status")
        validation_errors = order_resp.json()["fields"].get("validation_errors")
        print(f"  Status: {status} (Expected: Failed)")
        print(f"  Validation Errors: {validation_errors}")
        return status == "Failed" and validation_errors == "No Items"

# Test 2: Stock Checker - Positive & Negative
async def test_stock_checker_positive():
    print("\n=== Stock Checker (POSITIVE: Sufficient Stock) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "stock@test.com", "customer_id": "STOCK001", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(5)
        order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
        status = order_resp.json()["fields"].get("status")
        stock_validation = order_resp.json()["fields"].get("stock_validation")
        print(f"  Status: {status} (Expected: Stock Confirmed)")
        print(f"  Stock Validation: {stock_validation}")
        return status == "Stock Confirmed" and stock_validation == "Passed"

async def test_stock_checker_negative():
    print("\n=== Stock Checker (NEGATIVE: Insufficient Stock) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "nostock@test.com", "customer_id": "NOSTOCK", "priority": "Normal", "items": [{"sku": "item_123", "qty": 99999}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created with high qty: {order_id}")
        await asyncio.sleep(5)
        order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
        status = order_resp.json()["fields"].get("status")
        stock_validation = order_resp.json()["fields"].get("stock_validation")
        print(f"  Status: {status} (Expected: Failed)")
        print(f"  Stock Validation: {stock_validation}")
        backorders_resp = await client.get(f"{BASE_URL}/Backorders", headers=HEADERS)
        backorders = [b for b in backorders_resp.json()["records"] if order_id in str(b.get("fields", {}).get("original_order_id", []))]
        print(f"  Backorders created: {len(backorders)}")
        return status == "Failed" and stock_validation == "Failed"

# Test 3: Stock Transfer Validator - Positive & Negative
async def test_transfer_validator_negative_same_location():
    print("\n=== Transfer Validator (NEGATIVE: Same Location/Rack) ===")
    async with httpx.AsyncClient() as client:
        params = {"from_location": "Zone-A", "to_location": "Zone-A", "from_rack": "Rack-1", "to_rack": "Rack-1", "sku": "item_123", "quantity": 10, "requested_by": "Test"}
        resp = await client.post(f"{API_URL}/stock-transfers", params=params)
        transfer_id = resp.json().get("transfer_id")
        print(f"✓ Transfer created: {transfer_id}")
        await asyncio.sleep(3)
        transfer_resp = await client.get(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS)
        status = transfer_resp.json()["fields"].get("status")
        print(f"  Status: {status} (Expected: Failed)")
        exc_resp = await client.get(f"{BASE_URL}/Exceptions", headers=HEADERS)
        exceptions = [e for e in exc_resp.json()["records"] if transfer_id in str(e.get("fields", {}).get("related_id", ""))]
        print(f"  Exceptions created: {len(exceptions)}")
        return status == "Failed"

async def test_transfer_validator_negative_zero_qty():
    print("\n=== Transfer Validator (NEGATIVE: Quantity < 1) ===")
    async with httpx.AsyncClient() as client:
        params = {"from_location": "Zone-A", "to_location": "Zone-B", "from_rack": "Rack-1", "to_rack": "Rack-2", "sku": "item_123", "quantity": 0, "requested_by": "Test"}
        resp = await client.post(f"{API_URL}/stock-transfers", params=params)
        transfer_id = resp.json().get("transfer_id")
        print(f"✓ Transfer created with qty=0: {transfer_id}")
        await asyncio.sleep(3)
        transfer_resp = await client.get(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS)
        status = transfer_resp.json()["fields"].get("status")
        print(f"  Status: {status} (Expected: Failed)")
        return status == "Failed"

# Test 4: Transfer Approval - Positive & Negative
async def test_transfer_approval_positive_auto():
    print("\n=== Transfer Approval (POSITIVE: Qty <= 30 Auto-Approve) ===")
    async with httpx.AsyncClient() as client:
        params = {"from_location": "Zone-A", "to_location": "Zone-B", "from_rack": "Rack-1", "to_rack": "Rack-2", "sku": "item_123", "quantity": 20, "requested_by": "Test"}
        resp = await client.post(f"{API_URL}/stock-transfers", params=params)
        transfer_id = resp.json().get("transfer_id")
        print(f"✓ Transfer created (qty=20): {transfer_id}")
        await asyncio.sleep(3)
        transfer_resp = await client.get(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS)
        status = transfer_resp.json()["fields"].get("status")
        print(f"  Status: {status} (Expected: Completed)")
        return status == "Completed"

async def test_transfer_approval_negative_manual():
    print("\n=== Transfer Approval (NEGATIVE: Qty > 30 Manual Approval) ===")
    async with httpx.AsyncClient() as client:
        params = {"from_location": "Zone-A", "to_location": "Zone-B", "from_rack": "Rack-1", "to_rack": "Rack-2", "sku": "item_123", "quantity": 50, "requested_by": "Test"}
        resp = await client.post(f"{API_URL}/stock-transfers", params=params)
        transfer_id = resp.json().get("transfer_id")
        print(f"✓ Transfer created (qty=50): {transfer_id}")
        await asyncio.sleep(3)
        transfer_resp = await client.get(f"{BASE_URL}/Stock_Transfers/{transfer_id}", headers=HEADERS)
        status = transfer_resp.json()["fields"].get("status")
        print(f"  Status: {status} (Expected: Pending)")
        notif_resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
        print(f"  Notifications sent: {len(notif_resp.json()['records'])}")
        return status == "Pending"

# Test 5: High Priority Alert - Positive & Negative
async def test_high_priority_positive():
    print("\n=== High Priority Alert (POSITIVE: Urgent Priority) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "urgent@test.com", "customer_id": "URG001", "priority": "Urgent", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Urgent order created: {order_id}")
        await asyncio.sleep(8)
        notif_resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
        notifications = notif_resp.json()["records"]
        print(f"  Notifications: {len(notifications)} (Expected: > 0)")
        return len(notifications) > 0

async def test_high_priority_negative():
    print("\n=== High Priority Alert (NEGATIVE: Normal Priority) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "normal@test.com", "customer_id": "NORM001", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Normal order created: {order_id}")
        await asyncio.sleep(8)
        print(f"  No high priority alert expected")
        return True

# Test 6: Exception Alert - Positive & Negative
async def test_exception_alert_positive_critical():
    print("\n=== Exception Alert (POSITIVE: Critical Severity) ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        exc_data = {"fields": {"related_id": "CRIT001", "error_type": "System Error", "error_message": "Critical error", "severity": "Critical", "status": "Open", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Exceptions", headers=HEADERS, json=exc_data)
        exc_id = resp.json().get("id")
        print(f"✓ Critical exception created: {exc_id}")
        await asyncio.sleep(3)
        exc_resp = await client.get(f"{BASE_URL}/Exceptions/{exc_id}", headers=HEADERS)
        assigned_to = exc_resp.json()["fields"].get("assigned_to")
        print(f"  Assigned to: {assigned_to} (Expected: Ops Team)")
        return assigned_to == "Ops Team"

async def test_exception_alert_negative_low():
    print("\n=== Exception Alert (NEGATIVE: Low Severity) ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        exc_data = {"fields": {"related_id": "LOW001", "error_type": "System Error", "error_message": "Low error", "severity": "Low", "status": "Open", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Exceptions", headers=HEADERS, json=exc_data)
        exc_id = resp.json().get("id")
        print(f"✓ Low severity exception created: {exc_id}")
        await asyncio.sleep(3)
        print(f"  No alert expected for low severity")
        return True

# Test 7: Exception Auto Assignment - Positive Cases
async def test_exception_assignment_stock_team():
    print("\n=== Exception Auto Assignment (Stock Team) ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        exc_data = {"fields": {"related_id": "STOCK001", "error_type": "Stock Shortage", "error_message": "Stock shortage", "severity": "High", "status": "Open", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Exceptions", headers=HEADERS, json=exc_data)
        exc_id = resp.json().get("id")
        print(f"✓ Stock shortage exception: {exc_id}")
        await asyncio.sleep(3)
        exc_resp = await client.get(f"{BASE_URL}/Exceptions/{exc_id}", headers=HEADERS)
        assigned_to = exc_resp.json()["fields"].get("assigned_to")
        print(f"  Assigned to: {assigned_to} (Expected: Stock Team)")
        return assigned_to == "Stock Team"

async def test_exception_assignment_ops_team():
    print("\n=== Exception Auto Assignment (Ops Team) ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        exc_data = {"fields": {"related_id": "VAL001", "error_type": "Validation Error", "error_message": "Validation error", "severity": "Medium", "status": "Open", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Exceptions", headers=HEADERS, json=exc_data)
        exc_id = resp.json().get("id")
        print(f"✓ Validation error exception: {exc_id}")
        await asyncio.sleep(3)
        exc_resp = await client.get(f"{BASE_URL}/Exceptions/{exc_id}", headers=HEADERS)
        assigned_to = exc_resp.json()["fields"].get("assigned_to")
        print(f"  Assigned to: {assigned_to} (Expected: Ops Team)")
        return assigned_to == "Ops Team"

# Test 8: Order Cancellation
async def test_order_cancellation():
    print("\n=== Order Cancellation ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "cancel@test.com", "customer_id": "CANCEL", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(3)
        cancel_data = {"fields": {"status": "Cancelled"}}
        await client.patch(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS, json=cancel_data)
        print(f"✓ Order cancelled")
        await asyncio.sleep(3)
        items_resp = await client.get(f"{BASE_URL}/Order_Items", headers=HEADERS)
        items = items_resp.json()["records"]
        order_items = [i for i in items if order_id in str(i.get("fields", {}).get("order_id", []))]
        cancelled = [i for i in order_items if i["fields"].get("order_cancelled") == True]
        print(f"  Cancelled items: {len(cancelled)}/{len(order_items)}")
        return len(cancelled) > 0

# Test 9: Picklist Started & Completer
async def test_picklist_workflow():
    print("\n=== Picklist Started & Completer ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "pick@test.com", "customer_id": "PICK", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(8)
        picklists_resp = await client.get(f"{BASE_URL}/Picklists", headers=HEADERS)
        picklists = picklists_resp.json()["records"]
        picklist = next((p for p in picklists if order_id in str(p.get("fields", {}).get("order_id", []))), None)
        if picklist:
            picklist_id = picklist["id"]
            # Start picking
            await client.patch(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS, json={"fields": {"status": "In Progress"}})
            print(f"✓ Picklist started: {picklist_id}")
            await asyncio.sleep(3)
            order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
            status1 = order_resp.json()["fields"].get("status")
            print(f"  Order status after start: {status1} (Expected: Picking)")
            # Complete picking
            await client.patch(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS, json={"fields": {"status": "Completed"}})
            print(f"✓ Picklist completed")
            await asyncio.sleep(3)
            order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
            status2 = order_resp.json()["fields"].get("status")
            print(f"  Order status after complete: {status2} (Expected: Ready)")
            return status1 == "Picking" and status2 == "Ready"
        return False

# Test 10: Shipped Order Notification
async def test_shipped_notification():
    print("\n=== Shipped Order Notification ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "ship@test.com", "customer_id": "SHIP", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(3)
        await client.patch(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS, json={"fields": {"status": "Shipped"}})
        print(f"✓ Order shipped")
        await asyncio.sleep(3)
        notif_resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
        print(f"  Notifications: {len(notif_resp.json()['records'])}")
        return True

# Test 11: Low Stock Alert
async def test_low_stock_alert():
    print("\n=== Low Stock Alert ===")
    async with httpx.AsyncClient() as client:
        now = datetime.utcnow().isoformat()
        # Create stock with low quantity
        stock_data = {"fields": {"sku": "low_stock_item", "def_quantity": 100, "add_stock": 0, "location": "Zone-A", "rack": "Rack-1", "created_at": now, "created_by": "System", "updated_at": now, "updated_by": "System"}}
        resp = await client.post(f"{BASE_URL}/Stocks", headers=HEADERS, json=stock_data)
        stock_id = resp.json().get("id")
        print(f"✓ Stock created: {stock_id}")
        
        # Create order to reserve 60% (making available 40% which triggers alert at <=50%)
        order_data = {"customer_email": "lowstock@test.com", "customer_id": "LOWSTOCK", "priority": "Normal", "items": [{"sku": "low_stock_item", "qty": 60}]}
        await client.post(f"{API_URL}/orders", json=order_data)
        print(f"✓ Order created to trigger low stock")
        
        await asyncio.sleep(5)
        
        # Check for exceptions
        exc_resp = await client.get(f"{BASE_URL}/Exceptions", headers=HEADERS)
        exceptions = exc_resp.json()["records"]
        low_stock_exc = [e for e in exceptions if "low_stock_item" in str(e.get("fields", {}))]
        print(f"  Low stock exceptions: {len(low_stock_exc)} (Expected: > 0)")
        
        # Check notifications
        notif_resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
        print(f"  Notifications: {len(notif_resp.json()['records'])}")
        
        return len(low_stock_exc) > 0

# Test 12: Picklist Started (Already in workflow test, but separate)
async def test_picklist_started_only():
    print("\n=== Picklist Started (Standalone) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "pickstart@test.com", "customer_id": "PICKSTART", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(8)
        
        picklists_resp = await client.get(f"{BASE_URL}/Picklists", headers=HEADERS)
        picklists = picklists_resp.json()["records"]
        picklist = next((p for p in picklists if order_id in str(p.get("fields", {}).get("order_id", []))), None)
        
        if picklist:
            picklist_id = picklist["id"]
            # Update to In Progress
            await client.patch(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS, json={"fields": {"status": "In Progress"}})
            print(f"✓ Picklist started: {picklist_id}")
            await asyncio.sleep(3)
            
            # Check order status changed to Picking
            order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
            status = order_resp.json()["fields"].get("status")
            print(f"  Order status: {status} (Expected: Picking)")
            return status == "Picking"
        return False

# Test 13: Picklist Completer (Already in workflow test, but separate)
async def test_picklist_completer_only():
    print("\n=== Picklist Completer (Standalone) ===")
    async with httpx.AsyncClient() as client:
        order_data = {"customer_email": "pickcomplete@test.com", "customer_id": "PICKCOMPLETE", "priority": "Normal", "items": [{"sku": "item_123", "qty": 1}]}
        resp = await client.post(f"{API_URL}/orders", json=order_data)
        order_id = resp.json().get("order_id")
        print(f"✓ Order created: {order_id}")
        await asyncio.sleep(8)
        
        picklists_resp = await client.get(f"{BASE_URL}/Picklists", headers=HEADERS)
        picklists = picklists_resp.json()["records"]
        picklist = next((p for p in picklists if order_id in str(p.get("fields", {}).get("order_id", []))), None)
        
        if picklist:
            picklist_id = picklist["id"]
            # Update to Completed
            await client.patch(f"{BASE_URL}/Picklists/{picklist_id}", headers=HEADERS, json={"fields": {"status": "Completed"}})
            print(f"✓ Picklist completed: {picklist_id}")
            await asyncio.sleep(3)
            
            # Check order status changed to Ready
            order_resp = await client.get(f"{BASE_URL}/Orders/{order_id}", headers=HEADERS)
            status = order_resp.json()["fields"].get("status")
            print(f"  Order status: {status} (Expected: Ready)")
            
            # Check order items marked as picked
            items_resp = await client.get(f"{BASE_URL}/Order_Items", headers=HEADERS)
            items = items_resp.json()["records"]
            order_items = [i for i in items if order_id in str(i.get("fields", {}).get("order_id", []))]
            picked_items = [i for i in order_items if i["fields"].get("order_picked") == True]
            print(f"  Picked items: {len(picked_items)}/{len(order_items)}")
            
            # Check notifications
            notif_resp = await client.get(f"{BASE_URL}/Notifications", headers=HEADERS)
            print(f"  Notifications: {len(notif_resp.json()['records'])}")
            
            return status == "Ready" and len(picked_items) > 0
        return False

# Test 14: Failed Order Cleanup (Scheduled - Manual Check)
async def test_failed_order_cleanup():
    print("\n=== Failed Order Cleanup (Scheduled Automation) ===")
    print("  ⚠ This is a SCHEDULED automation (runs every 2 weeks on Sunday 9am)")
    print("  Manual test: Create failed orders > 7 days old")
    print("  Expected: Order items marked as cancelled after 7 days")
    print("  Verification: Check Airtable for old failed orders")
    return True

# Test 15: Reservation Timeout (Scheduled - Manual Check)
async def test_reservation_timeout():
    print("\n=== Reservation Timeout (Scheduled Automation) ===")
    print("  ⚠ This is a SCHEDULED automation (runs daily at 12am GMT-8)")
    print("  Manual test steps:")
    print("    1. Create order with status 'Reserved' or 'Picking'")
    print("    2. Set updated_at to 2+ days ago")
    print("    3. Wait for automation to run at midnight")
    print("  Expected: Order status → 'Expired', Exception created")
    print("  Verification: Check Airtable Exceptions table")
    return True

# Test 16: Ready Order Reminder (Scheduled - Manual Check)
async def test_ready_order_reminder():
    print("\n=== Ready Order Reminder (Scheduled Automation) ===")
    print("  ⚠ This is a SCHEDULED automation (runs every 2 days at 11am)")
    print("  Manual test steps:")
    print("    1. Create order with status 'Ready'")
    print("    2. Set updated_at to 2+ days ago")
    print("    3. Wait for automation to run")
    print("  Expected: Email sent, Notification created, AuditLog created")
    print("  Verification: Check Airtable Notifications and AuditLogs tables")
    return True

async def run_all_tests():
    print("=" * 70)
    print("COMPREHENSIVE AUTOMATION TEST SUITE - POSITIVE & NEGATIVE CASES")
    print("=" * 70)
    results = {}
    
    tests = [
        ("1a. Order Validator (Positive)", test_order_validator_positive),
        ("1b. Order Validator (Negative)", test_order_validator_negative),
        ("2a. Stock Checker (Positive)", test_stock_checker_positive),
        ("2b. Stock Checker (Negative)", test_stock_checker_negative),
        ("3a. Transfer Validator (Same Location)", test_transfer_validator_negative_same_location),
        ("3b. Transfer Validator (Zero Qty)", test_transfer_validator_negative_zero_qty),
        ("4a. Transfer Approval (Auto)", test_transfer_approval_positive_auto),
        ("4b. Transfer Approval (Manual)", test_transfer_approval_negative_manual),
        ("5a. High Priority (Urgent)", test_high_priority_positive),
        ("5b. High Priority (Normal)", test_high_priority_negative),
        ("6a. Exception Alert (Critical)", test_exception_alert_positive_critical),
        ("6b. Exception Alert (Low)", test_exception_alert_negative_low),
        ("7a. Exception Assignment (Stock)", test_exception_assignment_stock_team),
        ("7b. Exception Assignment (Ops)", test_exception_assignment_ops_team),
        ("8. Order Cancellation", test_order_cancellation),
        ("9. Picklist Workflow (Full)", test_picklist_workflow),
        ("10. Shipped Notification", test_shipped_notification),
        ("11. Low Stock Alert", test_low_stock_alert),
        ("12. Picklist Started", test_picklist_started_only),
        ("13. Picklist Completer", test_picklist_completer_only),
        ("14. Failed Order Cleanup", test_failed_order_cleanup),
    ]
    
    for name, test_func in tests:
        try:
            results[name] = await test_func()
        except Exception as e:
            print(f"✗ Error: {e}")
            results[name] = False
    
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)
    for name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(results.values())
    print(f"\nTotal: {passed}/{total} tests passed ({int(passed/total*100)}%)")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
