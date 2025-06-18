The project can be setup locally as well as tested on the hosted app.
There's 2 relevant endpoints.
1. /records - It lists all the records present in the database.
2. /identify - It adds and updates new or existing records.

To test the endpoints, following requests can be made.
/records

```
curl -s https://identity-reconciliation-vp2h.onrender.com/records | jq
```
