# bad_code.py — намеренно плохой код для рефакторинга (Задание 3)
# Проблемы: длинная функция, магические числа, нет обработки ошибок,
# неинформативные имена, дублирование кода

def calc(t, s, r):
    # считаем что-то для репетитора
    x = 0
    if r >= 5:
        x = t * s * 0.9
    if r >= 10:
        x = t * s * 0.8
    if r >= 20:
        x = t * s * 0.7
    if r < 5:
        x = t * s

    # теперь считаем рейтинг
    total = 0
    cnt = 0
    for i in s:
        total = total + i
        cnt = cnt + 1
    avg = total / cnt

    # бонус за рейтинг
    if avg > 4.5:
        x = x + 500
    if avg > 4:
        x = x + 200
    if avg > 3:
        x = x + 0

    # штраф за отмены
    if r > 3:
        x = x - 100
    if r > 10:
        x = x - 200
    if r > 20:
        x = x - 500

    # налог
    nn = x * 0.06
    x = x - nn

    # вывод
    print("итого: " + str(x))
    print("налог: " + str(nn))
    print("рейтинг: " + str(avg))

    return x


def get_tutors_list(d):
    res = []
    for k in d:
        t = d[k]
        if t["is_active"] == True:
            res.append(t)
    return res


def get_top(d):
    res = []
    for k in d:
        t = d[k]
        if t["is_active"] == True:
            res.append(t)
    # сортируем
    for i in range(len(res)):
        for j in range(i + 1, len(res)):
            if res[i]["hourly_rate"] < res[j]["hourly_rate"]:
                tmp = res[i]
                res[i] = res[j]
                res[j] = tmp
    return res[:10]