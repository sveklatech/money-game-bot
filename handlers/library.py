from telegram import Update
from telegram.ext import ContextTypes
from services.content import (
    get_manifesto_part, get_concept, get_scenario, get_mini_process_text
)
from keyboards.keyboards import (
    library_menu_keyboard, manifesto_keyboard, scenarios_keyboard,
    concepts_keyboard, back_keyboard, main_menu_keyboard
)


async def library_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📚 *Библиотека материалов*\n\nВыбери раздел:"

    if update.message:
        await update.message.reply_text(text, parse_mode="Markdown", reply_markup=library_menu_keyboard())
    elif update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(text, parse_mode="Markdown", reply_markup=library_menu_keyboard())


async def process_map_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "🗺️ *Карта Процесса — 6 шагов*\n\n"
        "_Дискомфорт — это мигающий красный сигнал: «Здесь Сила! Забери меня!»_\n\n"
        "1️⃣ *Погрузись в центр дискомфорта*\n"
        "Закрой глаза. Нырни в самый эпицентр ощущения. Не отворачивайся.\n\n"
        "2️⃣ *Прочувствуй энергию полностью*\n"
        "Без мыслей, без логики, без ярлыков. Это твоя Сила. Если можешь — усиль её.\n\n"
        "3️⃣ *На пике — скажи Истину*\n"
        "«Я есть Сила и Присутствие Бога. Я создала это. Оно не настоящее. Это творение моего Сознания.»\n\n"
        "4️⃣ *Забери Силу обратно*\n"
        "«ТЕПЕРЬ я забираю свою Силу из этого создания. Забирая её, я чувствую, как она возвращается ко мне.»\n\n"
        "5️⃣ *Раскройся тому, Кто ты есть*\n"
        "«Я ЕСТЬ Сила и Присутствие Бога. Я ЕСТЬ в Безграничном Изобилии, здесь и сейчас.»\n\n"
        "6️⃣ *Выразить Признательность*\n"
        "«Вау. Какое великолепное создание. Спасибо себе. Спасибо своему творению.»"
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard("library_menu"))


async def concepts_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = "💡 *Карта концепций*\n\nВыбери концепцию:"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=concepts_keyboard())


async def concept_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    concept_id = query.data.replace("concept_", "")
    concept = get_concept(concept_id)

    if not concept:
        await query.answer("Концепция не найдена", show_alert=True)
        return

    text = f"💡 *{concept['name']}*\n\n{concept['description']}"
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard("lib_concepts"))


async def scenarios_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "💼 *Бизнес-сценарии Процесса*\n\n"
        "10 самых горячих ситуаций предпринимательской жизни.\n"
        "Выбери ситуацию:"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=scenarios_keyboard())


async def scenario_detail_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    scenario_id = int(query.data.replace("scenario_", ""))
    scenario = get_scenario(scenario_id)

    if not scenario:
        await query.answer("Сценарий не найден", show_alert=True)
        return

    text = (
        f"💼 *{scenario['id']:02d}. {scenario['title']}*\n"
        f"_{scenario['category']}_\n\n"
        f"*Триггер:*\n{scenario['trigger']}\n\n"
        f"*Истина Фазы 2:*\n{scenario['truth']}\n\n"
        f"*Применение:*\n{scenario['application']}\n\n"
        f"*Мысленный скрипт:*\n_{scenario['script']}_"
    )

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard("lib_scenarios"))


async def manifesto_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "📖 *Манифест Фазы 2*\n\n"
        "_Золотая книга убеждений о Том, Кто Я Есть._\n\n"
        "Выбери раздел для чтения:"
    )
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=manifesto_keyboard())


async def manifesto_part_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    part_id = query.data.replace("manifesto_", "")
    part = get_manifesto_part(part_id)

    if not part:
        await query.answer("Раздел не найден", show_alert=True)
        return

    text = f"📖 *{part['title']}*\n_{part['subtitle']}_\n\n{part['content']}"

    if len(text) > 4096:
        text = text[:4090] + "..."

    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=back_keyboard("lib_manifesto"))


async def manifesto_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "📖 *Манифест Фазы 2*\n\n_Золотая книга убеждений о Том, Кто Я Есть._\n\nВыбери раздел:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=manifesto_keyboard())


async def concepts_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💡 *Карта концепций*\n\nВыбери концепцию:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=concepts_keyboard())


async def scenarios_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "💼 *Бизнес-сценарии Процесса*\n\nВыбери ситуацию:"
    await update.message.reply_text(text, parse_mode="Markdown", reply_markup=scenarios_keyboard())
