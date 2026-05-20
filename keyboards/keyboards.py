from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton


def main_menu_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("⚡ Процесс", callback_data="start_process"),
            InlineKeyboardButton("✨ Мини-процесс", callback_data="mini_process"),
        ],
        [
            InlineKeyboardButton("📅 Задание дня", callback_data="show_day"),
            InlineKeyboardButton("📔 Журнал", callback_data="journal_menu"),
        ],
        [
            InlineKeyboardButton("📚 Библиотека", callback_data="library_menu"),
            InlineKeyboardButton("📊 Статистика", callback_data="show_stats"),
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def journal_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("📝 Дневник Процесса", callback_data="journal_process")],
        [InlineKeyboardButton("🙏 Журнал Признательности", callback_data="journal_gratitude")],
        [InlineKeyboardButton("💬 Словарь Фазы 1→2", callback_data="journal_vocabulary")],
        [InlineKeyboardButton("📖 Мои последние записи", callback_data="journal_recent")],
        [InlineKeyboardButton("← Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def library_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🗺️ Карта Процесса", callback_data="lib_process_map")],
        [InlineKeyboardButton("💡 Карта концепций", callback_data="lib_concepts")],
        [InlineKeyboardButton("💼 Бизнес-сценарии", callback_data="lib_scenarios")],
        [InlineKeyboardButton("📖 Манифест Фазы 2", callback_data="lib_manifesto")],
        [InlineKeyboardButton("← Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def manifesto_keyboard():
    keyboard = [
        [InlineKeyboardButton("I. Кто Я Есть", callback_data="manifesto_part1")],
        [InlineKeyboardButton("II. Семь иллюзий", callback_data="manifesto_part2")],
        [InlineKeyboardButton("III. Четыре инструмента", callback_data="manifesto_part3")],
        [InlineKeyboardButton("IV. Словарь Фазы 2", callback_data="manifesto_part4")],
        [InlineKeyboardButton("V. Пять приглашений", callback_data="manifesto_part5")],
        [InlineKeyboardButton("VI. Ритуалы", callback_data="manifesto_part6")],
        [InlineKeyboardButton("VII. Точки опоры", callback_data="manifesto_part7")],
        [InlineKeyboardButton("← Назад", callback_data="library_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def scenarios_keyboard():
    keyboard = [
        [InlineKeyboardButton("01. Возражение по цене", callback_data="scenario_1")],
        [InlineKeyboardButton("02. «Нет» и отказ от сделки", callback_data="scenario_2")],
        [InlineKeyboardButton("03. Задержка оплаты", callback_data="scenario_3")],
        [InlineKeyboardButton("04. Сравнение с конкурентами", callback_data="scenario_4")],
        [InlineKeyboardButton("05. Оплата налогов", callback_data="scenario_5")],
        [InlineKeyboardButton("06. Выплаты команде", callback_data="scenario_6")],
        [InlineKeyboardButton("07. Просмотр баланса", callback_data="scenario_7")],
        [InlineKeyboardButton("08. Колебания дохода", callback_data="scenario_8")],
        [InlineKeyboardButton("09. Конфликт в команде", callback_data="scenario_9")],
        [InlineKeyboardButton("10. Большое решение", callback_data="scenario_10")],
        [InlineKeyboardButton("11. Страх потерять бизнес", callback_data="scenario_11")],
        [InlineKeyboardButton("← Назад", callback_data="library_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def concepts_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("Безграничное Я", callback_data="concept_true_self"),
            InlineKeyboardButton("Личность", callback_data="concept_personality"),
        ],
        [
            InlineKeyboardButton("Голограмма", callback_data="concept_hologram"),
            InlineKeyboardButton("Поле", callback_data="concept_field"),
        ],
        [
            InlineKeyboardButton("Паттерны", callback_data="concept_patterns"),
            InlineKeyboardButton("Сила", callback_data="concept_power"),
        ],
        [
            InlineKeyboardButton("Фаза 1 vs Фаза 2", callback_data="concept_phases"),
            InlineKeyboardButton("Признательность", callback_data="concept_gratitude"),
        ],
        [InlineKeyboardButton("🔄 Словарь Ф1→Ф2", callback_data="concept_dictionary")],
        [InlineKeyboardButton("← Назад", callback_data="library_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def settings_keyboard(notifications_on: bool = True):
    notif_text = "🔔 Уведомления: ВКЛ" if notifications_on else "🔕 Уведомления: ВЫКЛ"
    keyboard = [
        [InlineKeyboardButton(notif_text, callback_data="toggle_notifications")],
        [InlineKeyboardButton("⏰ Время утреннего напоминания", callback_data="set_morning_time")],
        [InlineKeyboardButton("🌙 Время вечернего напоминания", callback_data="set_evening_time")],
        [InlineKeyboardButton("← Назад", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def day_keyboard(day_number: int, is_completed: bool):
    keyboard = []
    if not is_completed:
        keyboard.append([
            InlineKeyboardButton("✅ Отметить выполненным", callback_data=f"complete_day_{day_number}")
        ])
    keyboard.append([
        InlineKeyboardButton("⚡ Запустить Процесс", callback_data="start_process"),
    ])
    keyboard.append([
        InlineKeyboardButton("← Главное меню", callback_data="back_main")
    ])
    return InlineKeyboardMarkup(keyboard)


def process_step_keyboard(step: int, total: int = 6):
    keyboard = []
    if step < total:
        keyboard.append([
            InlineKeyboardButton(f"▶ Шаг {step + 1} →", callback_data=f"process_step_{step + 1}")
        ])
    else:
        keyboard.append([
            InlineKeyboardButton("✍️ Записать в журнал", callback_data="process_save")
        ])
        keyboard.append([
            InlineKeyboardButton("Пропустить запись", callback_data="process_skip_save")
        ])
    keyboard.append([
        InlineKeyboardButton("✖ Выйти из Процесса", callback_data="cancel")
    ])
    return InlineKeyboardMarkup(keyboard)


def cancel_keyboard():
    keyboard = [[InlineKeyboardButton("✖ Отмена", callback_data="cancel")]]
    return InlineKeyboardMarkup(keyboard)


def back_keyboard(target: str = "back_main"):
    keyboard = [[InlineKeyboardButton("← Назад", callback_data=target)]]
    return InlineKeyboardMarkup(keyboard)


def confirm_keyboard(yes_data: str, no_data: str = "cancel"):
    keyboard = [
        [
            InlineKeyboardButton("✅ Да", callback_data=yes_data),
            InlineKeyboardButton("✖ Нет", callback_data=no_data),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def discomfort_level_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("1", callback_data="discomfort_1"),
            InlineKeyboardButton("2", callback_data="discomfort_2"),
            InlineKeyboardButton("3", callback_data="discomfort_3"),
            InlineKeyboardButton("4", callback_data="discomfort_4"),
            InlineKeyboardButton("5", callback_data="discomfort_5"),
        ],
        [
            InlineKeyboardButton("6", callback_data="discomfort_6"),
            InlineKeyboardButton("7", callback_data="discomfort_7"),
            InlineKeyboardButton("8", callback_data="discomfort_8"),
            InlineKeyboardButton("9", callback_data="discomfort_9"),
            InlineKeyboardButton("10", callback_data="discomfort_10"),
        ],
        [InlineKeyboardButton("✖ Отмена", callback_data="cancel")],
    ]
    return InlineKeyboardMarkup(keyboard)


def onboarding_keyboard():
    keyboard = [
        [InlineKeyboardButton("🚀 Начать с Дня 1", callback_data="onboarding_start_plan")],
        [InlineKeyboardButton("📚 Сначала посмотреть библиотеку", callback_data="library_menu")],
    ]
    return InlineKeyboardMarkup(keyboard)


def week_summary_keyboard(week: int):
    keyboard = [
        [InlineKeyboardButton(f"✅ Записать итог недели {week}", callback_data=f"write_weekly_review_{week}")],
        [InlineKeyboardButton("← Главное меню", callback_data="back_main")],
    ]
    return InlineKeyboardMarkup(keyboard)
