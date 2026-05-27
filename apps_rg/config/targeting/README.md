# apps_rg targeting inputs

## Briefing

| File pattern | Use |
|--------------|-----|
| `*_briefing.md` | Targeting brief SSOT (role themes, leadership, M&A/AI hooks) for all lanes and `python -m apps_rg` CLI. |

### Brown & Brown SVP IT Strategy & Innovation

- Briefing: [brown_brown_svp_it_strategy_innovation_briefing.md](brown_brown_svp_it_strategy_innovation_briefing.md)
- JD: [brown_brown_svp_it_strategy_innovation_jd.txt](brown_brown_svp_it_strategy_innovation_jd.txt)

```powershell
python -m apps_rg --target-company "Brown & Brown" `
  --target-role "SVP IT Strategy & Innovation" `
  --jd apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_jd.txt `
  --manual-brief apps_rg/config/targeting/brown_brown_svp_it_strategy_innovation_briefing.md
```

### AIG VP Global Head Agentic AI

- Briefing: [aig_vp_global_head_agentic_ai_briefing.md](aig_vp_global_head_agentic_ai_briefing.md)
- JD: [aig_vp_global_head_agentic_ai_jd.txt](aig_vp_global_head_agentic_ai_jd.txt)
