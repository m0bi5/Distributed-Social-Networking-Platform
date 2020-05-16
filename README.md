# Distributed Social Networking Platform

Execution steps-

1. Create two mysql databases called socialnetwork, socialnetwork2
2. Execute table creation commands from DBServer/schemas.txt on each of these databases
3. Run 2 db servers (execute following commands from within DB Server folder) - python3 app.py 5000 , python3 app.py 5001
4. Run load balancer (execute following commands from within load balancer folder) - python3 app.py 4000
5. Run application server (execute following commands from within Application folder) - python3 app.py 8000

(After performing steps 3-5 you will have 4 terminals running independently)

Access the application at http://localhost:8000
