from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards import ROADMAP_BUTTONS, create_keyboard
from data import PROFESSIONS_TABLE, ARCHETYPE_NAMES, CONVERSION_EXAMPLES
from states import TechTransition

async def show_results(message: Message, state: FSMContext):
    data = await state.get_data()
    vug = data.get('vug')
    archetype = data.get('archetype')
    vug_name = data.get('vug_name', vug)
    archetype_name = data.get('archetype_name', archetype)
    situations = data.get('situations', {})
    
    # Получаем профессии из таблицы
    professions = PROFESSIONS_TABLE.get((vug, archetype), 
        "👔 Руководитель технических проектов\n⚙️ Технический директор\n📋 Менеджер по развитию")
    
    # Сохраняем профессии
    await state.update_data(professions=professions)
    
    # Анализ ситуаций
    strengths = []
    weaknesses = []
    
    situation_names = {
        1: "Управление проектами",
        2: "Управление людьми",
        3: "Техническая экспертиза",
        4: "Коммуникации",
        5: "Стрессоустойчивость"
    }
    
    for num, answer_data in situations.items():
        if isinstance(answer_data, dict):
            answer_code = answer_data.get('code', '')
            if answer_code in ['yes', 'part']:
                strengths.append(f"• {situation_names.get(num, f'Ситуация {num}')}")
            elif answer_code == 'no':
                weaknesses.append(f"• {situation_names.get(num, f'Ситуация {num}')}")
    
    # Формируем итоговый текст
    result_text = (
        f"🎯 <b>ВАШ ПРОФИЛЬ ТЕХНОЛИДЕРА</b>\n\n"
        f"<b>Военно-учётная группа:</b> {vug_name}\n"
        f"<b>Архетип:</b> {archetype_name}\n\n"
        f"<b>💼 Целевые гражданские позиции:</b>\n{professions}\n\n"
    )
    
    if strengths:
        result_text += "<b>✅ Ваши сильные стороны:</b>\n" + "\n".join(strengths) + "\n\n"
    
    if weaknesses:
        result_text += "<b>📌 Зоны роста:</b>\n" + "\n".join(weaknesses) + "\n\n"
    
    result_text += "<b>🔁 Примеры конвертации опыта:</b>\n"
    for ex in CONVERSION_EXAMPLES:
        result_text += ex + "\n"
    
    result_text += "\n<b>Теперь выберите трек развития:</b>"
    
    await state.set_state(TechTransition.waiting_for_roadmap)
    keyboard = create_keyboard(ROADMAP_BUTTONS)
    
    # Отправляем новое сообщение вместо редактирования (из-за длины)
    await message.answer(result_text, reply_markup=keyboard)
    
    # Удаляем предыдущее сообщение с вопросом
    try:
        await message.delete()
    except:
        pass