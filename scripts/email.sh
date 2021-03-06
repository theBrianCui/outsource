LOG_OUTPUT=$(base64 LOG_PATH -w 0)
curl --request POST \
--url https://api.sendgrid.com/v3/mail/send \
--header "Authorization: Bearer SENDGRID_API_KEY" \
--header 'Content-Type: application/json' \
--data '{"personalizations": [{"to": [{"email": "RECIPIENT"}]}],"from": {"email": "azure@outsource.com"},"subject": "SUBJECT","content": [{"type": "text/plain", "value": "BODY"}],"attachments": [{"content": "'"$LOG_OUTPUT"'","filename": "out.txt"}]}'
