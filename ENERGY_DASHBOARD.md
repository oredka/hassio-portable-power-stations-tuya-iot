# Налаштування Energy Dashboard

Для використання 2E Power Station в панелі енергії Home Assistant потрібно створити допоміжні сенсори для обчислення енергії.

## Крок 1: Створити Riemann Sum Integration сенсори

Додайте до `configuration.yaml`:

```yaml
sensor:
  # Енергія заряду батареї (з вхідної потужності)
  - platform: integration
    source: sensor.2e_power_station_total_in_power
    name: "2E Battery Charge Energy"
    unique_id: 2e_battery_charge_energy
    unit_prefix: k
    round: 2
    method: left

  # Енергія розряду батареї (з вихідної потужності)
  - platform: integration
    source: sensor.2e_power_station_total_out_power
    name: "2E Battery Discharge Energy"
    unique_id: 2e_battery_discharge_energy
    unit_prefix: k
    round: 2
    method: left
```

## Крок 2: Перезапустити Home Assistant

Після додавання конфігурації перезапустіть Home Assistant.

## Крок 3: Налаштувати Energy Dashboard

1. Відкрийте **Налаштування** → **Панелі керування** → **Енергія**
2. Натисніть **Додати акумулятор**
3. Заповніть поля:
   - **Energy charged into the battery**: `sensor.2e_battery_charge_energy`
   - **Energy discharged from the battery**: `sensor.2e_battery_discharge_energy`
   - **Battery power** (опціонально): `sensor.2e_power_station_battery_power`

## Доступні сенсори

### Сенсори потужності (Power)
- `sensor.2e_power_station_total_in_power` - Вхідна потужність (Вт)
- `sensor.2e_power_station_total_out_power` - Вихідна потужність (Вт)
- `sensor.2e_power_station_battery_power` - Потужність батареї (позитивне = розряд, негативне = заряд)
- `sensor.2e_power_station_ac_out_power` - AC вихід
- `sensor.2e_power_station_dc_out_power` - DC вихід
- `sensor.2e_power_station_usb1_out_power` - USB порти

### Сенсори енергії (Energy) - Після додавання конфігурації
- `sensor.2e_battery_charge_energy` - Накопичена енергія заряду (kWh)
- `sensor.2e_battery_discharge_energy` - Накопичена енергія розряду (kWh)

### Інші сенсори
- `sensor.2e_power_station_main_battery_level` - Рівень батареї (%)
- `sensor.2e_power_station_battery_temperature` - Температура батареї (°C)

## Примітки

- Сенсори енергії будуть накопичувати дані з моменту створення
- При перезапуску Home Assistant значення можуть скинутися (залежить від recorder)
- Для точного обліку енергії переконайтеся, що інтервал оновлення не занадто великий (за замовчуванням 30 секунд)
