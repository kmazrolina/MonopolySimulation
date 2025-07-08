import streamlit as st
from gui.statistics import get_owned_properties

def generate_css_and_wrapper(inner_html, center_content=""):
    """
    Shared helper to generate the full HTML structure with given inner fields and optional center content.
    """
    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: #121212;
                color: #eee;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .board {{
                position: relative;
                width: 400px;
                height: 400px;
                border-radius: 50%;
                display: flex;
                justify-content: center;
                align-items: center;
                background: rgba(0,0,0,0);
                box-shadow: 0 0 20px rgba(0,0,0,0.8);
                overflow: visible;
            }}
            .fields {{
                position: absolute;
                width: 100%;
                height: 100%;
                display: grid;
                place-items: center;
            }}
            .field {{
                position: absolute;
                width: 70px;
                height: 70px;
                background: #2a2a2a;
                border: 2px solid #555;
                border-radius: 12px;
                text-align: center;
                font-size: 12px;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                color: #ddd;
                box-shadow: 0 0 5px rgba(255, 255, 255, 0.1);
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }}
            .bought{{
                background: rgb(175,100,88);
            }}
            .field:hover {{
                transform: scale(1.1);
                border-color: #fff;
                box-shadow: 0 0 10px rgba(255,255,255,0.3);
            }}
            .icon {{
                font-size: 22px;
            }}
            .player {{
                position: absolute;
                center: 0;
                font-size: 30px;
                z-index: 100;
            }}
            .label {{
                margin-top: 5px;
                font-size: 11px;
                line-height: 1;
                color: #aaa;
                height: 0;
                opacity: 0;
                visibility: hidden;
                transition: opacity 0.3s ease;
            }}
            .field:hover .label {{
                opacity: 1;
                visibility: visible;
                height: auto;
            }}
            .center {{
                position: absolute;
                width: 300px;
                height: 300px;
                background: #1a1a1a;
                border-radius: 50%;
                border: 3px dashed #666;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
                text-align: center;
                font-weight: bold;
                color: #eee;
                box-shadow: 0 0 10px rgba(255,255,255,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="board">
            <div class="fields">
                {inner_html}
            </div>
            {f'<div class="center">{center_content}</div>' if center_content else ''}
        </div>
    </body>
    </html>
    """


def get_field_display(field, position=None, player_position=None):
    """
    Returns HTML for a single field. Adds player icon if positions are provided and match.
    """
    icons = {
        "Start": ("🏁", "Start"),
        "Tax": ("$", "Tax"),
        "Chance": ("☆", "Chance"),
        "Property": ("⌂", field.name if hasattr(field, 'name') else "Property")
    }
    icon, label = icons.get(field.field_type, ("?", "Unknown"))
    
    player = "🐱" if position is not None and player_position is not None and position == player_position else ""
    
    return f"""
        {'<div class="player">' + player + '</div>' if player else ''}
        <div class='icon'>{icon}</div>
        <div class='label'>{label}</div>
    """


def render_html_board(board):
    """
    Render only the board without player or event.
    """
    fields = board.fields
    board_size = len(fields)

    fields_html = ''.join([
        f"<div class='field' style='transform: rotate({360 * i / board_size}deg) translate(0, -220px) rotate(-{360 * i / board_size}deg);'>{get_field_display(field)}</div>"
        for i, field in enumerate(fields)
    ])

    return generate_css_and_wrapper(fields_html)


def render_html_board_with_game(board, simulation_title, game_no, turn_outcome):
    """
    Render board with player position and event description.
    """
    fields = board.fields
    board_size = len(fields)
    player_position = turn_outcome.get('player_position', 0)

    def is_bought(field):
        if field.field_type != "Property":
            return False
        
        owned_properties = get_owned_properties(simulation_title=simulation_title, game_no=game_no)
        return field.name in owned_properties
    
    fields_html = ''.join([
        f"<div class='field' \
            style='transform: rotate({360 * i / board_size}deg) \
                translate(0, -220px) \
                rotate(-{360 * i / board_size}deg);'>\
            <div class='field  {'bought' if is_bought(field) else ''}'> \
                {get_field_display(field, i, player_position)}\
            </div>\
        </div>"
        for i, field in enumerate(fields)
    ])

    event_description = f"{turn_outcome.get('event', '')}:&#10;&#13;{turn_outcome.get('description', '')}"

    return generate_css_and_wrapper(fields_html, event_description)