# systemd Templates

These templates mirror `ops/data-quality-tasks.yaml`.
Adjust `User=` in the service files if the repository is owned by another
account.

| YAML task | Service | Timer | Default |
|---|---|---|---|
| `daily_cn_data` | `simtradedata-daily-cn.service` | `simtradedata-daily-cn.timer` | Enable |
| `weekly_cn_quality_repair` | `simtradedata-weekly-cn-quality-repair.service` | `simtradedata-weekly-cn-quality-repair.timer` | Manual after validation |
| `monthly_cn_reconcile` | `simtradedata-monthly-cn-reconcile.service` | `simtradedata-monthly-cn-reconcile.timer` | Manual after validation |

Install the daily timer:

```bash
sudo cp ops/systemd/simtradedata.env.example /etc/simtradedata.env
sudo editor /etc/simtradedata.env
sudo cp ops/systemd/simtradedata-daily-cn.service /etc/systemd/system/
sudo cp ops/systemd/simtradedata-daily-cn.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now simtradedata-daily-cn.timer
```

Weekly repair and monthly reconcile templates are intentionally not enabled by
default. Enable them only after runtime and data-source pressure are acceptable:

```bash
sudo cp ops/systemd/simtradedata-weekly-cn-quality-repair.* /etc/systemd/system/
sudo cp ops/systemd/simtradedata-monthly-cn-reconcile.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now simtradedata-monthly-cn-reconcile.timer
```
