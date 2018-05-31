import requests
def send_lead():
    apikey = "c6b7f558fb879c9dcbec357d28fc0c564a443108"
    # r = requests.post(f"https://www.tokkobroker.com/api/v1/webcontact?key={apikey}",
    #                   data={'cellphone': "1168412910", 'name': 'valentin gavela'})

    r = requests.post(f"https://www.tokkobroker.com/api/v1/webcontact?key={apikey}&cellphone=1168412910&name=valentin gavela)

    print(r.status_code, r.reason)

if __name__ == '__main__':
    send_lead()

    # curl - H "Content-Type: application/json" - d '{"key":"c6b7f558fb879c9dcbec357d28fc0c564a443108","cellphone":"1168412910","name":"valentin gavela"}'
    # https: // www.tokkobroker.com / api / v1 / webcontact
