# Troubleshooting

## LED Mode

### Підтримувані режими
2E SYAYVO-BP2400_D підтримує наступні режими LED підсвічування:
- **Off** - вимкнено
- **Low** - низька яскравість
- **Half Bright** - середня яскравість
- **High Light** - висока яскравість
- **Strobe** - мигання
- **SOS** - режим SOS

**Примітка:** Назви режимів відповідають Tuya Smart app (оновлено у версії 1.3.1).

### Якщо LED Mode не працює

1. Перевірте що ви використовуєте підтримуваний режим (див. список вище)
2. Перевірте логи Home Assistant (Налаштування → Система → Логи)
3. Знайдіть повідомлення `Failed to set LED Mode`
4. Створіть issue на GitHub з логами: https://github.com/oredka/hassio-portable-power-stations-tuya-iot/issues

## Проблеми з підключенням до Tuya Cloud

Якщо інтеграція не може підключитися до Tuya Cloud:

1. Перевірте що Access ID, Access Secret та Device ID правильні
2. Переконайтеся що пристрій підключений до Tuya IoT Platform:
   - Увійдіть на https://iot.tuya.com
   - Cloud → Development → ваш проєкт
   - Devices - пристрій має бути в списку
3. Перевірте що пристрій авторизовано через App Account:
   - Cloud → Development → Link Tuya App Account
   - Увійдіть через Smart Life або Tuya Smart app
4. Переконайтеся що API активовано:
   - Service API → IoT Core → Subscribe (безкоштовно)
