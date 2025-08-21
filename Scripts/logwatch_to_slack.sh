#!/bin/bash
# Exemple de comment envoyer les rapports de logwatch a slack.
# Il faut encore definir par exemple dans quel channel envoyer, etc ..

# URL du webhook Slack
webhook_url="https://hooks.slack.com/services/XXXXX/XXXXX/XXXXX"

# Exécute Logwatch et stocke le rapport dans une variable
logwatch_report=$(logwatch --detail low --range yesterday --output stdout)

# Envoyer le rapport à Slack
payload="{
    \"text\": \"$(echo "$logwatch_report" | sed 's/"/\\"/g')\"
}"

curl -X POST -H 'Content-type: application/json' --data "$payload" $webhook_url
