from bs4 import BeautifulSoup

with open("mudgrappler.html") as f:
    soup = BeautifulSoup(f, "html.parser")