start chrome 
start "/table/list" "http://localhost:5000/table/list"
start "/table/showall/<table>" "http://localhost:5000/table/showall/games"
start "/table/showall/<table>" "http://localhost:5000/table/showall/players"
start "/table/showall/<table>" "http://localhost:5000/table/showall/scores"

start "/table/post/games" "http://localhost:5000/table/post/games"
start "/table/post/players" "http://localhost:5000/table/post/players"
start "/table/post/scores" "http://localhost:5000/table/post/scores"

pause