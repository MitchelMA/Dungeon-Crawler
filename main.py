import keyboard, time, os, yaml
from yaml.loader import FullLoader

class GameInstance():
    def __init__(self):
        self.encoding = 'utf-8'
        self.new_in_scene = True
        self.kill = False
        self.char_list = {
            "¶": 'player',
            '@': 'monster',
            "·": 'field',
            "│": 'wall',
            "─": 'wall',
            "┐": 'corner',
            "┘": 'corner',
            "└": 'corner',
            "┌": 'corner',
            '¤': 'chest',
            '§': 'door',
        }
        self.scenes = {
            "test": {
                "file":"./testfield.txt",
                "spawn": 10,
                "width": 8,
                "triggers": {
                    "doors": ['30 29 fieldtwo']
                },
                "monsters": ['28 easy', '13 easy']
            },
            "fieldtwo": {
                "file": "./secondfield.txt",
                "spawn": 35,
                "width": 28,
                "triggers": {
                    "doors": ['28 29 test']
                }
            }
        }
        self.display_scene = 'test'
        self.shown_scene = ''
        outerYaml = open('data.yaml', 'r', encoding=self.encoding)
        self.extra_data = yaml.load(outerYaml, Loader=FullLoader)
        self.player_lvl = 1
        self.player_xp = 0
        self.player_total_hp = self.extra_data['player']['total-hitpoints'] + (self.player_lvl - 1) * self.extra_data['player']['level-up-info']['hitpoints-up']
        if "__scene_init__":
            self.scene_init()


    def scene_init(self):
        os.system('cls')
        print(self.display_scene, self.extra_data, self.player_total_hp)
        if self.new_in_scene:
            readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
            self.shown_scene = list(readScene.read())
            readScene.close()

            self.shown_scene[self.scenes[self.display_scene]['spawn']] = '¶'
            self.shown_scene = ''.join(self.shown_scene)

            self.new_in_scene = False
        # monster spawning
        if 'monsters' in self.scenes[self.display_scene]:
            monster_list = self.scenes[self.display_scene]['monsters']
            self.shown_scene = list(self.shown_scene)
            for monster in monster_list:
                self.shown_scene[int(monster.split(' ')[0])] = '@'
            self.shown_scene = ''.join(self.shown_scene)
        print(self.shown_scene)


    def movement(self, i):
        def move(am):
            norm_scene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
            norm_scene = ''.join(list(norm_scene.read()))
            player_index = self.shown_scene.index('¶')
            next_player_index = player_index + am
            player_ground = self.char_list.get(norm_scene[player_index])
            next_player_ground = self.char_list.get(self.shown_scene[next_player_index])

            # check if move is legal
            if next_player_ground == 'field':
                self.shown_scene = list(self.shown_scene)
                self.shown_scene[player_index] = norm_scene[player_index]
                self.shown_scene[next_player_index] = '¶'
                self.shown_scene = ''.join(self.shown_scene)
                self.scene_init()
            
            # check if next tile is a door
            if next_player_ground == 'door':
                print(next_player_index)
                corresponding = None
                for i in self.scenes[self.display_scene]['triggers']['doors']:
                    if int(i.split(' ')[0]) == next_player_index:
                        corresponding = i
                        break
                if corresponding != None:
                    self.through_door(corresponding.split(' '))              
            if next_player_ground == 'monster':
                print(f'MONSTER! op {next_player_index}')
            # print(player_index, self.shown_scene[player_index], dir(norm_scene), norm_scene[player_index])
        if i.name == 'esc':
            self.kill = True
        if i.name == 'right':
            move(1)
        if i.name == 'left':
            move(-1)
        if i.name == 'down':
            move(self.scenes[self.display_scene]['width'])
        if i.name == 'up':
            move(-1 * self.scenes[self.display_scene]['width'])

    def through_door(self, door):
        self.display_scene = door[2]
        readScene = open(self.scenes[self.display_scene]['file'], 'r', encoding=self.encoding)
        readScene = list(readScene.read())
        readScene[int(door[1])] = '¶'
        readScene = ''.join(readScene)
        self.shown_scene = readScene
        self.scene_init()


game = GameInstance()
# game.startup()



while game.kill == False:
    # to read keyboard input
    keyboard.on_press(game.movement, suppress=True)
    time.sleep(1/120)