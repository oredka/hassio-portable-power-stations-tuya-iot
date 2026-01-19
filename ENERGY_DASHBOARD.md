# Налаштування Energy Dashboard

Інтеграція 2E Power Station надає сенсор Battery Power для використання в панелі енергії Home Assistant.

## Налаштування Energy Dashboard

1. Відкрийте **Налаштування** → **Панелі керування** → **Енергія**
2. Натисніть **Додати акумулятор**
3. У полі **Battery power** виберіть: `sensor.2e_power_station_battery_power`

**Примітка**: Сенсор Battery Power показує потужність батареї в Ватах:
- Позитивне значення = розряд батареї (споживання)
- Негативне значення = заряд батареї (накопичення)

## Доступні сенсори

### Сенсори потужності (Power)
- `sensor.2e_power_station_total_in_power` - Вхідна потужність (Вт)
- `sensor.2e_power_station_total_out_power` - Вихідна потужність (Вт)
- `sensor.2e_power_station_battery_power` - Потужність батареї (Вт)
- `sensor.2e_power_station_ac_out_power` - AC вихід (Вт)
- `sensor.2e_power_station_dc_out_power` - DC вихід (Вт)
- `sensor.2e_power_station_usb1_out_power` - USB порти (Вт)

### Інші сенсори
- `sensor.2e_power_station_main_battery_level` - Рівень батареї (%)
- `sensor.2e_power_station_battery_temperature` - Температура батареї (°C)

## Обмеження

Energy Dashboard в Home Assistant вимагає сенсори енергії (kWh) для точного обліку заряду/розряду батареї. На даний момент пристрої 2E Power Station через Tuya IoT не надають дані про накопичену енергію, тільки поточну потужність.

Для повноцінного обліку енергії можна додатково створити допоміжні сенсори через інтеграцію **Riemann sum integral** в Home Assistant UI (Налаштування → Пристрої та служби → Додати інтеграцію → Riemann sum integral).
