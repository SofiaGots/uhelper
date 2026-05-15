import re
from pathlib import Path

from src.models.university import ProgramDetail, University

DEFAULT_DATA_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "universities.json"

_STOP_WORDS = frozenset(
    (
        "какие",
        "какой",
        "какая",
        "какое",
        "каких",
        "каким",
        "в",
        "на",
        "с",
        "со",
        "по",
        "из",
        "у",
        "от",
        "до",
        "для",
        "за",
        "о",
        "об",
        "и",
        "а",
        "но",
        "да",
        "или",
        "не",
        "ни",
        "нет",
        "есть",
        "быть",
        "был",
        "была",
        "это",
        "этого",
        "этот",
        "тот",
        "та",
        "те",
        "что",
        "чего",
        "чему",
        "чем",
        "кто",
        "кого",
        "весь",
        "все",
        "всё",
        "всей",
        "ты",
        "вы",
        "вас",
        "вам",
        "мой",
        "моя",
        "мое",
        "хочу",
        "нужно",
        "надо",
        "можно",
        "пожалуйста",
        "спасибо",
        "привет",
    )
)


class UniversityRepository:
    def __init__(self, data_path: Path | str | None = None) -> None:
        self._data_path = Path(data_path or DEFAULT_DATA_PATH)
        self._universities: list[University] = []
        self._loaded = False

    @property
    def all(self) -> list[University]:
        if not self._loaded:
            raise RuntimeError("Repository not loaded; call .load() first")
        return list(self._universities)

    def load(self) -> None:
        import json

        if not self._data_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self._data_path}")
        raw = json.loads(self._data_path.read_text(encoding="utf-8"))
        self._universities = [University.model_validate(item) for item in raw]
        self._loaded = True

    def search_by_city(self, city: str) -> list[University]:
        return [u for u in self.all if city.lower() in u.city.lower()]

    def search_by_program(self, program: str) -> list[University]:
        return [u for u in self.all if any(program.lower() in p.lower() for p in u.programs)]

    def search_by_name(self, name: str) -> list[University]:
        return [u for u in self.all if name.lower() in u.name.lower()]

    def filter_by_min_score(self, min_score: int) -> list[University]:
        return [u for u in self.all if u.budget_requirements.min_score >= min_score]

    _CITY_ALIASES: dict[str, list[str]] = {
        "санкт-петербург": ["питер", "спб"],
        "санкт петербург": ["питер", "спб"],
    }

    @staticmethod
    def _token_matches_field(token: str, field: str) -> bool:
        if token in field:
            return True
        if field in token:
            return True
        min_len = min(len(token), len(field))
        if min_len >= 4 and token[:4] == field[:4]:
            return True
        if any(len(w) >= 4 and token[:4] == w[:4] for w in field.split()):
            return True
        return False

    def _searchable_cities(self, uni: University) -> list[str]:
        cities = [uni.city.lower(), uni.name.lower()]
        for alias_city, aliases in self._CITY_ALIASES.items():
            if alias_city in uni.city.lower() or alias_city in uni.name.lower():
                cities.extend(aliases)
        return cities

    def _token_matches_any_city(self, token: str) -> bool:
        return any(
            any(self._token_matches_field(token, c) for c in self._searchable_cities(u))
            for u in self._universities
        )

    def _token_matches_any_program(self, token: str) -> bool:
        return any(
            self._token_matches_field(token, p.lower())
            for u in self._universities
            for p in u.programs
        )

    def _score_university(self, uni: University, tokens: list[str]) -> tuple[int, int]:
        searchable = self._searchable_cities(uni)
        prog_lower = [p.lower() for p in uni.programs]

        city_score = sum(
            1 for t in tokens if any(self._token_matches_field(t, s) for s in searchable)
        )
        prog_score = sum(
            1 for t in tokens if any(self._token_matches_field(t, p) for p in prog_lower)
        )
        return city_score, prog_score

    def extract_tokens(self, query: str) -> list[str]:
        return [
            t
            for t in re.sub(r"[^a-zа-яё0-9]", " ", query.lower()).split()
            if len(t) > 2 and t not in _STOP_WORDS
        ]

    def find_matching_programs(self, query: str) -> dict[str, list[ProgramDetail]]:
        tokens = self.extract_tokens(query)
        if not tokens:
            return {}
        result: dict[str, list[ProgramDetail]] = {}
        for uni in self.all:
            matches: list[ProgramDetail] = []
            for d in uni.program_details:
                if any(self._token_matches_field(t, d.name.lower()) for t in tokens):
                    matches.append(d)
            if matches:
                result[uni.name] = matches
        return result

    def search(self, query: str) -> list[University]:
        tokens = [
            t
            for t in re.sub(r"[^a-zа-яё0-9]", " ", query.lower()).split()
            if len(t) > 2 and t not in _STOP_WORDS
        ]
        if not tokens:
            return []

        query_has_city = any(self._token_matches_any_city(t) for t in tokens)
        query_has_prog = any(self._token_matches_any_program(t) for t in tokens)
        require_both = query_has_city and query_has_prog

        if require_both:
            both: list[tuple[int, University]] = []
            for uni in self.all:
                city_score, prog_score = self._score_university(uni, tokens)
                if city_score > 0 and prog_score > 0:
                    both.append((city_score + prog_score, uni))
            if both:
                both.sort(key=lambda x: x[0], reverse=True)
                return [uni for _, uni in both]

        scored: list[tuple[int, University]] = []
        for uni in self.all:
            city_score, prog_score = self._score_university(uni, tokens)
            total = city_score * 2 + prog_score
            if total > 0:
                scored.append((total, uni))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [uni for _, uni in scored]
