import random

# Word banks for constructing song names
adjectives = [
    "Cozy", "Gentle", "Warm", "Dreamy", "Soft", "Quiet", "Easy", "Calm", "Sunny", "Mellow",
    "Soothing", "Breezy", "Lazy", "Peaceful", "Golden", "Tranquil", "Chill", "Fading",
    "Hazy", "Serene", "Blissful", "Uplifting", "Hopeful", "Bright", "Velvet", "Drowsy",
    "Faint", "Shimmering", "Luminous", "Wistful", "Playful", "Cheerful", "Pastel", "Frosted",
    "Evening", "Morning", "Midnight", "Twilight", "Crimson", "Azure", "Ivory", "Amber"
]

time_words = [
    "Morning", "Noon", "Midnight", "Twilight", "Sunrise", "Sunset", "Dawn", "Dusk",
    "Nightfall", "Daybreak", "Golden Hour", "Evening", "Late Night", "Afternoon", "First Light"
]

nature_words = [
    "Breeze", "Rain", "Sunlight", "Sky", "Clouds", "Mist", "Waves", "Forest", "Leaves",
    "River", "Mountains", "Shore", "Sea", "Valley", "Horizon", "Moonlight", "Starlight",
    "Fog", "Petals", "Snow", "Wind", "Meadow", "Garden", "Ocean", "Stream", "Fields", "Branches"
]

cozy_nouns = [
    "Cafe", "Dream", "Glow", "Haze", "Drift", "Flow", "Rhythm", "Melody", "Harmony", "Serenade",
    "Echo", "Whisper", "Loop", "Groove", "Stroll", "Lounge", "Room", "Corner", "Window", "Light",
    "Steps", "Shadows", "Reflections", "Chapters", "Pages", "Stories", "Letters", "Moments", "Frames"
]

# Function to generate a title
def generate_title():
    pattern = random.choice([
        "{adj} {noun}",
        "{noun} of {nature}",
        "{time} {noun}",
        "{adj} {nature}",
        "{nature} and {noun}",
        "{adj} {time}",
        "{time} in {place}"
    ])
    place = random.choice(["the City", "the Garden", "the Cafe", "the Valley", "the Forest", "the Rain"])
    return pattern.format(
        adj=random.choice(adjectives),
        time=random.choice(time_words),
        nature=random.choice(nature_words),
        noun=random.choice(cozy_nouns),
        place=place
    )

# Generate 1000 unique titles
titles = set()
while len(titles) < 1000:
    titles.add(generate_title())

titles_list = list(titles)
print(titles_list[0:100])