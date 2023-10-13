# Originally based on https://realpython.com/pygame-a-primer/
# But it's ... rather different now...

from game import Game
from all_scenes import Title

if __name__ == "__main__":
    Game(Title()).run()
