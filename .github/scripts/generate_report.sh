#!/bin/bash
# Generate workflow execution report

echo "# R2 Zip Processing Report"
echo ""
echo "## Summary"
echo "- Files scanned: Completed"
echo "- Trigger type: $TRIGGER_TYPE"

if [[ "$FILE_COUNT" == "0" ]]; then
  echo "- No ZIP files found to process"
else
  echo "- ZIP files found: $FILE_COUNT"
  
  if [[ "$PROCESS_RESULT" == "success" ]]; then
    echo "- All files processed successfully"
    
    if [[ "$CLEANUP_RESULT" == "success" ]]; then
      echo "- Backup and processed directories cleaned up successfully"
    elif [[ "$CLEANUP_RESULT" == "skipped" ]]; then
      echo "- Cleanup was skipped"
    else
      echo "- Cleanup failed. Check job logs for details."
    fi
  elif [[ "$PROCESS_RESULT" == "skipped" ]]; then
    echo "- No files to process"
  else
    echo "- Some files failed to process. Check job logs for details."
  fi
fi

echo ""
echo "## Next Steps"
echo "- The workflow will run again in 5 minutes to check for new ZIP files"