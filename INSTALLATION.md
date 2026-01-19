# Інструкція по встановленню

## Проблема: При додаванні показує тільки поле "host"

Це означає що Home Assistant кешує старий код. Виконай ці кроки:

### Крок 1: Видалити стару інтеграцію

**Через UI:**
1. Налаштування → Пристрої та служби
2. Знайди "2E Power Stations" (або будь-яку схожу)
3. Три крапки → **Видалити**

### Крок 2: Видалити файли вручну

**SSH або File Editor:**
```bash
# Видалити папку інтеграції
rm -rf /config/custom_components/2e_power_stations

# Видалити кеш (опціонально, але рекомендовано)
rm -rf /config/.storage/core.config_entries
```

**УВАГА:** Видалення `core.config_entries` видалить налаштування ВСІХ інтеграцій!

**Безпечніше:**
```bash
# Тільки видалити папку
rm -rf /config/custom_components/2e_power_stations
```

### Крок 3: Перезапустити Home Assistant

**Через UI:**
1. Налаштування → Система → Перезапустити

**Або SSH:**
```bash
ha core restart
```

### Крок 4: Встановити знову

**Через HACS:**
1. HACS → Інтеграції
2. Три крапки → Custom repositories
3. URL: `https://github.com/oredka/2e-power-stations`
4. Category: Integration
5. Встановити "2E Power Stations"
6. **Перезапустити HA знову**

**Вручну:**
```bash
cd /config/custom_components/
git clone https://github.com/oredka/2e-power-stations.git 2e_power_stations
```

### Крок 5: Додати інтеграцію

1. Налаштування → Пристрої та служби → **Додати інтеграцію**
2. Знайти "2E Power Stations"
3. Тепер має показатись **4 поля**:
   - ✅ Tuya Access ID
   - ✅ Tuya Access Secret
   - ✅ Device ID
   - ✅ Регіон

## Якщо все ще показує "host"

### Варіант 1: Очистити кеш браузера

1. У браузері натисни **Ctrl+Shift+Delete** (або Cmd+Shift+Delete на Mac)
2. Видали кеш
3. Перезавантаж сторінку Home Assistant

### Варіант 2: Використати інший браузер або режим інкогніто

### Варіант 3: Перевірити логи

```bash
# Дивись логи Home Assistant
tail -f /config/home-assistant.log

# Або через UI:
# Налаштування → Система → Логи
```

Шукай помилки типу:
- `ModuleNotFoundError`
- `ImportError`
- `Error loading custom_components.2e_power_stations`

## Отримання Tuya Credentials

1. Зареєструйся на https://iot.tuya.com
2. Створи Cloud Project:
   - Cloud → Development → Create Cloud Project
3. Отримай:
   - **Access ID** (з розділу Overview)
   - **Access Secret** (з розділу Overview)
4. Додай пристрій:
   - Devices → Link App Account
   - Додай через Tuya Smart або Smart Life app
5. Скопіюй **Device ID** зі списку пристроїв
6. Активуй API:
   - Service API → IoT Core → Subscribe (безкоштовно)

## Підтримка

Якщо нічого не допомагає:
1. [Створи issue](https://github.com/oredka/2e-power-stations/issues)
2. Додай логи з Home Assistant
3. Опиши що саме показується при додаванні інтеграції
