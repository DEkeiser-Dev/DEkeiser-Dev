import json
import os
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ["GITHUB_TOKEN"]
USERNAME = os.environ["GITHUB_USERNAME"]

STATS_DIR = "stats"

os.makedirs(STATS_DIR, exist_ok=True)

BG = "#17121F"
CARD = "#211A2E"
BORDER = "#4C1D95"
PURPLE = "#A78BFA"
LIGHT = "#D8B4FE"
TEXT = "#F5F3FF"
MUTED = "#A78BAF"


def github(query):
    body = json.dumps({"query": query}).encode()

    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Content-Type": "application/json",
            "User-Agent": "Dekeiser-GitHub-Stats"
        }
    )

    with urllib.request.urlopen(request) as response:
        result = json.loads(response.read())

    if "errors" in result:
        raise RuntimeError(result["errors"])

    return result["data"]


year = datetime.now(timezone.utc).year

query = f"""
query {{
  user(login: "{USERNAME}") {{

    repositories(
      first: 1
      ownerAffiliations: OWNER
      privacy: PUBLIC
    ) {{
      totalCount
    }}

    contributionsCollection(
      from: "{year}-01-01T00:00:00Z"
      to: "{year}-12-31T23:59:59Z"
    ) {{
      totalCommitContributions
      totalIssueContributions
      totalPullRequestContributions
      totalRepositoryContributions
      contributionCalendar {{
        totalContributions
        weeks {{
          contributionDays {{
            date
            contributionCount
          }}
        }}
      }}
    }}
  }}
}}
"""

data = github(query)["user"]

repositories = data["repositories"]["totalCount"]

collection = data["contributionsCollection"]

contributions = collection["contributionCalendar"]["totalContributions"]

days = []

for week in collection["contributionCalendar"]["weeks"]:
    days.extend(week["contributionDays"])


def svg_card(title, icon, value, subtitle):
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
width="360" height="150" viewBox="0 0 360 150">

<rect
x="2"
y="2"
width="356"
height="146"
rx="18"
fill="{CARD}"
stroke="{BORDER}"
stroke-width="2"/>

<text
x="28"
y="40"
font-family="Arial, sans-serif"
font-size="25"
fill="{LIGHT}">
{icon}
</text>

<text
x="65"
y="40"
font-family="Arial, sans-serif"
font-size="16"
font-weight="bold"
fill="{TEXT}">
{title}
</text>

<text
x="28"
y="92"
font-family="Arial, sans-serif"
font-size="38"
font-weight="bold"
fill="{PURPLE}">
{value}
</text>

<text
x="28"
y="122"
font-family="Arial, sans-serif"
font-size="13"
fill="{MUTED}">
{subtitle}
</text>

</svg>
"""


# 1. REPOSITORIOS

with open(
    f"{STATS_DIR}/repositories.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(
        svg_card(
            "Repositorios",
            "📦",
            repositories,
            "repositorios públicos"
        )
    )


# 2. CONTRIBUCIONES EN EL AÑO

with open(
    f"{STATS_DIR}/contributions.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(
        svg_card(
            "Contribuciones",
            "📈",
            contributions,
            f"en {year}"
        )
    )


# 3. ACTIVIDAD DE CONTRIBUCIÓN

width = 360
height = 150

svg = f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}" height="{height}" viewBox="0 0 {width} {height}">

<rect
x="2"
y="2"
width="356"
height="146"
rx="18"
fill="{CARD}"
stroke="{BORDER}"
stroke-width="2"/>

<text
x="28"
y="40"
font-family="Arial, sans-serif"
font-size="16"
font-weight="bold"
fill="{TEXT}">
🔥 Actividad de contribución
</text>
"""

# Últimos 91 días
recent = days[-91:]

cell = 10
gap = 3

for i, day in enumerate(recent):

    column = i % 13
    row = i // 13

    x = 28 + column * (cell + gap)
    y = 52 + row * (cell + gap)

    count = day["contributionCount"]

    if count == 0:
        color = "#2A2236"
    elif count <= 2:
        color = "#4C1D95"
    elif count <= 5:
        color = "#7C3AED"
    elif count <= 10:
        color = "#A78BFA"
    else:
        color = "#DDD6FE"

    svg += f"""
<rect
x="{x}"
y="{y}"
width="{cell}"
height="{cell}"
rx="3"
fill="{color}"/>
"""

svg += f"""
<text
x="28"
y="137"
font-family="Arial, sans-serif"
font-size="11"
fill="{MUTED}">
Últimos 3 meses
</text>

</svg>
"""

with open(
    f"{STATS_DIR}/activity.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write(svg)
