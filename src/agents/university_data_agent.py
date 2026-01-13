import os
import anthropic
from typing import Dict, Any, List
from src.agents.base_agent import BaseAgent
from src.models.base import BaseAgentMessage, UniversityInfo


class UniversityDataAgent(BaseAgent):
    """Агент для работы с данными университетов"""

    def __init__(self):
        super().__init__()
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        # База данных университетов с реальными требованиями по программам
        self.universities = self._initialize_universities()

    def can_handle(self, intent: str) -> bool:
        return intent in ["university_search", "program_search", "requirements_search"]

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        """Обрабатывает запросы о университетах"""

        if message.intent == "university_search":
            response = await self._search_universities(message.message)
        elif message.intent == "program_search":
            response = await self._search_programs(message.message)
        elif message.intent == "requirements_search":
            response = await self._search_requirements(message.message)
        else:
            response = "Извините, я не понял ваш запрос о университетах"

        message.agent_response = {
            "agent": self.name,
            "response": response,
            "next_steps": ["university_search", "profile_analysis"],
            "confidence": 0.9
        }
        return message

    async def _search_universities(self, query: str) -> str:
        """Поиск университетов по запросу"""

        # Фильтруем университеты по запросу
        filtered_universities = []
        for uni in self.universities:
            if query.lower() in uni["name"].lower() or query.lower() in uni["city"].lower():
                filtered_universities.append(uni)

        if filtered_universities:
            result = "Нашел следующие университеты:\n\n"
            for uni in filtered_universities[:5]:  # Ограничиваем вывод
                result += f"🏛️ **{uni['name']}** ({uni['city']})\n"
                result += f"   Программы: {', '.join(uni['programs'][:3])}\n"
                result += f"   Бюджетные места: от {uni['budget_requirements']['min_score']} баллов\n"
                result += f"   Платные места: от {uni['paid_requirements']['min_score']} баллов\n"
                result += f"   Срок подачи: {uni['application_deadlines']['main']}\n\n"
            return result
        else:
            return "Извините, не нашел университетов по вашему запросу. Попробуйте уточнить поиск."

    async def _search_programs(self, query: str) -> str:
        """Поиск образовательных программ"""

        # Ищем программы по запросу
        matching_programs = []
        for uni in self.universities:
            for program in uni["program_details"]:
                if query.lower() in program["name"].lower():
                    matching_programs.append({"university": uni["name"], "program": program})

        if matching_programs:
            result = "Нашел следующие программы:\n\n"
            for match in matching_programs[:5]:
                program = match["program"]
                result += f"🎓 **{program['name']}** ({match['university']})\n"
                result += f"   Предметы ЕГЭ: {', '.join(program['ege_subjects'])}"
                if "budget_score" in program:
                    result += f"\n   Бюджет: от {program['budget_score']} баллов"
                if "paid_score" in program:
                    result += f"\n   Платное: от {program['paid_score']} баллов\n\n"
            return result
        else:
            return "Извините, не нашел программ по вашему запросу. Попробуйте уточнить поиск."

    async def _search_requirements(self, query: str) -> str:
        """Поиск требований к поступлению"""

        return """
        **Общие требования к поступлению в российские университеты:**

        📚 **Основные документы:**
        - Паспорт
        - Аттестат о среднем образовании
        - Результаты ЕГЭ
        - Медицинская справка (форма 086/у)
        - Фотографии 3x4

        💡 **Рекомендации:**
        - Начинайте готовиться за 1-2 года до поступления
        - Участвуйте в олимпиадах для получения льгот
        - Следите за сроками подачи документов
        - Сдавайте предметы, соответствующие выбранной специальности
        """

    def _initialize_universities(self) -> List[Dict[str, Any]]:
        """Инициализирует базу университетов с реальными требованиями"""
        return [
            {
                "name": "МГУ им. М.В. Ломоносова",
                "city": "Москва",
                "programs": ["Математика", "Информатика", "Физика", "Химия", "Экономика", "Журналистика"],
                "budget_requirements": {"min_score": 290},
                "paid_requirements": {"min_score": 220},
                "tuition_fee": 350000,
                "application_deadlines": {"main": "20 июля", "олимпиады": "1 февраля"},
                "program_details": [
                    {"name": "Математика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 290, "paid_score": 220},
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 295, "paid_score": 225},
                    {"name": "Физика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 285, "paid_score": 215},
                    {"name": "Экономика", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 300, "paid_score": 230}
                ]
            },
            {
                "name": "СПбГУ",
                "city": "Санкт-Петербург",
                "programs": ["Информатика", "Физика", "Математика", "Юриспруденция", "Менеджмент"],
                "budget_requirements": {"min_score": 270},
                "paid_requirements": {"min_score": 200},
                "tuition_fee": 280000,
                "application_deadlines": {"main": "25 июля", "олимпиады": "15 февраля"},
                "program_details": [
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 280, "paid_score": 210},
                    {"name": "Юриспруденция", "ege_subjects": ["Обществознание", "Русский язык", "История"], "budget_score": 290, "paid_score": 220},
                    {"name": "Физика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 275, "paid_score": 205}
                ]
            },
            {
                "name": "МГТУ им. Н.Э. Баумана",
                "city": "Москва",
                "programs": ["Информатика", "Машиностроение", "Робототехника", "Авиастроение"],
                "budget_requirements": {"min_score": 275},
                "paid_requirements": {"min_score": 210},
                "tuition_fee": 320000,
                "application_deadlines": {"main": "30 июля", "олимпиады": "10 февраля"},
                "program_details": [
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 280, "paid_score": 215},
                    {"name": "Машиностроение", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 270, "paid_score": 205},
                    {"name": "Робототехника", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 285, "paid_score": 220}
                ]
            },
            {
                "name": "НИУ ВШЭ",
                "city": "Москва",
                "programs": ["Экономика", "Менеджмент", "Социология", "Политология", "Юриспруденция"],
                "budget_requirements": {"min_score": 285},
                "paid_requirements": {"min_score": 215},
                "tuition_fee": 380000,
                "application_deadlines": {"main": "22 июля", "олимпиады": "5 февраля"},
                "program_details": [
                    {"name": "Экономика", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 295, "paid_score": 225},
                    {"name": "Менеджмент", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 285, "paid_score": 215},
                    {"name": "Юриспруденция", "ege_subjects": ["Обществознание", "Русский язык", "История"], "budget_score": 290, "paid_score": 220}
                ]
            },
            {
                "name": "МФТИ",
                "city": "Москва",
                "programs": ["Прикладная математика", "Физика", "Информатика", "Биомедицина"],
                "budget_requirements": {"min_score": 300},
                "paid_requirements": {"min_score": 230},
                "tuition_fee": 400000,
                "application_deadlines": {"main": "18 июля", "олимпиады": "25 января"},
                "program_details": [
                    {"name": "Прикладная математика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 305, "paid_score": 235},
                    {"name": "Физика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 300, "paid_score": 230},
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 310, "paid_score": 240}
                ]
            },
            {
                "name": "УрФУ",
                "city": "Екатеринбург",
                "programs": ["Физика", "Математика", "Информатика", "Экономика", "Юриспруденция"],
                "budget_requirements": {"min_score": 250},
                "paid_requirements": {"min_score": 180},
                "tuition_fee": 180000,
                "application_deadlines": {"main": "28 июля", "олимпиады": "20 февраля"},
                "program_details": [
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 255, "paid_score": 185},
                    {"name": "Экономика", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 250, "paid_score": 180},
                    {"name": "Физика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 245, "paid_score": 175}
                ]
            },
            {
                "name": "НГУ",
                "city": "Новосибирск",
                "programs": ["Математика", "Физика", "Биология", "Химия", "Экономика"],
                "budget_requirements": {"min_score": 260},
                "paid_requirements": {"min_score": 190},
                "tuition_fee": 200000,
                "application_deadlines": {"main": "26 июля", "олимпиады": "18 февраля"},
                "program_details": [
                    {"name": "Математика", "ege_subjects": ["Математика", "Русский язык", "Физика"], "budget_score": 265, "paid_score": 195},
                    {"name": "Биология", "ege_subjects": ["Биология", "Русский язык", "Химия"], "budget_score": 255, "paid_score": 185},
                    {"name": "Экономика", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 260, "paid_score": 190}
                ]
            },
            {
                "name": "ТГУ",
                "city": "Томск",
                "programs": ["Информатика", "Физика", "Психология", "Журналистика", "История"],
                "budget_requirements": {"min_score": 255},
                "paid_requirements": {"min_score": 185},
                "tuition_fee": 190000,
                "application_deadlines": {"main": "27 июля", "олимпиады": "17 февраля"},
                "program_details": [
                    {"name": "Информатика", "ege_subjects": ["Математика", "Русский язык", "Информатика"], "budget_score": 260, "paid_score": 190},
                    {"name": "Психология", "ege_subjects": ["Биология", "Русский язык", "Математика"], "budget_score": 250, "paid_score": 180},
                    {"name": "Журналистика", "ege_subjects": ["Литература", "Русский язык", "Иностранный язык"], "budget_score": 255, "paid_score": 185}
                ]
            },
            {
                "name": "МГИМО",
                "city": "Москва",
                "programs": ["Международные отношения", "Политология", "Юриспруденция", "Экономика"],
                "budget_requirements": {"min_score": 295},
                "paid_requirements": {"min_score": 225},
                "tuition_fee": 420000,
                "application_deadlines": {"main": "15 июля", "олимпиады": "28 января"},
                "program_details": [
                    {"name": "Международные отношения", "ege_subjects": ["История", "Иностранный язык", "Русский язык"], "budget_score": 300, "paid_score": 230},
                    {"name": "Юриспруденция", "ege_subjects": ["Обществознание", "Русский язык", "История"], "budget_score": 295, "paid_score": 225},
                    {"name": "Экономика", "ege_subjects": ["Математика", "Иностранный язык", "Русский язык"], "budget_score": 290, "paid_score": 220}
                ]
            },
            {
                "name": "РЭУ им. Г.В. Плеханова",
                "city": "Москва",
                "programs": ["Экономика", "Менеджмент", "Маркетинг", "Финансы", "Бухучет"],
                "budget_requirements": {"min_score": 270},
                "paid_requirements": {"min_score": 200},
                "tuition_fee": 280000,
                "application_deadlines": {"main": "23 июля", "олимпиады": "14 февраля"},
                "program_details": [
                    {"name": "Экономика", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 275, "paid_score": 205},
                    {"name": "Маркетинг", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 270, "paid_score": 200},
                    {"name": "Финансы", "ege_subjects": ["Математика", "Русский язык", "Обществознание"], "budget_score": 280, "paid_score": 210}
                ]
            }
        ]