#!/bash

python3 tg_bot.py &

python3 vk_bot.py &

wait -n

exit $?
