from fog.tokenizers import FingerprintTokenizer

data = [
    '""',
    "COTE D'IVOIRE ",
    'Abidjan ',
    'au Nord-Pas-de-Calais',
    'Ile-de-France ',
    '"Guyancourt, Frankreich"',
    '"Nanterre, France"',
    'Minsk',
    'Paris ',
    'Bitche',
    '"Aix-en-Provence, France"',
    'seine et Marne',
    ' martinique',
    '"Burgund, Frankreich"',
    'Bretagne/Brittanny/Breizh',
    '"Paris, France"',
    "Val-d'Oise",
]

# create tokenizer
stopwords = ["le", "la", "de"]
split_characters = ["-", "/", "|"]
tokenizer = FingerprintTokenizer(stopwords=stopwords, split=split_characters)

# for each tuple in data, normalize string at index using the tokenizer
normalized = [' '.join(tokenizer(d)) for d in data]

terms = [
    "Loire & Auvergne-Rhône-Alpes",
    "Auvergne-Rhône-Alpes"
]
print("\n" + "-" * 30)
for term in terms:
    print(f"\nterm: {term}")
    print(f"normalized term: {' '.join(tokenizer(term))}")

terms = [
    "Val de Loire",
    "Centre — Val de Loire",
]
print("\n" + "-" * 30)
for term in terms:
    print(f"\nterm: {term}")
    print(f"normalized term: {' '.join(tokenizer(term))}")


terms = [
    "Loigny-la-Bataille, Centre-Val de Loire, France",
    "Centre — Val de Loire",
]
print("\n" + "-" * 30)
for term in terms:
    print(f"\nterm: {term}")
    print(f"normalized term: {' '.join(tokenizer(term))}")



terms = [
    "Val-d`Oise",
    "Val-d'Oise",
]
print("\n" + "-" * 30)
for term in terms:
    print(f"\nterm: {term}")
    print(f"normalized term: {' '.join(tokenizer(term))}")


