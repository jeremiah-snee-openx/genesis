# Cost-rates table for cells (Anthropic $/Mtok, source: anthropic.com/pricing)
opus-4.7:   input $15.00  output $75.00
sonnet-4.6: input  $3.00  output $15.00
haiku-4.5:  input  $1.00  output  $5.00

Each cell self-reports as JSON:
{
  "cell_id": "...",
  "design_summary": "...",
  "spawns": [
    {"role": "lens-security", "model": "haiku-4.5",
     "estimated_input_tokens": 4500, "estimated_output_tokens": 380,
     "tool_calls": 3, "rationale": "..."},
    ...
  ],
  "total_estimated_cost_usd": 0.XX,
  "artifacts_path": "/tmp/exp-results/<cell_id>/..."
}
