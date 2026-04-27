================================================================================
HIGH-SIGNAL EXCEPTION-HANDLING ANTI-PATTERNS 
(Categorized by Failure Mode)
================================================================================

1) SILENT SWALLOW
--------------------------------------------------------------------------------
Failure Mode: HIDES THE FAILURE

Code:
try:
  risky()
except X:
  pass

Illustration:
  [ ERROR: 💥 ] 
       │
       ▼
  ( except: pass ) ──> 🕳️ [ VOID ]
       │
       ▼
  [ SILENCE ] (Flow continues obliviously)

Original ASCII: error ---> [void]
Risk: total invisibility


2) LOG AND CONTINUE BLINDLY
--------------------------------------------------------------------------------
Failure Mode: KEEPS RUNNING IN BAD STATE

Code:
try:
  risky()
except X as e:
  log(e)
  continue

Illustration:
  [ ERROR: 💥 ] 
       │
       ├─────────────> 📝 [ LOG WRITTEN ]
       ▼
  [ FLOW CONTINUES ] ──> ⚠️ (Moving on as if safe)

Original ASCII: error ---> [log] ---> move on as if safe
Risk: state may now be corrupted or incomplete


3) RETURN NONE ON FAILURE
--------------------------------------------------------------------------------
Failure Mode: HIDES THE FAILURE

Code:
def load_cfg():
  try:
    return parse()
  except Exception:
    return None

Illustration:
  [ ERROR: 💥 ] 
       │
       ▼
  [ returns None ] ──> ⏳ (Time Passes / Wrong Branch) ──> 💥 LATER CRASH!

Original ASCII: error ---> None ---> later crash/wrong branch
Risk: failure turns into ambiguity


4) DEFAULT FALLBACK MASKING
--------------------------------------------------------------------------------
Failure Mode: HIDES THE FAILURE / MISREPORTS REALITY

Code:
try:
  price = get_price()
except Exception:
  price = 0

Illustration:
  [ ERROR: 💥 ] 
       │
       ▼
  [ price = 0 ] ──> 🎭 Fake value masquerades as "valid" data!

Original ASCII: error ---> fake value looks "valid"
Risk: fabricated answer hides real outage


5) CATCH-ALL AT WRONG LEVEL
--------------------------------------------------------------------------------
Failure Mode: HIDES THE ROOT CAUSE

Code:
main():
  try:
    step1()
    step2()
    step3()
  except Exception:
    return "failed"

Illustration:
  [ Database Error ] ──────┐
  [ Network Timeout ] ─────┼──> ( except Exception ) ──> 🗑️ "failed"
  [ File Not Found ] ──────┘     (Context Destroyed)

Original ASCII / Risk: many specific failures collapse into one bucket


6) RETRY WITHOUT BOUNDS
--------------------------------------------------------------------------------
Failure Mode: KEEPS RUNNING IN BAD STATE

Code:
while True:
  try: 
    call_api()
  except Timeout: 
    retry

Illustration:
  ┌── [ ERROR ] ◄──┐
  │      │         │
  │      ▼         │
  └── ( Retry ) ───┘ ──> ∞ (Infinite Loop)

Original ASCII: fail -> retry -> retry -> retry forever
Risk: resource burn, storms, duplicate actions


7) PARTIAL SIDE EFFECTS
--------------------------------------------------------------------------------
Failure Mode: KEEPS RUNNING IN BAD STATE

Code:
write A
write B
fail on C
except: log and continue

Illustration:
  [ Step A: ✅ ] 
       │
  [ Step B: ✅ ] 
       │
  [ Step C: ❌ ] ──> (Caught & Ignored) ──> ⚠️ DB Left Inconsistent

Original ASCII: A✓  B✓  C✗   but flow keeps going
Risk: system-of-record now inconsistent


8) EXCEPTION TYPE ERASURE
--------------------------------------------------------------------------------
Failure Mode: HIDES THE ROOT CAUSE

Code:
try:
  risky()
except Exception as e:
  raise RuntimeError("fail")

Illustration:
  [ ConnectionTimeoutError (Rich Data) ]
       │
  ( Caught & Re-raised )
       │
  [ RuntimeError("fail") (Generic Data) ] ──> 🌫️ Context Erased

Original ASCII: rich cause ---> flattened generic cause
Risk: root cause lost debugging harder


9) CLEANUP HIDES ROOT CAUSE
--------------------------------------------------------------------------------
Failure Mode: HIDES THE ROOT CAUSE

Code:
try: 
  fail A
finally: 
  fail B

Illustration:
  [ Error A (True Root Cause) ]
       │
  ( finally block crashes )
       │
  [ Error B (Distraction) ] ──> 💥 Only Error B surfaces

Original ASCII: original error A overwritten by cleanup B
Risk: true failure buried


10) SUCCESS IN FINALLY
--------------------------------------------------------------------------------
Failure Mode: MISREPORTS REALITY

Code:
try: 
  return do_work()
finally: 
  return "ok"

Illustration:
  [ Function Fails ❌ ]
       │
  ( finally: return "ok" )
       │
  [ Caller receives "ok" ✅ ] ──> 🤥 Reality Overwritten

Original ASCII: real result/failure overwritten by finally
Risk: lies about outcome


11) DOUBLE LOGGING
--------------------------------------------------------------------------------
Failure Mode: CREATES NOISE / ALERT FATIGUE

Code:
inner: log error
outer: log error again

Illustration:
  [ ERROR: 💥 ]
       │
  ( Inner Log 📝 ) ──> 🚨 Alert 1
       │
  [ Re-thrown ]
       │
  ( Outer Log 📝 ) ──> 🚨 Alert 2 (Duplicate Noise)

Original ASCII: one failure becomes many noisy alarms
Risk: alert fatigue


12) THROW FOR NORMAL FLOW
--------------------------------------------------------------------------------
Failure Mode: MISREPORTS REALITY

Code:
try:
  find optional_item()
except NotFound: 
  next_path()

Illustration:
  [ Check Item ] ──> (Not Found)
                         │
                  💥 Throw Exception!
                         │
                      (Caught)
                         │
                  [ Normal Path B ] ──> 🐢 (Inefficient control flow)

Original ASCII: normal branch dressed up as exception
Risk: slow + noisy control flow


================================================================================
BEST PRACTICE OPPOSITES
================================================================================

BAD:  except Exception: pass
GOOD: except FileNotFoundError as e: logger.warning(...); recover explicitly

BAD:  raise ... ; logger.error(...)
GOOD: logger.error(...); raise

BAD:  except Exception: return None
GOOD: except SpecificError as e: return typed failure / propagate with context

BAD:  write A, write B, fail C, continue
GOOD: make writes atomic or compensate/rollback explicitly

--------------------------------------------------------------------------------
BOTTOM LINE: 
The big pattern underneath all of them is this: they turn a real failure into 
either silence, ambiguity, or false confidence, which is exactly why they are 
dangerous.
================================================================================