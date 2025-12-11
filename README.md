# Change Risk Scoring Service

Scorecard-based risk scoring for change requests using scorecardpy.

## API

### POST /score-change

Score a change request.

**Request:**
```json
{
  "data_sensitivity": "payment_card_data|regulated_pii|customer_pii|internal_business|public_data",
  "downtime_impact": "revenue_loss_critical|major_disruption|productivity_impact|minimal_impact",
  "integrity_impact": "financial_harm|decision_impact|operational_inefficiency|low_impact",
  "breach_consequence": "payment_exposure|pii_breach|customer_data_exposure|internal_exposure|public_only",
  "disaster_recovery": "four_hours|twentyfour_hours|three_days|one_week",
  "system_dependencies": "high_dependency|moderate_dependency|low_dependency|standalone",
  "regulatory_count": 0-5,
  "resilience_category": "0|1|2|3",
  "change_size": "XS|S|M|L|XL",
  "test_depth": "NONE|UNIT_ONLY|UNIT_INTEGRATION|FULL|FULL_PLUS_CHAOS",
  "apps_sharing_codebase": int,
  "downstream_critical_deps": int
}
```

**Response:**
```json
{
  "version": 2,
  "score": 727.0,
  "band": "CRITICAL",
  "feature_scores": { ... },
  "raw_points": 127.0
}
```

### GET /health

Returns service status and config version.

### GET /scorecard

Returns current scorecard definition.

### POST /reload-config

Hot-reload scorecard.yaml without restart.

## Features

| Feature | Source | Description |
|---------|--------|-------------|
| data_sensitivity | questionnaire | Data classification level |
| downtime_impact | questionnaire | 4-hour outage impact |
| integrity_impact | questionnaire | Data corruption impact |
| breach_consequence | questionnaire | Security breach worst case |
| disaster_recovery | questionnaire | Recovery time objective |
| system_dependencies | questionnaire | Downstream system count |
| regulatory_count | questionnaire | Regulatory frameworks (0-5) |
| resilience_category | CMDB | Resilience tier (0-3) |
| change_size | git | Lines changed |
| test_depth | CI/CD | Test stages passed |
| apps_sharing_codebase | component_mapping | Shared codebase count |
| downstream_critical_deps | dependency_graph | Critical dependency count |

## Scoring

- **Base score**: 600
- **Range**: 592 - 740
- **Bands**: LOW (≤635), MEDIUM (≤670), HIGH (≤705), CRITICAL (>705)

## Configuration

Edit `config/scorecard.yaml` to modify bins, points, or bands.

## Run

```bash
pip install -r requirements.txt
uvicorn main:app --reload
```
