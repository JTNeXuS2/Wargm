### Настройка

## bot_token
из вашего приложения созданого в https://discord.com/developers/applications
![bot_token](https://junger.zzux.com/webhook/guide/4.png)

незабудьте включить намерения
![idents](https://junger.zzux.com/webhook/guide/3.png)

## shopid и shop_token
например https://wargm.ru/shop/105/
 ![wargm_api.png](https://junger.zzux.com/webhook/guide/wargm_shop_api.png)
 
=> это номер вашего магазина на сайте там же генерируем API ключ

## bonusdays 
=> время жизни начисленых бонусво в днях 1-365
## channel_id 
=> ид канала для уведомлений заполняется после добавления бота в ваш дискорд и использования команды /sendhere
 ![log.png](https://junger.zzux.com/webhook/guide/log.png)

## timer 
время опроса варгм в секундах
не рекомендуется ставить слишком частые опросы
т.к варгм дает только 150 запросов за 5 минут

## [server]
 на варг создаем предложение и копурем id

![offer_id](https://junger.zzux.com/webhook/guide/offer_id.png)

также копируем id сервера куда будут начислятся бонусы за покупку этого товара

![target_id](https://junger.zzux.com/webhook/guide/target_id.png)

далее используем в дискорде команду для добавления сопоставления
/addoffer (ид предложения) (ид целевого сервера) (имя не обязательно)

или вручную заполняем конфиг по образцу
##  
    [server]
    190210 = 52964: Conan Великая Русь


### [Donate for me](https://yoomoney.ru/to/4100116619431314)
https://fkwallet.io  ID: F7202415841873335


 
