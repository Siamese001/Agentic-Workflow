+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: SILENT SWALLOW            | FIXED STATE: EXPLICIT HANDLE / RAISE      |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     risky()                               |     risky()                               |
| except X:                                 | except SpecificError as exc:              |
|     pass                                  |     logger.warning("...", exc_info=exc)   |
|                                           |     raise                                 |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ risky step ]                            | [ risky step ]                            |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
|   [ error ]                               |   [ error ]                               |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
|  [ pass / void ]                          | [ log real failure ]                      |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ continue obliviously ]                  | [ raise / route failure ]                 |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ hidden bad state ]                      | [ fail / retry / heal / escalate ]        |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Failure is hidden entirely.               | Truth stays visible.                      |
| No signal to caller or control flow.      | Caller can react safely.                  |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: Error happened, but the system   | SUMMARY: Error happened, and the system   |
| pretended nothing happened.               | treated it as real.                       |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: LOG AND CONTINUE BLINDLY  | FIXED STATE: LOG AND RAISE / RECOVER      |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     risky()                               |     risky()                               |
| except X as exc:                          | except SpecificError as exc:              |
|     logger.error("...", exc_info=exc)     |     logger.error("...", exc_info=exc)     |
|     continue                              |     raise  # or explicit bounded recover  |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ critical step ]                         | [ critical step ]                         |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
|   [ error ]                               |   [ error ]                               |
|      |                                    |      |                                    |
|      +--> [ log ]                         |      +--> [ log ]                         |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ continue anyway ]                       | [ raise or approved recovery ]            |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ system acts "fine" ]                    | [ safe branch chosen explicitly ]         |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Log preserves words, not truth.           | Logging and truth now agree.              |
| Runtime may continue in bad state.        | Failure becomes actionable.               |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: "We saw the fire" but kept       | SUMMARY: "We saw the fire" and either     |
| driving.                                  | stopped or followed the fire drill.       |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: RETURN NONE ON FAILURE    | FIXED STATE: TYPED FAILURE / PROPAGATE    |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| def load_cfg():                           | def load_cfg():                           |
|     try:                                  |     try:                                  |
|         return parse()                    |         return parse()                    |
|     except Exception:                     |     except ParseError as exc:             |
|         return None                       |         raise ConfigLoadError(...)        |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ parse config ]                          | [ parse config ]                          |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
|   [ error ]                               |   [ parse error ]                         |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ return None ]                           | [ raise typed failure ]                   |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ wrong branch later ]                    | [ caller handles exact problem ]          |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ later crash / ambiguity ]               | [ safe fail / repair / default path ]     |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Failure became ambiguity.                 | Failure becomes explicit.                 |
| Crash moves downstream and gets murky.    | Downstream logic stays clean.             |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: The real error was delayed and   | SUMMARY: The real error stayed labeled    |
| disguised as "maybe empty".               | and reachable.                            |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: DEFAULT FALLBACK MASKING  | FIXED STATE: EXPLICIT UNAVAILABLE STATE   |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     price = get_price()                   |     price = get_price()                   |
| except Exception:                         | except PriceLookupError as exc:           |
|     price = 0                             |     raise PriceUnavailable(...)           |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ fetch real value ]                      | [ fetch real value ]                      |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
|   [ error ]                               |   [ lookup error ]                        |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ fake value = 0 ]                        | [ explicit unavailable ]                  |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ bad data looks valid ]                  | [ caller knows data is missing ]          |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Outage is hidden behind fake data.        | Reality is preserved.                     |
| Business logic may trust a lie.           | Consumers can retry or degrade safely.    |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: It replaced "unknown" with a     | SUMMARY: It keeps "unknown" honest.       |
| made-up answer.                           |                                           |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: CATCH-ALL AT WRONG LEVEL  | FIXED STATE: NARROW CATCH AT BOUNDARY     |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| def main():                               | def step2():                              |
|     try:                                  |     try:                                  |
|         step1(); step2(); step3()         |         do_db_write()                     |
|     except Exception:                     |     except DBWriteError as exc:           |
|         return "failed"                   |         raise Step2Failed(...) from exc   |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ step1 ] [ step2 ] [ step3 ]             | [ step1 ] [ step2 ] [ step3 ]             |
|                 |                         |           |                               |
|                 v                         |           v                               |
|          [ many possible errors ]         |     [ exact error point ]                 |
|                 |                         |           |                               |
|                 v                         |           v                               |
|          [ one generic bucket ]           |   [ precise typed failure ]               |
|                 |                         |           |                               |
|                 v                         |           v                               |
|          [ context destroyed ]            |   [ caller knows what failed ]            |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Root cause is flattened.                  | Failure stays local and labeled.          |
| Debugging and recovery both weaken.       | Recovery can be targeted.                 |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: Many different failures were     | SUMMARY: The failure is caught where it   |
| collapsed into one shrug.                 | can still be understood.                  |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: RETRY WITHOUT BOUNDS      | FIXED STATE: BOUNDED RETRY + BACKOFF      |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| while True:                               | for attempt in range(MAX_RETRIES):        |
|     try: call_api()                       |     try:                                  |
|     except Timeout: retry                 |         call_api()                        |
|                                           |     except Timeout:                       |
|                                           |         sleep(backoff(attempt))           |
|                                           | raise FinalTimeout(...)                   |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ call ] -> [ fail ] -> [ retry ] -> ...  | [ call ] -> [ fail ] -> [ backoff ]       |
|                 ^                         |                  |                        |
|                 |                         |                  v                        |
|                 +--------- infinity ------+             [ retry N times ]             |
|                                           |                  |                        |
|                                           |            +--------+--------+            |
|                                           |            |                 |            |
|                                           |            v                 v            |
|                                           |       [ success ]      [ give up cleanly ]|
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Burns time, resources, and may storm.     | Retries are controlled and observable.    |
| Can duplicate side effects forever.       | Terminal failure is still reachable.      |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: It confused persistence with     | SUMMARY: It tries hard, but not forever.  |
| discipline.                               |                                           |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: PARTIAL SIDE EFFECTS      | FIXED STATE: ATOMICITY / ROLLBACK         |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| write A                                   | begin transaction                         |
| write B                                   | write A                                   |
| fail on C                                 | write B                                   |
| except: log and continue                  | write C                                   |
|                                           | commit                                    |
|                                           | except: rollback                          |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ A done ]                                | [ begin unit of work ]                    |
|    |                                      |          |                                |
| [ B done ]                                |          v                                |
|    |                                      | [ A ] -> [ B ] -> [ C ]                   |
| [ C fails ]                               |          |                                |
|    |                                      |          v                                |
| [ ignored ]                               |   [ commit ] or [ rollback all ]          |
|    |                                      |          |                                |
|    v                                      |          v                                |
| [ inconsistent system of record ]         | [ consistent final state ]                |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Some writes landed, some did not.         | State changes become all-or-nothing.      |
| Downstream truth is corrupted.            | Recovery is predictable.                  |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: It left half the paperwork filed | SUMMARY: Either the full change lands,    |
| and walked away.                          | or none of it does.                       |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: EXCEPTION TYPE ERASURE    | FIXED STATE: PRESERVE CAUSE AND TYPE      |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     risky()                               |     risky()                               |
| except Exception as exc:                  | except ConnectionTimeoutError as exc:     |
|     raise RuntimeError("fail")            |     raise ServiceTimeout(...) from exc    |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ rich error data ]                       | [ rich error data ]                       |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ caught broadly ]                        | [ caught specifically ]                   |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ generic wrapper only ]                  | [ wrapper keeps causal chain ]            |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ root cause blurred ]                    | [ root cause still inspectable ]          |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Important diagnostic detail was lost.     | Causality survives.                       |
| Recovery logic loses precision.           | Debugging and handling improve.           |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: The message survived, but the    | SUMMARY: The message and the cause both   |
| identity of the failure did not.          | survive.                                  |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: CLEANUP HIDES ROOT CAUSE  | FIXED STATE: GUARDED CLEANUP              |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     fail_A()                              |     fail_A()                              |
| finally:                                  | finally:                                  |
|     fail_B()                              |     try: cleanup()                        |
|                                           |     except CleanupError:                  |
|                                           |         logger.warning("cleanup failed")  |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ true error A ]                          | [ true error A ]                          |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ finally crashes ]                       | [ cleanup attempted ]                     |
|      |                                    |      |                                    |
|      v                                    |      +--> [ cleanup warning if needed ]   |
| [ error B surfaces instead ]              |      |                                    |
|                                           |      v                                    |
|                                           | [ original error A preserved ]            |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Cleanup became the distraction.           | Primary failure remains primary.          |
| RCA points at the wrong thing.            | Cleanup issues are separated cleanly.     |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: The mop-up spilled paint over    | SUMMARY: Cleanup can fail without         |
| the original crime scene.                 | deleting the real clue.                   |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: SUCCESS IN FINALLY        | FIXED STATE: LET REAL OUTCOME WIN         |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | try:                                      |
|     return do_work()                      |     return do_work()                      |
| finally:                                  | finally:                                  |
|     return "ok"                           |     cleanup_only()                        |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ do_work fails ]                         | [ do_work fails ]                         |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ finally returns ok ]                    | [ finally cleans up only ]                |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ caller sees success ]                   | [ caller sees real fail or real result ]  |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Control flow lies about outcome.          | Outcome truth is preserved.               |
| This is outright misreporting.            | Cleanup no longer overwrites reality.     |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: Finally should tidy up, not      | SUMMARY: Cleanup happens, but truth keeps |
| forge the report card.                    | the final word.                           |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: DOUBLE LOGGING            | FIXED STATE: LOG ONCE AT OWNERSHIP EDGE   |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| inner():                                  | inner():                                  |
|   except X as exc:                        |   except X:                               |
|     logger.error("inner", exc_info=exc)   |     raise                                 |
|     raise                                 | outer():                                  |
| outer():                                  |   except X as exc:                        |
|   except X as exc:                        |     logger.error("outer", exc_info=exc)   |
|     logger.error("outer", exc_info=exc)   |     handle()                              |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ one error ]                             | [ one error ]                             |
|      |                                    |      |                                    |
|      +--> [ log 1 ]                       |      v                                    |
|      |                                    | [ propagate upward ]                      |
|      +--> [ rethrow ]                     |      |                                    |
|      |                                    |      v                                    |
|      v                                    | [ log once where owned ]                  |
| [ log 2 ]                                 |      |                                    |
|      |                                    |      v                                    |
|      v                                    | [ one signal, one alert ]                 |
| [ duplicate noise ]                       |                                           |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| One fault created many alarms.            | Signal-to-noise improves.                 |
| Observability gets noisier, not smarter.  | RCA stays cleaner.                        |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: It counted the same fire twice.  | SUMMARY: One failure should usually       |
|                                           | produce one owned log.                    |
+-------------------------------------------+-------------------------------------------+

+-------------------------------------------+-------------------------------------------+
| ORIGINAL STATE: THROW FOR NORMAL FLOW     | FIXED STATE: NORMAL BRANCHING             |
+-------------------------------------------+-------------------------------------------+
| [ Code ]                                  | [ Code ]                                  |
| try:                                      | item = find_optional_item()               |
|     find_optional_item()                  | if item is None:                          |
| except NotFound:                          |     next_path()                           |
|     next_path()                           | else:                                     |
|                                           |     use(item)                             |
+-------------------------------------------+-------------------------------------------+
| [ Flow ]                                  | [ Flow ]                                  |
| [ check optional thing ]                  | [ check optional thing ]                  |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ not found ]                             | [ not found ]                             |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ throw exception ]                       | [ ordinary branch ]                       |
|      |                                    |      |                                    |
|      v                                    |      v                                    |
| [ catch ]                                 | [ next path ]                             |
|      |                                    |                                           |
|      v                                    |                                           |
| [ do normal path anyway ]                 |                                           |
+-------------------------------------------+-------------------------------------------+
| [ Why it was bad ]                        | [ What the fix achieved ]                 |
| Exceptions were used for routine logic.   | Normal flow becomes simple and cheap.     |
| Code gets slower and noisier.             | Errors remain reserved for real errors.   |
+-------------------------------------------+-------------------------------------------+
| SUMMARY: A regular hallway was treated    | SUMMARY: Use exceptions for surprises,    |
| like a fire escape.                       | not for everyday doorways.                |
+-------------------------------------------+-------------------------------------------+