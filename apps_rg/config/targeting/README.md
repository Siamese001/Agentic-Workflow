# apps_rg targeting inputs

## Briefing variants

| File pattern | Use |
|--------------|-----|
| `*_briefing.md` | Full research dossier (human prep, citations, tables). **Not sized for 24k Qwen first-pass exec-summary token budget.** |
| `*_briefing_exec.md` | Exec-summary digest (role themes, leadership, M&A/AI hooks). **Default for `python -m apps_rg` CLI.** |

### Brown & Brown SVP IT Strategy & Innovation

- Full: [brown_brown_svp_it_strategy_innovation_briefing.md](brown_brown_svp_it_strategy_innovation_briefing.md)
- CLI default: [brown_brown_svp_it_strategy_innovation_briefing_exec.md](brown_brown_svp_it_strategy_innovation_briefing_exec.md)
- JD: [brown_brown_svp_it_strategy_innovation_jd.txt](brown_brown_svp_it_strategy_innovation_jd.txt)

### Auto exec brief

Set `APPS_RG_AUTO_EXEC_BRIEF=1` to swap `*_briefing.md` → `*_briefing_exec.md` when the sibling exists.

```powershell
$env:APPS_RG_AUTO_EXEC_BRIEF = "1"
python -m apps_rg --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

RCA: [brown_svp_full_resume_rca_remediation_20260527.md](../../../docs/reports/apps_rg/brown_svp_full_resume_rca_remediation_20260527.md)
