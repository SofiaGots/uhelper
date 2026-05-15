from collections.abc import Sequence

from src.agents.base_agent import BaseAgent
from src.data.repository import UniversityRepository
from src.models.base import BaseAgentMessage
from src.models.university import ProgramDetail, University


class UniversityDataAgent(BaseAgent):
    def __init__(self, repository: UniversityRepository | None = None) -> None:
        super().__init__()
        self._repo = repository or UniversityRepository()
        self._repo.load()

    def can_handle(self, intent: str) -> bool:
        return intent in ("university_search", "program_search", "requirements_search")

    async def process(self, message: BaseAgentMessage) -> BaseAgentMessage:
        if message.intent == "university_search":
            response = self._search_universities(message.message)
        elif message.intent == "program_search":
            response = self._search_programs(message.message)
        elif message.intent == "requirements_search":
            response = self._search_requirements(message.message)
        else:
            response = "Извините, я не понял ваш запрос о университетах"

        message.agent_response = {
            "agent": self.name,
            "response": response,
            "next_steps": ["university_search", "profile_analysis"],
            "confidence": 0.9,
        }
        return message

    def _search_universities(self, query: str) -> str:
        tokens = self._repo.extract_tokens(query)
        if not tokens:
            return "Извините, не понял ваш запрос."

        query_has_city = any(self._repo._token_matches_any_city(t) for t in tokens)
        query_has_prog = any(self._repo._token_matches_any_program(t) for t in tokens)

        if query_has_city and query_has_prog:
            matching_progs = self._repo.find_matching_programs(query)
            city_universities = [
                u
                for u in self._repo.all
                if any(
                    self._repo._token_matches_field(t, c)
                    for t in tokens
                    for c in self._repo._searchable_cities(u)
                )
            ]
            results = [u for u in city_universities if u.name in matching_progs]
            if not results:
                return (
                    "В этом городе не нашлось университетов с запрошенной программой. "
                    "Попробуйте изменить направление или город."
                )
            progs_to_show = matching_progs
        else:
            results = self._repo.search(query)
            progs_to_show = self._repo.find_matching_programs(query)

        if not results:
            return "Извините, не нашел университетов по вашему запросу. Попробуйте уточнить поиск."

        lines = ["Нашел следующие университеты:\n"]
        for uni in results:
            lines.append(f"**{uni.name}** ({uni.city})")
            uni_progs = progs_to_show.get(uni.name)
            if uni_progs:
                for detail in uni_progs:
                    parts = [f"   Программа: {detail.name}"]
                    if detail.ege_subjects:
                        parts.append(f"   Предметы ЕГЭ: {', '.join(detail.ege_subjects)}")
                    budget = detail.budget_score or uni.budget_requirements.min_score
                    parts.append(f"   Бюджет: от {budget} баллов")
                    paid = detail.paid_score or uni.paid_requirements.min_score
                    parts.append(f"   Платное: от {paid} баллов")
                    deadline = uni.application_deadlines.get("main", "уточнять")
                    parts.append(f"   Срок подачи: {deadline}")
                    lines.extend(parts)
                    lines.append("")
            else:
                progs = ", ".join(uni.programs[:3])
                lines.append(f"   Программы: {progs}")
                lines.append(f"   Бюджет: от {uni.budget_requirements.min_score} баллов")
                lines.append(f"   Платное: от {uni.paid_requirements.min_score} баллов")
                deadline = uni.application_deadlines.get("main", "уточнять")
                lines.append(f"   Срок подачи: {deadline}\n")
        return "\n".join(lines)

    def _search_programs(self, query: str) -> str:
        tokens = self._repo.extract_tokens(query)
        if not tokens:
            return "Извините, не понял ваш запрос."
        matches: list[tuple[University, ProgramDetail]] = []
        for uni in self._repo.all:
            for detail in uni.program_details:
                if any(self._repo._token_matches_field(t, detail.name.lower()) for t in tokens):
                    matches.append((uni, detail))
        if not matches:
            return "Извините, не нашел программ по вашему запросу. Попробуйте уточнить поиск."
        seen: set[str] = set()
        lines = ["Нашел следующие программы:\n"]
        for uni, detail in matches:
            key = f"{uni.name}:{detail.name}"
            if key in seen:
                continue
            seen.add(key)
            lines.append(f"**{uni.name}** ({uni.city})")
            lines.append(f"   Программа: {detail.name}")
            if detail.ege_subjects:
                lines.append(f"   Предметы ЕГЭ: {', '.join(detail.ege_subjects)}")
            budget = detail.budget_score or uni.budget_requirements.min_score
            lines.append(f"   Бюджет: от {budget} баллов")
            paid = detail.paid_score or uni.paid_requirements.min_score
            lines.append(f"   Платное: от {paid} баллов")
            deadline = uni.application_deadlines.get("main", "уточнять")
            lines.append(f"   Срок подачи: {deadline}\n")
        return "\n".join(lines)

    def _search_requirements(self, query: str) -> str:  # noqa: ARG002
        return (
            "**Общие требования к поступлению в российские университеты:**\n\n"
            "**Основные документы:**\n"
            "- Паспорт\n"
            "- Аттестат о среднем образовании\n"
            "- Результаты ЕГЭ\n"
            "- Медицинская справка (форма 086/у)\n"
            "- Фотографии 3x4\n\n"
            "**Рекомендации:**\n"
            "- Начинайте готовиться за 1-2 года до поступления\n"
            "- Участвуйте в олимпиадах для получения льгот\n"
            "- Следите за сроками подачи документов\n"
            "- Сдавайте предметы, соответствующие выбранной специальности"
        )

    @property
    def universities(self) -> Sequence[University]:
        return self._repo.all
