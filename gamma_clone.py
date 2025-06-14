import os
import argparse
try:
    import openai
except ImportError as exc:
    raise SystemExit(
        "The 'openai' package is required. Install it with 'pip install -r requirements.txt'."
    ) from exc

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang='en'>
<head>
    <meta charset='UTF-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1.0'>
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        section {{ margin-bottom: 40px; }}
        h2 {{ background: #333; color: #fff; padding: 10px; }}
    </style>
</head>
<body>
{body}
</body>
</html>"""


def generate_slides(topic: str, slide_count: int = 5) -> str:
    """Generate slide content using the OpenAI API."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY environment variable is not set")
    openai.api_key = api_key
    prompt = f"Create a {slide_count}-slide presentation about '{topic}'. Provide output as JSON with 'slides' as a list of objects containing 'title' and 'bullet_points'."
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
    )
    return res.choices[0].message.content.strip()


def json_to_html(title: str, slides_json: str) -> str:
    import json
    data = json.loads(slides_json)
    sections = []
    for slide in data.get("slides", []):
        bullets = "\n".join(f"<li>{point}</li>" for point in slide.get("bullet_points", []))
        sections.append(f"<section><h2>{slide.get('title')}</h2><ul>{bullets}</ul></section>")
    body = "\n".join(sections)
    return HTML_TEMPLATE.format(title=title, body=body)


def main():
    parser = argparse.ArgumentParser(description="Generate a simple presentation using OpenAI")
    parser.add_argument("topic", help="Topic to generate slides for")
    parser.add_argument("--slides", type=int, default=5, help="Number of slides")
    parser.add_argument("--output", default="presentation.html", help="Output HTML file")
    args = parser.parse_args()

    slides_json = generate_slides(args.topic, args.slides)
    html = json_to_html(args.topic, slides_json)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Presentation saved to {args.output}")


if __name__ == "__main__":
    main()
