import flet as ft

from app.pipeline import (
    define_and_save_word,
    get_vocabulary_entries,
    listen_and_transcribe,
)


BACKGROUND = "#070910"
SURFACE = "#10131C"
SURFACE_LIGHT = "#171B27"
BORDER = "#252B3A"
TEXT = "#F4F7FB"
TEXT_MUTED = "#9CA6B8"
TEXT_DIM = "#687285"
ACCENT = "#AAB3FF"
SUCCESS = "#83E6B1"
ERROR = "#FF8A8A"


def _entry_value(entry, key: str, default: str = "") -> str:
    """Read a field from either a dict or a Pydantic model."""
    if isinstance(entry, dict):
        value = entry.get(key, default)
    else:
        value = getattr(entry, key, default)

    return "" if value is None else str(value)


def _card(content: ft.Control, padding: int = 18, bgcolor: str = SURFACE) -> ft.Container:
    return ft.Container(
        content=content,
        bgcolor=bgcolor,
        border=ft.Border.all(1, BORDER),
        border_radius=18,
        padding=padding,
        shadow=[
            ft.BoxShadow(
                blur_radius=24,
                spread_radius=-8,
                color="#66000000",
                offset=ft.Offset(0, 12),
            )
        ],
    )


def _language_badge(language: str) -> ft.Container:
    return ft.Container(
        content=ft.Text(language or "Unknown", size=11, color="#DDE2FF"),
        bgcolor="#26305F",
        border=ft.Border.all(1, "#354071"),
        border_radius=999,
        padding=ft.Padding(10, 4, 10, 4),
    )


def _wave(
    width: int,
    height: int,
    left: int,
    top: int,
    color: str,
    angle: float,
    opacity: float = 1.0,
) -> ft.Container:
    return ft.Container(
        width=width,
        height=height,
        left=left,
        top=top,
        bgcolor=color,
        border_radius=999,
        opacity=opacity,
        rotate=ft.Rotate(angle),
    )


def build_voice_orb(
    is_listening: bool,
    on_tap=None,
    on_hover=None,
    is_hovered: bool = False,
) -> ft.Control:
    """Build the abstract voice orb without Flet button hover chrome."""
    glow = "#776875FF" if is_listening else "#3F5967D8"
    outer_glow = "#668E9BFF" if is_listening else "#335967D8"
    rim = "#D9DEFF" if is_listening else "#8F99DF"
    scale = 1.025 if is_hovered else 1.0

    inner_shapes = [
        ft.Container(
            width=112,
            height=112,
            left=13,
            top=12,
            shape=ft.BoxShape.CIRCLE,
            gradient=ft.RadialGradient(
                colors=(
                    ["#FBFCFF", "#AEB9FF", "#384283"]
                    if is_listening
                    else ["#E7EAFF", "#8D98E5", "#2F366B"]
                ),
                stops=[0.0, 0.43, 1.0],
                radius=0.83,
            ),
            opacity=0.96,
        ),
        _wave(116, 22, 8, 75, "#202846", -0.18, 0.78),
        _wave(118, 18, 3, 91, "#0F1427", 0.16, 0.78),
        _wave(82, 16, 40, 61, "#CAD1FF" if is_listening else "#AAB3FF", -0.3, 0.42),
        _wave(72, 13, 17, 51, "#FFFFFF", 0.24, 0.22 if is_listening else 0.16),
        _wave(68, 11, 50, 38, "#7785FF", -0.42, 0.34 if is_listening else 0.22),
        ft.Container(
            width=42,
            height=42,
            left=31,
            top=26,
            shape=ft.BoxShape.CIRCLE,
            bgcolor="#FFFFFF",
            opacity=0.17 if is_listening else 0.1,
        ),
    ]

    orb = ft.Container(
        width=178,
        height=178,
        alignment=ft.Alignment.CENTER,
        border_radius=999,
        clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
        scale=ft.Scale(scale),
        animate=ft.Animation(180, ft.AnimationCurve.EASE_OUT),
        content=ft.Stack(
            width=178,
            height=178,
            alignment=ft.Alignment.CENTER,
            controls=[
                ft.Container(
                    width=178,
                    height=178,
                    shape=ft.BoxShape.CIRCLE,
                    opacity=0.96 if is_listening else 0.64,
                    gradient=ft.RadialGradient(
                        colors=[outer_glow, "#22344388", "#00070910"],
                        stops=[0.0, 0.5, 1.0],
                        radius=0.92,
                    ),
                ),
                ft.Container(
                    width=144,
                    height=144,
                    shape=ft.BoxShape.CIRCLE,
                    bgcolor="#0D1019",
                    border=ft.Border.all(1, rim),
                    shadow=[
                        ft.BoxShadow(
                            blur_radius=62 if is_listening else 42,
                            spread_radius=5 if is_listening else 1,
                            color=glow,
                            offset=ft.Offset(0, 14),
                        )
                    ],
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS_WITH_SAVE_LAYER,
                    content=ft.Stack(width=144, height=144, controls=inner_shapes),
                ),
                ft.Container(
                    width=144,
                    height=144,
                    shape=ft.BoxShape.CIRCLE,
                    border=ft.Border.all(1, "#44FFFFFF" if is_listening else "#22FFFFFF"),
                ),
            ],
        ),
    )

    return ft.GestureDetector(
        content=orb,
        on_tap=on_tap,
        on_hover=on_hover,
        mouse_cursor=ft.MouseCursor.CLICK,
    )


def _entry_matches(entry, query: str) -> bool:
    if not query:
        return True

    haystack = " ".join(
        [
            _entry_value(entry, "word"),
            _entry_value(entry, "definition"),
            _entry_value(entry, "example"),
            _entry_value(entry, "language"),
        ]
    ).lower()
    return query.lower() in haystack


def main(page: ft.Page) -> None:
    page.title = "Vocabulary Assistant"
    page.window_title_bar_hidden = False
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = BACKGROUND
    page.padding = 28
    page.spacing = 0
    page.scroll = ft.ScrollMode.AUTO
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    all_entries = []
    is_listening = False
    is_orb_hovered = False

    status_text = ft.Text("Ready", size=14, color=TEXT_MUTED, weight=ft.FontWeight.W_500)
    voice_slot = ft.Container(alignment=ft.Alignment.CENTER)

    word_field = ft.TextField(
        hint_text="Recognized word",
        border=ft.InputBorder.OUTLINE,
        border_radius=14,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=SURFACE_LIGHT,
        color=TEXT,
        cursor_color=ACCENT,
        hint_style=ft.TextStyle(color=TEXT_DIM),
        filled=True,
        text_align=ft.TextAlign.CENTER,
    )

    search_field = ft.TextField(
        hint_text="Search saved words",
        border=ft.InputBorder.OUTLINE,
        border_radius=14,
        border_color=BORDER,
        focused_border_color=ACCENT,
        bgcolor=SURFACE,
        color=TEXT,
        cursor_color=ACCENT,
        hint_style=ft.TextStyle(color=TEXT_DIM),
        filled=True,
    )

    result_word = ft.Text("No word selected", size=22, weight=ft.FontWeight.W_600, color=TEXT)
    result_language = ft.Text("Language: -", size=12, color=TEXT_MUTED)
    result_definition = ft.Text("Definition: -", size=14, color="#D8DEEA", selectable=True)
    result_example = ft.Text("Example: -", size=14, color=TEXT_MUTED, italic=True, selectable=True)

    entries_list = ft.Column(controls=[], spacing=12)
    saved_count_text = ft.Text("", size=12, color=TEXT_DIM)

    def set_status(message: str, color: str = TEXT_MUTED) -> None:
        status_text.value = message
        status_text.color = color
        page.update()

    def show_entry(entry, fill_word_field: bool = True) -> None:
        word = _entry_value(entry, "word", "Unknown word")
        result_word.value = word
        result_language.value = f"Language: {_entry_value(entry, 'language', '-') or '-'}"
        result_definition.value = f"Definition: {_entry_value(entry, 'definition', '-')}"
        result_example.value = f"Example: {_entry_value(entry, 'example', '-') or '-'}"

        if fill_word_field:
            word_field.value = word

    def render_voice_orb() -> None:
        voice_slot.content = build_voice_orb(
            is_listening=is_listening,
            on_tap=on_listen_tap,
            on_hover=on_orb_hover,
            is_hovered=is_orb_hovered,
        )

    def set_voice_state(value: bool) -> None:
        nonlocal is_listening
        is_listening = value
        render_voice_orb()
        page.update()

    def on_orb_hover(event: ft.ControlEvent) -> None:
        nonlocal is_orb_hovered
        is_orb_hovered = event.data == "true"
        render_voice_orb()
        page.update()

    def build_saved_entry(entry) -> ft.Control:
        word = _entry_value(entry, "word", "Unknown word")
        language = _entry_value(entry, "language", "Unknown")
        definition = _entry_value(entry, "definition", "No definition.")
        example = _entry_value(entry, "example")

        card = _card(
            ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(word, size=16, weight=ft.FontWeight.W_600, color=TEXT),
                            _language_badge(language),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        definition,
                        size=13,
                        color=TEXT_MUTED,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                    ft.Text(
                        f"Example: {example or '-'}",
                        size=12,
                        color="#B6BED0",
                        italic=True,
                        max_lines=2,
                        overflow=ft.TextOverflow.ELLIPSIS,
                    ),
                ],
                spacing=8,
            ),
            padding=14,
            bgcolor=SURFACE_LIGHT,
        )

        return ft.GestureDetector(
            content=card,
            on_tap=lambda event, selected=entry: on_saved_entry_tap(selected),
            mouse_cursor=ft.MouseCursor.CLICK,
        )

    def refresh_entries(load_from_storage: bool = True) -> None:
        nonlocal all_entries

        if load_from_storage:
            try:
                all_entries = get_vocabulary_entries()
            except Exception as exc:
                entries_list.controls = [
                    ft.Text(f"Could not load saved words: {exc}", color=ERROR)
                ]
                saved_count_text.value = ""
                return

        query = (search_field.value or "").strip()
        filtered_entries = [entry for entry in all_entries if _entry_matches(entry, query)]

        entries_list.controls.clear()
        saved_count_text.value = f"{len(filtered_entries)} shown / {len(all_entries)} saved"

        if not filtered_entries:
            entries_list.controls.append(
                ft.Text("No matching saved words.", color=TEXT_MUTED, text_align=ft.TextAlign.CENTER)
            )
            return

        for entry in list(reversed(filtered_entries))[:10]:
            entries_list.controls.append(build_saved_entry(entry))

    def on_search_change(event: ft.ControlEvent) -> None:
        refresh_entries(load_from_storage=False)
        page.update()

    def on_saved_entry_tap(entry) -> None:
        show_entry(entry, fill_word_field=True)
        set_status("Saved word selected", ACCENT)
        page.update()

    def on_listen_tap(event) -> None:
        set_voice_state(True)
        set_status("Listening...", ACCENT)

        try:
            word = listen_and_transcribe()
        except Exception as exc:
            set_voice_state(False)
            set_status(f"Error: {exc}", ERROR)
            return

        word_field.value = word
        set_voice_state(False)
        set_status("Word recognized", SUCCESS)
        page.update()

    def on_define_click(event: ft.ControlEvent) -> None:
        word = (word_field.value or "").strip()

        if not word:
            set_status("Enter or speak a word first", ERROR)
            return

        set_status("Generating definition...", ACCENT)

        try:
            entry = define_and_save_word(word)
        except Exception as exc:
            set_status(f"Error: {exc}", ERROR)
            return

        show_entry(entry, fill_word_field=False)
        refresh_entries(load_from_storage=True)
        set_status("Saved", SUCCESS)
        page.update()

    search_field.on_change = on_search_change
    render_voice_orb()
    refresh_entries(load_from_storage=True)

    define_button = ft.Container(
        content=ft.Text("Define & save", color=TEXT, weight=ft.FontWeight.W_600),
        bgcolor="#27305F",
        border=ft.Border.all(1, "#39447D"),
        border_radius=14,
        height=46,
        alignment=ft.Alignment.CENTER,
        ink=True,
        ink_color="#22FFFFFF",
        on_click=on_define_click,
    )

    hero = ft.Column(
        controls=[
            ft.Text("Vocabulary Assistant", size=20, color=TEXT, weight=ft.FontWeight.W_600),
            ft.Text(
                "Speak a word. Edit it. Save its meaning.",
                size=13,
                color=TEXT_MUTED,
                text_align=ft.TextAlign.CENTER,
            ),
            ft.Container(height=14),
            voice_slot,
            status_text,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        spacing=10,
    )

    result_card = _card(
        ft.Column(
            controls=[
                ft.Row(
                    controls=[result_word, result_language],
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.START,
                ),
                ft.Divider(height=18, color=BORDER),
                result_definition,
                result_example,
            ],
            spacing=8,
        )
    )

    saved_header = ft.Row(
        controls=[
            ft.Text("Saved words", size=16, color=TEXT, weight=ft.FontWeight.W_600),
            saved_count_text,
        ],
        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
        vertical_alignment=ft.CrossAxisAlignment.CENTER,
    )

    app_shell = ft.Container(
        width=780,
        content=ft.Column(
            controls=[
                hero,
                ft.Container(height=8),
                word_field,
                define_button,
                result_card,
                ft.Container(height=8),
                saved_header,
                search_field,
                entries_list,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.STRETCH,
            spacing=16,
        ),
    )

    page.add(app_shell)


if __name__ == "__main__":
    ft.app(target=main)
