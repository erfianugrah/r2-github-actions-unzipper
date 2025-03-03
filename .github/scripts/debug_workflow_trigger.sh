#!/bin/bash
# Debug Workflow Trigger Script

if [[ "$GITHUB_EVENT_NAME" == "schedule" ]]; then
  echo "This workflow was triggered by a schedule"
  echo "trigger_type=schedule" >> $GITHUB_OUTPUT
elif [[ "$GITHUB_EVENT_NAME" == "workflow_dispatch" ]]; then
  echo "This workflow was triggered manually via workflow_dispatch"
  echo "trigger_type=manual" >> $GITHUB_OUTPUT
else
  echo "This workflow was triggered by: $GITHUB_EVENT_NAME"
  echo "trigger_type=$GITHUB_EVENT_NAME" >> $GITHUB_OUTPUT
fi