# web.py — простой HTML без jinja2

import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from db import init_db, list_products

app = FastAPI()


@app.on_event("startup")
def on_startup():
    # создаём базу/таблицы, если их ещё нет
    init_db()


@app.get("/", response_class=HTMLResponse)
def shop_page():
    products = list_products()

    cards = []
    for p in products:
        if p["old_price"] is not None and p["old_price"] > p["price"]:
            price_html = f"""
                <span style="text-decoration: line-through; color: #888; margin-right: 5px;">
                    {p['old_price']:.2f} грн
                </span>
                <span style="color: red; font-weight: bold;">
                    {p['price']:.2f} грн
                </span>
            """
        else:
            price_html = f"<span>{p['price']:.2f} грн</span>"

        desc_html = (
            f"<div style='font-size:0.9rem;color:#555;margin-bottom:8px;'>{p['description']}</div>"
            if p["description"] else ""
        )

        card = f"""
        <div style="background:#fff;padding:10px;border-radius:8px;
                    box-shadow:0 2px 5px rgba(0,0,0,0.1); margin-bottom:10px;">
            <div style="font-weight:bold;margin-bottom:5px;">{p['title']}</div>
            {desc_html}
            <div>{price_html}</div>
        </div>
        """
        cards.append(card)

    cards_html = "\n".join(cards) if cards else "<p>Пока нет товаров.</p>"

    html = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8" />
        <title>Магазин по селу</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background: #f5f5f5;
            }}
            header {{
                background: #2e8b57;
                color: #fff;
                padding: 15px;
                text-align: center;
            }}
            .container {{
                padding: 15px;
                max-width: 900px;
                margin: 0 auto;
            }}
        </style>
    </head>
    <body>
        <header>
            <h1>Магазин по селу</h1>
            <p>Оформление заказов — через Telegram бота</p>
        </header>
        <div class="container">
            {cards_html}
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/api/products")
def api_products():
    products = list_products()
    return JSONResponse(products)


if __name__ == "__main__":
    uvicorn.run("web:app", host="127.0.0.1", port=8000, reload=True)
