import time
import random
from datetime import datetime

# ==========================================
# 1. БАЗА ДАННЫХ И ИСТОРИЯ (BIG DATA)
# ==========================================
# Храним историю карьеры игроков (вклад в голы/защиту)
players_history = {
    101: {"name": "M. Salah", "goals_per_match": 0.65, "position": "FW", "style": ["fast_break", "wing_cut"]},
    102: {"name": "V. van Dijk", "defensive_index": 0.95, "position": "DF", "style": ["aerial_master", "leader"]},
    103: {"name": "J. Tah", "defensive_index": 0.80, "position": "DF", "style": ["heavy_def"]}
}

# ==========================================
# 2. МАТЕМАТИЧЕСКОЕ ЯДРО (НАША ФОРМУЛА)
# ==========================================
def calculate_true_total(home_base, away_base, match_conditions):
    """
    Идеальная формула: учитывает погоду, покрытие, судей, трансферы и баланс дня.
    """
    # Базовый тотал из истории команд
    true_total = home_base + away_base
    
    # Фактор 1: Погода и аэродинамика (Дождь/Ветер)
    if match_conditions['weather']['rain']:
        true_total *= 0.92  # Мяч вязнет, голов меньше
    if match_conditions['weather']['wind_speed'] > 8:
        true_total *= 0.88  # Сопротивление мяча мешает дальним передачам
        
    # Фактор 2: Футбольное покрытие
    if not match_conditions['pitch']['is_natural']:
        true_total *= 0.95  # Непривычный отскок на синтетике снижает темп
        
    # Фактор 3: Судейский фактор и пенальти
    referee = match_conditions['referee']
    if referee['penalties_per_match'] > 0.4 or referee['corruption_risk']:
        true_total += 0.20  # Повышаем ожидание гола из-за свистков или пенальти
        
    # Фактор 4: Трансферный вес и история игроков (Big Data)
    for p_id in match_conditions['squad']['new_players']:
        player = players_history.get(p_id)
        if player and player['position'] == "FW":
            true_total += player['goals_per_match'] # Игрок усиливает атаку
            
    for p_id in match_conditions['squad']['injured_players']:
        player = players_history.get(p_id)
        if player and player['position'] == "DF":
            true_total += 0.15 # Защита ослаблена, пропустят больше
            
    # Фактор 5: Баланс линии дня (Mean Reversion)
    true_total += match_conditions['day_line_balance']['shift']
    
    return round(true_total, 2)

# ==========================================
# 3. МОДУЛЬ LIVE-АНАЛИЗА И ГЕНЕРАЦИИ СИГНАЛОВ
# ==========================================
def process_live_match(match_name, home_base, away_base, conditions, live_data):
    """
    Проверяет live-матч по нашей стратегии позднего гола.
    """
    # Считаем истинный потенциал матча по формуле
    true_potential = calculate_true_total(home_base, away_base, conditions)
    
    minute = live_data['minute']
    score = live_data['score']
    odds = live_data['current_odds_tb05']
    
    # Наш жесткий триггер фильтрации:
    # 55-65 минута, счет 0:0, истинный потенциал высокий, коэффициент валуйный (>= 1.35)
    if 55 <= minute <= 65 and score == "0:0":
        if true_potential > 2.0 and odds >= 1.35:
            # Формируем готовый текст Push-уведомления для пользователя приложения
            push_notification = {
                "status": "SEND_SIGNAL",
                "title": f"🔥 СИГНАЛ ПО НАШЕЙ ФОРМУЛЕ!",
                "message": f"Матч: {match_name}\n"
                           f"Минута: {minute} | Счет: {score}\n"
                           f"Ставка: Тотал Больше 0.5\n"
                           f"Коэффициент БК: {odds} (ВАЛУЙ)\n"
                           f"Истинный тотал матча по формуле: {true_potential}\n"
                           f"Ударов в створ за 15 мин: {live_data['recent_shots']}"
            }
            return push_notification
            
    return {"status": "SKIPPED", "message": f"Матч {match_name} не прошел фильтр формулы."}

# ==========================================
# 4. СИМУЛЯЦИЯ РАБОТЫ НАШЕГО ПРИЛОЖЕНИЯ
# ==========================================
# Задаем условия реального матча
current_match_conditions = {
    "weather": {"rain": False, "wind_speed": 4},
    "pitch": {"is_natural": True},
    "referee": {"penalties_per_match": 0.45, "corruption_risk": True}, # Судья часто ставит пенальти
    "squad": {"new_players":, "injured_players": [103]},        # Топ-форвард пришел, защитник травмирован
    "day_line_balance": {"shift": -0.05}                              # Небольшой откат линии дня
}

# Имитируем данные, которые приходят к нам в live на 60-й минуте
live_match_state = {
    "minute": 60,
    "score": "0:0",
    "current_odds_tb05": 1.38, # Букмекер дает коэффициент 1.38 на один гол
    "recent_shots": 4          # Команды активно бьют по воротам последние 15 минут
}

print("=== ЗАПУСК СЕРВЕРА ПРИЛОЖЕНИЯ С НАШЕЙ ФОРМУЛОЙ ===")
result = process_live_match(
    match_name="Австралия (мол) - Япония (мол)",
    home_base=1.2,
    away_base=1.1,
    conditions=current_match_conditions,
    live_data=live_match_state
)

# Выводим результат работы приложения
if result["status"] == "SEND_SIGNAL":
    print("\n[ОТПРАВКА PUSH-УВЕДОМЛЕНИЯ ПОЛЬЗОВАТЕЛЯМ]:")
    print(result["message"])
else:
    print(f"\n[ЛОГ]: {result['message']}")
