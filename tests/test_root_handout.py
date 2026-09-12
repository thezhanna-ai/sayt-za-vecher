"""Проверки КОРНЕВОЙ раздатки САЙТ (`index.html` этого репозитория).

Зачем файл существует. Набор этого репозитория судил только вложенные
страницы `claude-knopka-za-knopkoy/`, а корневая раздатка - один из двух
продуктов задачи - не проверялась ни одним тестом: машинной защиты от
регресса у неё не было вовсе. Этот файл её подключает.

Почему правила написаны здесь заново, а не взяты импортом из общего модуля
соседней раздатки: репозиторий обязан проверяться в одиночку, на машине, где
соседней папки нет вообще. Импорт через путь наружу сделал бы набор
неработоспособным вне конкретного компьютера, и это дороже, чем повтор
десятка регулярок. Цена названа честно, решение то же, что для соседнего
набора: единство правил держится внутри репозитория, а не между ними.

Правила ловят ПОДМЕНУ, а не только удаление: разбор разметки идёт без учёта
регистра тега, запрет на содержание - по нормализованному тексту. Проверка,
которая краснеет лишь на удалении проверяемого, зелена вхолостую
"""

from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
HANDOUT = ROOT / "index.html"

FLAGS = re.IGNORECASE

PARTNER_LINK = "https://theivansergeev.com/ailager/?gcpc=16fff"
SOURCE_DOMAINS = ("code.claude.com", "support.claude.com")

# Замеры сняты с принятого файла и зафиксированы числом, чтобы сломанный
# разбор стал красным тестом, а не пустым зелёным обходом
PARTNER_BUTTONS = 2
PARTNER_LINK_OCCURRENCES = 3
SECTION_COUNT = 13
# Декоративные галочки и волна в блоке CTA. Рост числа означает, что вместо
# настоящего кадра экрана нарисована схема, а это прямо запрещено
DECORATIVE_SVG = 5

# Собирается из кусков нарочно: файл, который ПЕРЕЧИСЛЯЕТ запрещённые строки,
# иначе ловит сам себя
FOREIGN_SPECIFICS = (
    "/" + "Users/",
    "Ivan" + "OS",
    "zslep" + "ova",
)

# Суммы и даты обязаны нести привязку ко времени, а не звучать вечной ценой
DATED_AMOUNTS = (
    "20 долларов в месяц",
    "2100-2200",
)


def normalized_text(html):
    """Текст в виде, по которому судится запрет на содержание"""
    text = html
    for entity, char in (
        ("&mdash;", "—"),
        ("&ndash;", "–"),
        ("&#8212;", "—"),
        ("&#8211;", "–"),
        ("&#x2014;", "—"),
        ("&#x2013;", "–"),
    ):
        text = text.replace(entity, char)
    return text.lower()


def long_dashes(html):
    return re.findall(r"[—–]", normalized_text(html))


def word_veshchi(html):
    return re.findall(r"вещ", normalized_text(html))


def foreign_specifics(html):
    low = normalized_text(html)
    return [leak for leak in FOREIGN_SPECIFICS if leak.lower() in low]


def paragraphs_ending_with_period(html):
    """Абзацы, закончившиеся точкой; абзац это `p` и `li`, `td` исключён"""
    hits = []
    for match in re.finditer(r"<(p|li)\b[^>]*>(.*?)</\1>", html, re.S | FLAGS):
        tail = re.sub(r"(?:\s|</?[a-z0-9]+\s*/?>)+$", "", match.group(2), flags=FLAGS)
        if not tail.endswith("."):
            continue
        if tail.endswith("..") or tail.endswith("…"):
            continue
        hits.append(" ".join(tail.split())[-60:])
    return hits


def ids_with_tags(html):
    """Пары «тег + id»: id обязан остаться на ТОМ ЖЕ теге"""
    return set(re.findall(r"<([a-z0-9]+)[^>]*\sid=\"([^\"]+)\"", html, FLAGS))


def anchors(html):
    return re.findall(r'href="#([^"]+)"', html, FLAGS)


def partner_buttons(html):
    return re.findall(r"<a\b[^>]*\bdata-partner\b[^>]*>", html, FLAGS)


def partner_link_declarations(html):
    return re.findall(r"(?:var|let|const)\s+PARTNER_LINK\s*=", html, FLAGS)


def source_block_urls(html):
    block = re.search(r'<ul[^>]*class="sources"[^>]*>.*?</ul>', html, re.S | FLAGS)
    if not block:
        return []
    return re.findall(r'href="(https?://[^"]+)"', block.group(0), FLAGS)


def section_ids(html):
    return re.findall(r'<h2[^>]*\sid="([^"]+)"', html, FLAGS)


def sections_without_lead(html):
    """Разделы `h2 id` без единого абзаца до следующего заголовка.

    Обход идёт по РАЗДЕЛАМ, а не по абзацам: раздел, из которого абзац убрали,
    попадает в результат пустым. Обход по абзацам был бы зелёным вхолостую
    """
    heads = [(m.start(), m.group(1))
             for m in re.finditer(r'<h2[^>]*\sid="([^"]+)"', html, FLAGS)]
    empty = []
    for index, (start, section_id) in enumerate(heads):
        end = heads[index + 1][0] if index + 1 < len(heads) else len(html)
        if not re.search(r"<(p|li)\b", html[start:end], FLAGS):
            empty.append(section_id)
    return empty


class RootHandoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = HANDOUT.read_text(encoding="utf-8")

    def test_page_has_exactly_one_h1(self):
        self.assertEqual(len(re.findall(r"<h1\b", self.html, FLAGS)), 1)

    def test_every_internal_anchor_resolves(self):
        ids = {anchor_id for _, anchor_id in ids_with_tags(self.html)}
        self.assertEqual(sorted({a for a in anchors(self.html) if a not in ids}), [])

    def test_no_long_dashes(self):
        self.assertEqual(long_dashes(self.html), [])

    def test_no_paragraph_ends_with_a_period(self):
        self.assertEqual(paragraphs_ending_with_period(self.html), [])

    def test_word_veshchi_is_absent(self):
        self.assertEqual(word_veshchi(self.html), [])

    def test_no_foreign_specifics_leak(self):
        self.assertEqual(foreign_specifics(self.html), [])
        for path in Path(__file__).parent.glob("*.py"):
            text = path.read_text(encoding="utf-8")
            self.assertEqual(
                [leak for leak in FOREIGN_SPECIFICS if leak in text], [], path.name
            )

    def test_partner_link_is_canonical_and_declared_once(self):
        self.assertEqual(len(partner_buttons(self.html)), PARTNER_BUTTONS)
        self.assertEqual(len(partner_link_declarations(self.html)), 1)
        self.assertEqual(
            len(re.findall(re.escape("gcpc=16fff"), self.html)),
            PARTNER_LINK_OCCURRENCES,
        )
        for link in re.findall(r'href="(https?://[^"]*theivansergeev[^"]*)"', self.html):
            self.assertEqual(link, PARTNER_LINK)

    def test_sources_block_exists_with_official_domains(self):
        urls = source_block_urls(self.html)
        self.assertGreater(len(urls), 0, "блока источников нет")
        for url in urls:
            self.assertTrue(any(domain in url for domain in SOURCE_DOMAINS), url)

    def test_every_section_carries_at_least_one_paragraph(self):
        self.assertEqual(sections_without_lead(self.html), [])

    def test_draft_stays_out_of_search_until_published(self):
        """Канон раздаток, пункт 9: черновик держать с noindex.

        Строчка исчезает молча при любой правке шапки, а заметно это
        становится только когда страница уже в индексе поисковика
        """
        self.assertRegex(
            self.html,
            r'<meta\s+name=["\']robots["\']\s+content=["\'][^"\']*noindex',
            "в шапке нет meta robots noindex",
        )

    def test_page_declares_language_and_doctype(self):
        """Без lang читалки и переводчики принимают страницу за английскую"""
        self.assertRegex(self.html, r'(?i)^\s*<!doctype html>', "нет doctype")
        self.assertRegex(self.html, r'(?i)<html\s+lang=["\']ru["\']', "нет html lang=ru")

    def test_section_walk_covers_every_section(self):
        """Охват объявлен числом: пустой обход не пройдёт незамеченным"""
        self.assertEqual(len(section_ids(self.html)), SECTION_COUNT)

    def test_amounts_keep_their_anchor_in_time(self):
        """Сумма без привязки ко времени читается как вечная цена.

        Обе суммы страницы названы поимённо, и рядом с каждой обязан стоять
        год или месяц: иначе через полгода раздатка врёт читателю
        """
        for amount in DATED_AMOUNTS:
            index = self.html.find(amount)
            self.assertNotEqual(index, -1, "сумма пропала со страницы: %s" % amount)
            window = self.html[max(0, index - 400):index + 400]
            self.assertRegex(
                window,
                r"20\d\d|лет[оа]|осен|зим|весн|сентябр|на сегодня",
                "сумма «%s» стоит без привязки ко времени" % amount,
            )

    def test_decorative_svg_did_not_grow(self):
        """Схема вместо настоящего кадра экрана запрещена прямо.

        Рост числа `<svg` - главный машинный признак того, что недостающий
        скриншот подменили рисунком
        """
        self.assertEqual(len(re.findall(r"<svg\b", self.html, FLAGS)), DECORATIVE_SVG)


class MutationResistanceTest(unittest.TestCase):
    """Проверки НА проверки: правило обязано краснеть на ПОДМЕНЁННОМ входе"""

    def assert_caught(self, hits, case):
        self.assertTrue(hits, "подмена прошла незамеченной: %s" % case)

    def test_forbidden_word_is_caught_in_any_case(self):
        for case in ("вещи", "Вещи", "ВЕЩИ", "Вещь"):
            self.assert_caught(word_veshchi("<p>%s тут</p>" % case), case)

    def test_long_dash_is_caught_as_symbol_and_as_entity(self):
        for case in ("—", "–", "&mdash;", "&ndash;", "&#8212;"):
            self.assert_caught(long_dashes("<p>а %s б</p>" % case), case)

    def test_foreign_specifics_are_caught_in_any_case(self):
        for case in FOREIGN_SPECIFICS:
            for variant in (case, case.upper(), case.lower()):
                self.assert_caught(foreign_specifics("<!-- %s -->" % variant), variant)

    def test_period_at_paragraph_end_is_caught_in_every_shape(self):
        cases = (
            "<p>текст.</p>",
            "<p>текст.\n  </p>",
            "<li>текст.</li>",
            "<p>текст.</b></p>",
            "<P>текст.</P>",
            "<LI>текст.</LI>",
            "<p>текст.<br></p>",
        )
        for case in cases:
            self.assert_caught(paragraphs_ending_with_period(case), case)

    def test_ellipsis_is_not_mistaken_for_a_period(self):
        self.assertEqual(paragraphs_ending_with_period("<p>текст…</p>"), [])

    def test_id_moved_to_another_tag_is_visible(self):
        """Перенос id на другой тег запрещён, и пара «тег + id» его показывает"""
        before = ids_with_tags('<h2 id="itog">К</h2>')
        after = ids_with_tags('<div id="itog">К</div>')
        self.assertNotEqual(before, after)

    def test_markup_walks_survive_uppercase_tags(self):
        html = HANDOUT.read_text(encoding="utf-8")
        upper = (
            html.replace("<h2 id=", "<H2 ID=")
            .replace('<ul class="sources"', '<UL CLASS="sources"')
        )
        self.assertEqual(len(section_ids(upper)), len(section_ids(html)))
        self.assertEqual(len(source_block_urls(upper)), len(source_block_urls(html)))


if __name__ == "__main__":
    unittest.main()
