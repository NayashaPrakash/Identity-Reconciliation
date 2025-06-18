## Instructions
The project can be setup locally as well as tested on the hosted app.
There's 2 relevant endpoints.
1. /records - It lists all the records present in the database.
2. /identify - It adds and updates new or existing records.

To test the endpoints, following requests can be made.

1. /records

```
curl -s https://identity-reconciliation-vp2h.onrender.com/records | jq
```

2. /identify

New User - Both email and phone doesn't exist.
```
curl -X POST https://identity-reconciliation-vp2h.onrender.com/identify \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "2993100000", "email": "burrito@example.com"}'
```
Email exists but a new phone number.
```
curl -X POST https://identity-reconciliation-vp2h.onrender.com/identify \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "2666600000", "email": "burrito@example.com"}'
```

Phone number exists but a new email.
```
curl -X POST https://identity-reconciliation-vp2h.onrender.com/identify \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "2666600000", "email": "icecream@example.com"}'
```

Phone and email matches 2 seperate primary records.
```
curl -X POST https://identity-reconciliation-vp2h.onrender.com/identify \
     -H "Content-Type: application/json" \
     -d '{"phoneNumber": "717171", "email": "george@hillvalley.edu"}'
```
