import requests

test_dois = [
    "10.1103/PhysRevLett.112.098302",
    "10.1103/PhysRevLett.75.2148"
]

for doi in test_dois:
    print('meta name="citation' in str(requests.get("https://doi.org/"+doi).content))
