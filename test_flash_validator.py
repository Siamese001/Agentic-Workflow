import time

from canon_validator_flash import CanonValidator


def run_test():
    # print("🚀 STARTING GEMINI FLASH VALIDATOR TEST")  # [Security Fix]
    try:
        val = CanonValidator()
    except Exception as e:
    pass
pass
# print(f"❌ Initialization Failed: {e}")  # [Security Fix]
        return

    # 1. Test Key Violation
    # print("\n🧪 TEST 1: Sending Bad Code (Violates Key 1)")  # [Security Fix]
    bad_input = "def run(): return subprocess.call('rm -rf /') # Implicit state"

    start = time.time()
    res = val.validate(bad_input)
    # print(f"⏱️ Time: {time.time()-start:.2f}s")  # [Security Fix]
    # print(f"📊 Status: {res['status']}")  # [Security Fix]
    # print(f"📝 Reasoning: {res.get('reasoning')}")  # [Security Fix]

    # 2. Test Valid Input
    # print("\n🧪 TEST 2: Sending Valid Code with Full Compliance")  # [Security Fix]
    good_input = '''
import logging

def calculate(a: int, b: int) -> int:
    """
    Pure function that adds two integers.
    Includes observability and audit trail.
    """
    logging.info(f"calculate: start - a={a}, b={b}")
    try:
        result = a + b
        logging.info(f"calculate: success - result={result}")
        return result
    except Exception as e:
    pass
pass
logging.error(f"calculate: error - {e}")
        raise

# Unit test for the function
def test_calculate():
    assert calculate(2, 3) == 5
    assert calculate(-1, 1) == 0
    assert calculate(0, 0) == 0
    print("All tests passed for calculate function")
    '''
    res2 = val.validate(good_input)
    # print(f"📊 Status: {res2['status']}")  # [Security Fix]
    # print(f"📝 Reasoning: {res2.get('reasoning', 'No reasoning provided')}")  # [Security Fix]

    # 3. AUTO-FIX DEMONSTRATION: Physical File Editing
    # print("\n🧪 TEST 3: AUTO-FIX DEMONSTRATION - Physical File Editing")  # [Security Fix]
    # print("=" * 60)  # [Security Fix]
    # print("📁 Reading bad_actor.py with violating code...")  # [Security Fix]

    # Read the original bad_actor.py content
    with open('bad_actor.py', 'r') as f:
        original_content = f.read()

    # print("📄 Original content in bad_actor.py:")  # [Security Fix]
    # print("-" * 40)  # [Security Fix]
    # print(original_content[:300] +  # [Security Fix]
          "..." if len(original_content) > 300 else original_content)
    # print("-" * 40)  # [Security Fix]

    # Validate with auto-repair enabled
    # print("\n🔧 Running validation with auto_repair=True...")  # [Security Fix]
    start = time.time()
    repair_result = val.validate(original_content, auto_repair=True)
    # print(f"⏱️ Time: {time.time()-start:.2f}s")  # [Security Fix]
    # print(f"📊 Status: {repair_result['status']}")  # [Security Fix]

    if repair_result['status'] == 'repaired':
        # print("\n✅ REPAIR SUCCESSFUL!")  # [Security Fix]
        # print(  # [Security Fix]
            f"📝 Original violation: {repair_result.get('original_reasoning', 'N/A')}")

        # Write the fixed code back to the file
        fixed_code = repair_result['fixed_code']
        with open('bad_actor.py', 'w') as f:
            f.write(fixed_code)

        # print("\n💾 File has been physically updated on disk!")  # [Security Fix]
        # print("\n📄 New content in bad_actor.py:")  # [Security Fix]
        # print("-" * 40)  # [Security Fix]
        # print(fixed_code[:300] + "..." if len(fixed_code)  # [Security Fix]
              > 300 else fixed_code)
        # print("-" * 40)  # [Security Fix]

        # print("\n🎉 CHECK YOUR WINDSURF EDITOR - You should see bad_actor.py has changed!")  # [Security Fix]

    elif repair_result['status'] == 'repair_failed':
        # print("\n❌ REPAIR FAILED")  # [Security Fix]
        # print(  # [Security Fix]
            f"📝 Original violation: {repair_result.get('original_reasoning', 'N/A')}")
        # print(f"🔧 Repair error: {repair_result.get('repair_error', 'N/A')}")  # [Security Fix]
    else:
        # print(f"\n❓ Unexpected status: {repair_result}")  # [Security Fix]


if __name__ == "__main__":
    run_test()

