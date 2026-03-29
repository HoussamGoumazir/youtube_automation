#!/bin/bash
cd /home/houssam/Documents/youtube_automation

echo "🎯 Starting YouTube Automation System"
echo "📅 $(date)"

case $1 in
    "morning"|"noon"|"evening")
        python3 main.py $1
        ;;
    "check")
        python3 main.py check
        ;;
    "health")
        python3 main.py health
        ;;
    "stats")
        python3 main.py stats
        ;;
    *)
        echo "Usage: $0 {morning|noon|evening|check|health|stats}"
        exit 1
        ;;
esac

echo "🏁 Process completed at $(date)"