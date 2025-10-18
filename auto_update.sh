#!/bin/bash
"""
Setup automatic sector rotation scanning during market hours
This script can be run via cron to automatically scan and update GitHub Pages
"""

# Run the scanner only during market hours
python3 run_during_market_hours.py

# If scanner ran successfully, update GitHub Pages
if [ $? -eq 0 ]; then
    echo ""
    echo "Updating GitHub Pages..."
    python3 update_github_pages.py
    
    # Check if there are changes to commit
    if ! git diff --quiet docs/; then
        echo ""
        echo "Committing and pushing changes..."
        git add docs/
        git commit -m "Auto-update sector rotation data - $(date '+%Y-%m-%d %H:%M:%S')"
        git push
        echo ""
        echo "✅ GitHub Pages updated successfully!"
    else
        echo "No changes to commit."
    fi
fi
